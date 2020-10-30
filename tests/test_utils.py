import unittest


from proxy_db.utils import get_domain


class TestGetDomain(unittest.TestCase):
    def test_get_domain(self):
        self.assertEqual(get_domain('https://user:pass@domain.com:8888/'), 'domain.com')
