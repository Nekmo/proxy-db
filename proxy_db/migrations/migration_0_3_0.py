from proxy_db.migrations.migration_base import MigrateBase
from proxy_db.models import ProviderRequest, Proxy, association_table


class Migrate(MigrateBase):
    version = '0.3.0'
    tables = [
        {
            'model': ProviderRequest,
            'fields': ['id', 'provider', 'request_id', 'created_at', 'updated_at', 'results'],
        },
        {
            'model': Proxy,
            'fields': ['id', 'votes', 'country', 'created_at', 'updated_at', 'on_provider_at'],
        },
    ]

    def migrate_data(self):
        super(Migrate, self).migrate_data()
        new_database_session = self.create_new_database()
        for proxy in new_database_session.query(Proxy).all():
            proxy.protocol = proxy.id.split(':')[0]
        new_database_session.commit()
