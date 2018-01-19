"""Based on:
https://github.com/constverum/ProxyBroker/blob/master/proxybroker/providers.py


"""
import copy
import datetime
import re
import requests
from bs4 import BeautifulSoup

from proxy_db.db import get_or_create
from proxy_db.models import create_session, Proxy, ProviderRequest

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


class ProviderRequestBase(object):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0'}

    def __init__(self, provider, url, method='GET', data=None, headers=None, options=None):
        self.provider = provider
        self.url = url
        self.method = method
        self.headers = headers or copy.copy(self.headers)
        self.data = data
        self.options = options

    def now(self):
        self.provider.process_page(requests.request(self.method, self.url), self)
        session = create_session()
        self.get_or_create(session)
        session.commit()

    def requires_update(self):
        instance, exists = self.get_or_create()
        return not exists or \
               datetime.datetime.now() > \
               instance.updated_at + datetime.timedelta(minutes=PROVIDER_REQUIRES_UPDATE_MINUTES)

    def get_or_create(self, session=None):
        session = session or create_session()
        return get_or_create(session, ProviderRequest, defaults={'updated_at': datetime.datetime.now()},
                             id=self.id)

    @property
    def id(self):
        return '-'.join(['{}'.format(x[1]) for x in sorted(self.options.items())])


class Provider(object):
    base_url = None

    def __init__(self, base_url=None):
        self.base_url = base_url or self.base_url

    def request(self, url=None, country=None):
        return self.get_provider_request(url, country)

    def find_page_proxies(self, request):
        return [{'proxy': proxy} for proxy in IP_PORT_PATTERN_GLOBAL.findall(request.text)]

    def process_page(self, request, provider_request):
        self.process_proxies(self.find_page_proxies(request))

    def process_proxies(self, proxies):
        session = create_session()
        for proxy in proxies:
            instance, exists = get_or_create(session, Proxy, defaults=dict(votes=0),
                                             id='http://{}'.format(proxy['proxy']))
            instance.votes += 1
        session.commit()

    def get_provider_request(self, url, country):
        return ProviderRequestBase(self, url, options={'country': country})


class SoupProvider(Provider):
    parser = 'lxml' if lxml_available else 'html.parser'

    def find_page_proxies(self, request):
        soup = BeautifulSoup(request.text, self.parser)
        items = self.soup_items(soup)
        return [self.soup_item(item) for item in items]

    def soup_items(self, soup):
        raise NotImplementedError

    def soup_item(self, item):
        raise NotImplementedError


class ProxyNovaCom(SoupProvider):
    base_url = 'https://www.proxynova.com/proxy-server-list/'

    def request(self, url=None, country=None):
        url = self.base_url
        if country:
            url += 'country-{}/'.format(country.lower())
        return super(ProxyNovaCom, self).request(url, country)

    def soup_items(self, soup):
        return soup.select('tr[data-proxy-id]')

    def soup_item(self, item):
        # document.write('12345678190.7'.substr(8) + '7.81.128');
        script = item.find('script').string
        port = ''.join(item.find_all('td')[1].stripped_strings)
        subs = script.split("'")
        substr = int(re.match('.+substr\((\d+)\).+', script).group(1))
        start = subs[1][substr:]
        end = subs[-2]
        return {'proxy': '{}{}:{}'.format(start, end, port)}
