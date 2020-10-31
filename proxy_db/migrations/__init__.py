from proxy_db.utils import import_string


class MigrateVersion(object):
    versions = [
        '0.3.0',
    ]

    def is_last_version(self):
        from proxy_db.models import create_session, Version
        session = create_session()
        version = session.query(Version).order_by(Version.id.desc()).first()
        return version.version == self.versions[-1] if version else False

    def pending_versions(self):
        from proxy_db.models import create_session, Version
        session = create_session()
        migrated_versions = session.query(Version).order_by(Version.id.asc()).all()
        migrated_versions = set([version.version for version in migrated_versions])
        return set(self.versions) - migrated_versions

    def migrate_pending_versions(self):
        for version in self.pending_versions():
            self.migrate_version(version)

    def create_all_versions(self):
        for version in self.versions:
            migration_cls = self.import_migration(version)
            migration_cls().create_version_row()

    def import_migration(self, version):
        version_alias = version.replace('.', '_')
        return import_string('proxy_db.migrations.migration_{}.Migrate'.format(version_alias))

    def migrate_version(self, version):
        migration_cls = self.import_migration(version)
        migration_cls().migrate()
