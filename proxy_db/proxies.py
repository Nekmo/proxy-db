import six
from sqlalchemy import exists

from proxy_db.exceptions import NoProvidersAvailable
from proxy_db.models import Proxy, ProviderRequest, create_session
from proxy_db.providers import PROVIDERS, ManualProxy


class NONE:
    pass


class ProxiesList(object):
    def __init__(self, country=None, provider=None):
        if isinstance(country, six.string_types):
            country = country.upper()
        self.request_options = dict(
            country=country,
        )
        self._proxies = set()
        provider_name = provider
        if provider is not None and isinstance(provider, str):
            provider = next(iter(filter(lambda x: x.name == provider, PROVIDERS)), NONE)
        if provider is NONE:
            manual_provider_exists = create_session().query(
                exists().where(ProviderRequest.provider == provider_name)
            ).scalar()
            assert manual_provider_exists is True, "Invalid provider name."
            provider = ManualProxy(provider_name)
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
            query = query.filter(Proxy.country == country)
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

    def reload_provider_without_error(self):
        try:
            self.reload_provider()
        except NoProvidersAvailable:
            pass

    def __iter__(self):
        self._proxies = set()
        return self

    def try_get_proxy(self, retry=True):
        proxy = self.find_db_proxy()
        if proxy:
            self._proxies.add(proxy)
            return proxy
        elif retry:
            self.reload_provider_without_error()
        if retry:
            return self.try_get_proxy(retry=False)
        else:
            raise StopIteration

    def __next__(self):
        return self.try_get_proxy()

    def next(self):
        return self.__next__()
