import unittest


from proxy_db.countries import ip_country, geoip2_manager
from ._compat import patch


class TestIpCountry(unittest.TestCase):
    @patch('proxy_db.countries.geoip2_manager')
    def test_ip_country(self, m):
        ip_country('proxy')
        m.__getitem__.assert_called_once()

    def test_without_license(self):
        if geoip2_manager is None:
            self.skipTest("external module geoip-tools not available")
            return
        with patch('proxy_db.countries.geoip2_manager.is_license_key_available', return_value=False) as m:
            self.assertEqual(ip_country('proxy'), '')
            m.__getitem__.assert_not_called()

    @patch('proxy_db.countries.geoip2_manager')
    def test_address_not_found(self, m):
        try:
            from geoip2.errors import AddressNotFoundError
        except ImportError:
            self.skipTest("external module geoip2 not available")
            return
        m.__getitem__.side_effect = AddressNotFoundError
        self.assertEqual(ip_country('proxy'), '')
