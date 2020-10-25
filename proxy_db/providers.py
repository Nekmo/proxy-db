"""Based on:
https://github.com/constverum/ProxyBroker/blob/master/proxybroker/providers.py


"""
from __future__ import absolute_import
import copy
import datetime
import re
from logging import getLogger

import requests
from bs4 import BeautifulSoup

from proxy_db.countries import ip_country
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


class Provider(object):
    name = 'Provider'
    base_url = None

    def __init__(self, base_url=None):
        self.base_url = base_url or self.base_url
        self.logger = getLogger('proxy_db.providers.{}'.format(self.lowercase_name()))

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
                instance.country = ip_country(get_domain(instance.id))
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
        # document.write('12345678190.7'.substr(8) + '7.81.128');
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
        subs = script.split("'")
        matchs = re.match('.+substr\((\d+)\).+', script)
        if matchs is None:
            self.logger.warning('Invalid script value for item {}'.format(item))
            return None
        substr = int(matchs.group(1))
        start = subs[1][substr:]
        end = subs[-2]
        return {'proxy': '{}{}:{}'.format(start, end, port)}


# class NordVpnProviderRequest(ProviderRequestBase):
#     def make_request(self):
#         return requests.request(self.method, self.url, )


class NordVpn(Provider):
    name = 'Nord VPN'
    base_url = 'https://api.nordvpn.com/server'
    protocols = [
        {'feature': 'socks', 'protocol': 'socks5', 'port': 1080},
        {'feature': 'proxy', 'protocol': 'http', 'port': 80},
        {'feature': 'proxy_ssl', 'protocol': 'https', 'port': 443},
    ]

    def request(self, url=None, country=None):
        url = url or self.base_url
        return super(NordVpn, self).request(url, country)

    def find_page_proxies(self, request):
        proxies = request.json()
        proxy_datas = []
        for proxy in proxies:
            for protocol in self.protocols:
                if not proxy['features'].get(protocol['feature']):
                    continue
                proxy_datas.append({
                    'proxy': '{ip_address}:{port}'.format(
                        ip_address=proxy['ip_address'], **protocol
                    ),
                    'protocol': protocol['protocol'],
                })
        return proxy_datas


PROVIDERS = [
    NordVpn(),
    ProxyNovaCom(),
]
