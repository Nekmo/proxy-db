import os
from sqlalchemy import create_engine, Integer, Column, String, Sequence, DateTime, func, Table, ForeignKey, \
    UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from proxy_db._compat import urlparse

PROXY_DB_FILE = os.environ.get('PROXY_DB_FILE', os.path.expanduser('~/.local/var/lib/proxy-db/db.sqlite3'))
PROXY_DB_DB_URL = os.environ.get('PROXY_DB_DB_URL', 'sqlite:///{}'.format(PROXY_DB_FILE))
PROTOCOLS = ['http', 'https']


Base = declarative_base()

association_table = Table('proxy_provider_request', Base.metadata,
                          Column('proxy_id', String(255), ForeignKey('proxies.id')),
                          Column('provider_request_id', Integer, ForeignKey('provider_requests.id'))
                          )


class ProviderRequest(Base):
    __tablename__ = 'provider_requests'
    __table_args__ = (UniqueConstraint('provider', 'request_id', name='_provider_request_uc'),
                     )

    id = Column(Integer, Sequence('provider_requests_id_seq'), primary_key=True)
    provider = Column(String(30))
    request_id = Column(String(255), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    results = Column(Integer)
    proxies = relationship("Proxy", secondary=association_table, backref="provider_requests")

    def get_provider_instance(self):
        from proxy_db.providers import PROVIDERS
        return next(filter(lambda x: x.name == self.provider, PROVIDERS))


class Proxy(Base):
    __tablename__ = 'proxies'
    _proxies_list = None

    id = Column(String(255), primary_key=True)
    votes = Column(Integer, default=0)
    country = Column(String(5), index=True)
    protocol = Column(String(32), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    on_provider_at = Column(DateTime(timezone=True))
    providers = {}
    credentials = ()

    def get_updated_proxy(self, session=None):
        """
        :param session:
        :return:
        :rtype: Proxy
        """
        session = session or create_session()
        return session.query(Proxy).filter_by(id=self.id).first()

    def vote(self, vote):
        session = create_session()
        instance = self.get_updated_proxy(session)
        instance.votes += vote
        session.commit()

    def positive(self):
        self.vote(1)

    def negative(self):
        self.vote(-1)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def set_proxies_list(self, proxies_list):
        self._proxies_list = proxies_list

    def __contains__(self, item):
        return item in PROTOCOLS

    def __getitem__(self, item):
        if item not in PROTOCOLS:
            raise KeyError
        return str(self)

    def copy(self):
        return {key: str(self) for key in PROTOCOLS}

    def _set_providers(self):
        provider_instances = map(lambda x: x.get_provider_instance(), self.provider_requests)
        credential_provider = next(filter(lambda x: x.has_credentials(), provider_instances), None)
        if credential_provider:
            self.credentials = credential_provider.credentials()
        self.providers = {proxy.provider for proxy in self.provider_requests}

    def __repr__(self):
        return "<Proxy {} ({})>".format(self, ','.join(self.providers))

    def proxy_with_credentials(self):
        if self.credentials:
            url_result = urlparse(self.id)
            return '{url_result.scheme}://{username}:{password}@{url_result.netloc}'.format(
                username=self.credentials[0], password=self.credentials[1],
                url_result=url_result
            )
        return self.id

    def __str__(self):
        return self.proxy_with_credentials()


class Version(Base):
    __tablename__ = 'versions'
    _proxies_list = None

    id = Column(Integer, Sequence('version_id_seq'), primary_key=True)
    version = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return "<Version {}>".format(self.version)

    def __str__(self):
        return self.version


proxy_db_dir = os.path.dirname(PROXY_DB_FILE)
if not os.path.lexists(proxy_db_dir):
    os.makedirs(proxy_db_dir)

db_created = not os.path.lexists(PROXY_DB_FILE)
engine = create_engine(PROXY_DB_DB_URL,
                       connect_args={'check_same_thread': False} if PROXY_DB_DB_URL.startswith('sqlite://') else {})
Base.metadata.create_all(engine)


def create_session_maker():
    return sessionmaker(bind=engine)


session_maker = create_session_maker()


def create_session():
    return session_maker()


from proxy_db.migrations import MigrateVersion


if db_created:
    MigrateVersion().create_all_versions()
else:
    MigrateVersion().migrate_pending_versions()
