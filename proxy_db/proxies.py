import six
from sqlalchemy import exists, func

from proxy_db.exceptions import NoProvidersAvailable, UnsupportedEngine
from proxy_db.models import Proxy, ProviderRequest, create_session
from proxy_db.providers import PROVIDERS, ManualProxy


class NONE:
    pass


class ListingStrategy(object):
    def __init__(self, filters=None, order_by=None, no_repeat=True):
        self.filters = filters
        self.order_by = order_by
        self.no_repeat = no_repeat
        self._proxies = set()

    def get_default_filters(self):
        return []

    def get_order_by(self, query):
        if self.order_by is not None:
            return self.order_by
        else:
            return Proxy.created_at.desc()

    def get_filters(self, query):
        filters = list(self.filters or [])
        filters.extend(self.get_default_filters())
        if self.no_repeat:
            filters.append(~Proxy.id.in_(self._returned_proxies()))
        return filters

    def _returned_proxies(self):
        return [proxy.id for proxy in self._proxies]

    def get_query(self, query):
        return query.filter(*self.get_filters(query)).order_by(self.get_order_by(query))

    def next(self, query):
        query = self.get_query(query)
        proxy = query.first()
        if proxy is not None and self.no_repeat:
            self._proxies.add(proxy)
        if proxy is not None:
            proxy._set_providers()
        return proxy


class VotesListingStrategy(ListingStrategy):
    def __init__(self, filters=None, min_votes=0):
        super().__init__(filters, Proxy.votes.desc())
        self.min_votes = min_votes

    def get_default_filters(self):
        return [Proxy.votes >= self.min_votes]


class RandomListingStrategy(ListingStrategy):
    def __init__(self, filters=None):
        super().__init__(filters, None)

    def get_order_by(self, query):
        engine_name = query.session.get_bind().name
        if engine_name in ['sqlite', 'postgresql']:
            return func.random()
        elif engine_name == 'mysql':
            return func.rand()
        elif engine_name == 'oracle':
            return 'dbms_random.value'
        else:
            raise UnsupportedEngine(
                '{engine_name} engine does not support random ordering.'.format(**locals())
            )


class ProxiesList(object):
    def __init__(self, country=None, provider=None, protocol=None, strategy=None):
        if isinstance(country, six.string_types):
            country = country.upper()
        self.request_options = dict(
            country=country,
            protocol=protocol,
        )
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
        if strategy and isinstance(strategy, type):
            # Is a class without initialize. Instance now.
            strategy = strategy()
        self.strategy = strategy or VotesListingStrategy()

    def available_providers(self):
        providers = PROVIDERS
        if self.provider:
            providers = [self.provider]
        return filter(lambda x: x.is_available(), providers)

    def find_db_proxy(self):
        query = create_session().query(Proxy).join(Proxy.provider_requests).filter(
            ProviderRequest.provider.in_([x.name for x in self.available_providers()]),
        )
        country = self.request_options['country']
        protocol = self.request_options['protocol']
        if country:
            query = query.filter(Proxy.country == country)
        if protocol:
            query = query.filter(Proxy.protocol == protocol)
        return self.strategy.next(query)

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
