import six

from proxy_db.exceptions import NoProvidersAvailable
from proxy_db.models import Proxy, ProviderRequest, create_session
from proxy_db.providers import PROVIDERS


class ProxiesList(object):
    def __init__(self, country=None, provider=None):
        if isinstance(country, six.string_types):
            country = country.upper()
        self.request_options = dict(
            country=country,
        )
        self._proxies = set()
        if provider is not None and isinstance(provider, str):
            provider = next(iter(filter(lambda x: x.name == provider, PROVIDERS)), None)
            assert provider is not None, "Invalid provider name."
        self.provider = provider

    def available_providers(self):
        providers = PROVIDERS
        if self.provider:
            providers = [self.provider]
        return filter(lambda x: x.is_available(), providers)

    def _excluded_proxies(self):
        return [proxy.id for proxy in self._proxies]

    def find_db_proxy(self):
        query = create_session().query(Proxy).filter(Proxy.votes > 0)
        query = query.join(Proxy.provider_requests).filter(
            ~Proxy.id.in_(self._excluded_proxies()),
            ProviderRequest.provider.in_([x.name for x in self.available_providers()]),
            # Proxy.provider_requests.provider.in_(self.available_providers())
        ).order_by(Proxy.votes.desc())
        country = self.request_options['country']
        if country:
            query = query.filter_by(country=country)
        proxy = query.first()
        if proxy is not None:
            proxy._set_providers()
        return proxy

    def find_provider(self):
        for provider in self.available_providers():
            req = provider.request(**self.request_options)
            if req.requires_update():
                return provider
        raise NoProvidersAvailable

    def reload_provider(self):
        provider = self.find_provider()
        provider.request(**self.request_options).now()

    def __iter__(self):
        self._proxies = set()
        return self

    def try_get_proxy(self, retry=True):
        proxy = self.find_db_proxy()
        if proxy:
            self._proxies.add(proxy)
            return proxy
        else:
            self.reload_provider()
        if retry:
            return self.try_get_proxy(retry=False)
        else:
            raise StopIteration

    def __next__(self):
        return self.try_get_proxy()

    def next(self):
        return self.__next__()
