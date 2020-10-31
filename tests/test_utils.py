import unittest


from proxy_db.utils import get_domain, import_string


class TestGetDomain(unittest.TestCase):
    def test_get_domain(self):
        self.assertEqual(get_domain('https://user:pass@domain.com:8888/'), 'domain.com')


class TestImportString(unittest.TestCase):
    def test_import_class(self):
        self.assertEqual(import_string('proxy_db.utils.import_string'), import_string)

    def test_invalid_string(self):
        with self.assertRaises(ImportError):
            import_string('foobar')

    def test_invalid_attribute(self):
        with self.assertRaises(ImportError):
            import_string('proxy_db.utils.invalid')
