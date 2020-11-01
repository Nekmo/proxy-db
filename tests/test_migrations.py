import unittest

from proxy_db.migrations import MigrateVersion
from ._compat import patch


class TestMigrateVersion(unittest.TestCase):
    def test_pending_versions(self):
        versions = MigrateVersion().pending_versions()
        self.assertEqual(versions, set())

    def test_is_last_version(self):
        self.assertTrue(MigrateVersion().is_last_version())

    @patch('proxy_db.migrations.migration_0_3_0.Migrate.migrate')
    def test_migrate_version(self, m):
        MigrateVersion().migrate_version('0.3.0')
        m.assert_called_once()
