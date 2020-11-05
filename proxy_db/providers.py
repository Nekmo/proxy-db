"""Based on:
https://github.com/constverum/ProxyBroker/blob/master/proxybroker/providers.py


"""
from __future__ import absolute_import
import copy
import datetime
import os
import re
from logging import getLogger

import requests
from bs4 import BeautifulSoup

from proxy_db.countries import ip_country, COUNTRIES
from proxy_db.db import get_or_create
from proxy_db.models import create_session, Proxy, ProviderRequest
from proxy_db.utils import get_domain

try:
    import lxml
except ImportError:
    lxml_available = False
else:
    lxml_available = True

PROVIDER_REQUIRES_UPDATE_MINUTES = 45
SIMPLE_IP_PATTERN = re.compile('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
IP_PORT_PATTERN_GLOBAL = re.compile(
    r'(?P<ip>(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?))'  # noqa
    r'(?=.*?(?:(?:(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?))|(?P<port>\d{2,5})))',  # noqa
    flags=re.DOTALL)
UPDATE_VOTES = 3


class ProviderRequestBase(object):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0'}

    def __init__(self, provider, url, method='GET', data=None, headers=None, options=None):
        self.provider = provider
        self.url = url
        self.method = method
        self.headers = headers or copy.copy(self.headers)
        self.data = data
        self.options = options

    def make_request(self):
        return requests.request(self.method, self.url)

    def now(self):
        session = create_session()
        proxies = self.provider.process_page(self.make_request(), session)
        provider_request, _ = self.get_or_create(session, {'results': len(proxies)})
        for proxy in proxies:
            provider_request.proxies.append(proxy)
        session.commit()

    def requires_update(self):
        instance, exists = self.get_or_create()
        return not exists or \
               datetime.datetime.now() > \
               instance.updated_at + datetime.timedelta(minutes=PROVIDER_REQUIRES_UPDATE_MINUTES)

    def get_or_create(self, session=None, update_defaults=None):
        session = session or create_session()
        defaults = {
            'updated_at': datetime.datetime.now(),
            'results': 0,
        }
        defaults.update(update_defaults or {})
        return get_or_create(session, ProviderRequest, defaults=defaults,
                             request_id=self.id, provider=self.provider.name)

    @property
    def id(self):
        return '-'.join(['{}'.format(x[1]) for x in sorted(self.options.items())])


class ProviderCredentialMixin:
    env_key_username =  None
    env_key_password = None

    def is_available(self):
        return os.environ.get(self.env_key_username) and os.environ.get(self.env_key_password)

    def has_credentials(self):
        return self.is_available()

    def credentials(self):
        if not self.is_available():
            return ()
        return os.environ.get(self.env_key_username), os.environ.get(self.env_key_password)


class Provider(object):
    name = 'Provider'
    base_url = None

    def __init__(self, base_url=None):
        self.base_url = base_url or self.base_url
        self.logger = getLogger('proxy_db.providers.{}'.format(self.lowercase_name()))

    def is_available(self):
        return True

    def has_credentials(self):
        return False

    def credentials(self):
        return ()

    def request(self, url=None, country=None):
        url = url or self.base_url
        return self.get_provider_request(url, country)

    def find_page_proxies(self, request):
        return [{'proxy': proxy} for proxy in IP_PORT_PATTERN_GLOBAL.findall(request.text)]

    def process_page(self, request, session=None):
        return self.process_proxies(self.find_page_proxies(request), session)

    def process_proxies(self, proxies, session=None):
        session = session or create_session()
        proxy_instances = []
        for proxy in proxies:
            protocol = proxy.get('protocol', 'http')
            instance, exists = get_or_create(
                session, Proxy, defaults=dict(votes=0, protocol=protocol),
                id='{}://{}'.format(protocol, proxy['proxy'])
            )
            if not instance.country:
                detected_country = ip_country(get_domain(instance.id))
                instance.country = detected_country or proxy.get('country_code') or ''
            instance.votes += UPDATE_VOTES
            proxy_instances.append(instance)
        session.commit()
        return proxy_instances

    def get_provider_request(self, url, country):
        return ProviderRequestBase(self, url, options={'country': country})

    def lowercase_name(self):
        return self.name.lower().replace(' ', '_')


class SoupProvider(Provider):
    parser = 'lxml' if lxml_available else 'html.parser'

    def find_page_proxies(self, request):
        soup = BeautifulSoup(request.text, self.parser)
        items = self.soup_items(soup)
        return list(filter(bool, map(lambda item: self.soup_item(item), items)))

    def soup_items(self, soup):
        raise NotImplementedError

    def soup_item(self, item):
        raise NotImplementedError


class ProxyNovaCom(SoupProvider):
    name = 'Proxy Nova'
    base_url = 'https://www.proxynova.com/proxy-server-list/'

    def request(self, url=None, country=None):
        url = url or self.base_url
        if country:
            url += 'country-{}/'.format(country.lower())
        return super(ProxyNovaCom, self).request(url, country)

    def soup_items(self, soup):
        return soup.select('tr[data-proxy-id]')

    def soup_item(self, item):
        script = item.find('script')
        if script is None:
            self.logger.warning('Script tag is no available in item {}'.format(item))
            return None
        script = script.string or ''
        td_tags = item.find_all('td')
        if len(td_tags) < 2:
            self.logger.warning('td tag including port is not available in item {}'.format(item))
            return None
        port = ''.join(td_tags[1].stripped_strings or '')
        matchs = SIMPLE_IP_PATTERN.search(script)
        if matchs is None:
            self.logger.warning('Invalid script value for item {}'.format(item))
            return None
        img = item.find('img', class_='flag')
        country = None
        if img is None or 'alt' not in img.attrs:
            self.logger.warning('Image with country is not available in item {}'.format(item))
        else:
            country = img.attrs['alt'].upper()
        if country and country not in COUNTRIES:
            self.logger.warning('Invalid country code in item {}: {}'.format(item, country))
            country = None
        ip_address = matchs.group(1)
        return {'proxy': '{}:{}'.format(ip_address, port), 'country_code': country}


# class NordVpnProviderRequest(ProviderRequestBase):
#     def make_request(self):
#         return requests.request(self.method, self.url, )


class NordVpn(ProviderCredentialMixin, Provider):
    name = 'Nord VPN'
    base_url = 'https://api.nordvpn.com/server'
    protocols = [
        {'feature': 'socks', 'protocol': 'socks5', 'port': 1080},
        {'feature': 'proxy', 'protocol': 'http', 'port': 80},
        {'feature': 'proxy_ssl', 'protocol': 'https', 'port': 89},
    ]
    env_key_username =  'PROXYDB_NORDVPN_USERNAME'
    env_key_password = 'PROXYDB_NORDVPN_PASSWORD'

    def request(self, url=None, country=None):
        url = url or self.base_url
        return super(NordVpn, self).request(url, country)

    def find_page_proxies(self, request):
        proxies = request.json()
        proxy_datas = []
        for proxy in proxies:
            country = proxy['flag']
            if country not in COUNTRIES:
                self.logger.warning('Invalid country in proxy {}: {}'.format(
                    proxy['ip_address'], country,
                ))
                country = None
            for protocol in self.protocols:
                if not proxy['features'].get(protocol['feature']):
                    continue
                address = proxy['domain'] if protocol['protocol'] == 'https' else proxy['ip_address']
                proxy_datas.append({
                    'proxy': '{address}:{port}'.format(
                        address=address, **protocol
                    ),
                    'country_code': country,
                    'protocol': protocol['protocol'],
                })
        return proxy_datas


PROVIDERS = [
    NordVpn(),
    ProxyNovaCom(),
]
