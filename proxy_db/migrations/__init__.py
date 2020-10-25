from proxy_db.models import create_session, Version
from proxy_db.utils import import_string


class MigrateVersion(object):
    versions = [
        '0.3.0',
    ]

    def is_last_version(self):
        session = create_session()
        version = session.query(Version).order_by(Version.id.desc()).first()
        return version.version == self.versions[-1] if version else False

    def pending_versions(self):
        session = create_session()
        migrated_versions = session.query(Version).order_by(Version.id.asc()).all()
        migrated_versions = set([version.version for version in migrated_versions])
        return set(self.versions) - migrated_versions

    def migrate_pending_versions(self):
        for version in self.pending_versions():
            self.migrate_version(version)

    def migrate_version(self, version):
        version_alias = version.replace('.', '_')
        migrate_cls = import_string('proxy_db.migrations.migration_{}.Migrate'.format(version_alias))
        migrate_cls().migrate()
