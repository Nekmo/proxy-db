

class ProxyDB(Exception):
    pass


class NoProvidersAvailable(ProxyDB):
    pass


class UnknownExportFormat(ProxyDB):
    pass


class UnsupportedEngine(ProxyDB):
    pass
