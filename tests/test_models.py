import unittest

from proxy_db.models import Proxy, PROTOCOLS

from ._compat import patch


class TestProxy(unittest.TestCase):
    proxy_id = '1.1.1.1:8888'

    def test_get(self):
        self.assertEqual(Proxy(id=self.proxy_id).get('http'), self.proxy_id)

    def test_get_default(self):
        self.assertEqual(Proxy(id=self.proxy_id).get('spam', 'foo'), 'foo')

    @patch('proxy_db.models.create_session')
    def test_vote(self, m):
        Proxy(id=self.proxy_id).positive()
        Proxy(id=self.proxy_id).negative()

    def test_in(self):
        proxy = Proxy(id=self.proxy_id)
        for protocol in PROTOCOLS:
            self.assertTrue(protocol in proxy)

    def test_copy(self):
        self.assertEqual(Proxy(id=self.proxy_id).copy(), {key: self.proxy_id for key in PROTOCOLS})

    def test_str(self):
        self.assertEqual(str(Proxy(id=self.proxy_id)), self.proxy_id)
