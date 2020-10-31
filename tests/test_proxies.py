import unittest
from ._compat import patch, Mock

from proxy_db.proxies import ProxiesList


class TestProxiesList(unittest.TestCase):
    @patch('proxy_db.proxies.create_session')
    def test_find_db_proxy(self, m):
        ProxiesList().find_db_proxy()
        m.assert_called_once()

    @patch('proxy_db.proxies.ProxiesList.available_providers', return_value=[Mock()])
    def test_find_provider(self, m):
        provider = ProxiesList().find_provider()
        self.assertEqual(provider, m.return_value[0])

    @patch('proxy_db.proxies.ProxiesList.find_provider')
    def test_reload_provider(self, m):
        p = ProxiesList()
        p.reload_provider()
        m.return_value.request.assert_called_once_with(**p.request_options)
        m.return_value.request.return_value.now.assert_called_once()

    def test_iter(self):
        p = ProxiesList()
        p._proxies = None
        p2 = iter(p)
        self.assertEqual(p2._proxies, set())
