import os
from sqlalchemy import create_engine, Integer, Column, String, Sequence, DateTime, func, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

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

    id = Column(Integer, Sequence('provider_requests_id_seq'), primary_key=True)
    provider = Column(String(30))
    request_id = Column(String(255), index=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    results = Column(Integer)
    proxies = relationship("Proxy", secondary=association_table, backref="provider_requests")


class Proxy(Base):
    __tablename__ = 'proxies'
    _proxies_list = None

    id = Column(String(255), primary_key=True)
    votes = Column(Integer, default=0)
    country = Column(String(5))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    on_provider_at = Column(DateTime(timezone=True))

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
        return self.id

    def copy(self):
        return {key: self.id for key in PROTOCOLS}

    def __str__(self):
        return self.id


proxy_db_dir = os.path.dirname(PROXY_DB_FILE)
if not os.path.lexists(proxy_db_dir):
    os.makedirs(proxy_db_dir)

engine = create_engine(PROXY_DB_DB_URL,
                       connect_args={'check_same_thread': False} if PROXY_DB_DB_URL.startswith('sqlite://') else {})
Base.metadata.create_all(engine)


def create_session_maker():
    return sessionmaker(bind=engine)

session_maker = create_session_maker()


def create_session():
    return session_maker()
