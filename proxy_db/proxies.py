from proxy_db.exceptions import NoProvidersAvailable
from proxy_db.models import Proxy, create_session
from proxy_db.providers import PROVIDERS


class ProxiesList(object):
    def __init__(self, country=None):
        if isinstance(country, str):
            country = country.upper()
        self.request_options = dict(
            country=country,
        )
        self._proxies = set()

    def _excluded_proxies(self):
        return [proxy.id for proxy in self._proxies]

    def find_db_proxy(self):
        query = create_session().query(Proxy).filter(Proxy.votes > 0)
        query = query.filter(~Proxy.id.in_(self._excluded_proxies())).order_by(Proxy.votes.desc())
        country = self.request_options['country']
        if country:
            query = query.filter_by(country=country)
        return query.first()

    def find_provider(self):
        for provider in PROVIDERS:
            req = provider.request(**self.request_options)
            if req.requires_update():
                return provider
        raise NoProvidersAvailable

    def reload_provider(self):
        provider = self.find_provider()
        # TODO: controlar cuando no hay provider
        provider.request(**self.request_options).now()

    def __iter__(self):
        self._proxies = set()
        return self

    def __next__(self):
        proxy = self.find_db_proxy()
        if proxy:
            self._proxies.add(proxy)
            return proxy
        else:
            self.reload_provider()
        return next(self)
