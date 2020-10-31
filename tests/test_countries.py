import unittest

from geoip2.errors import AddressNotFoundError

from proxy_db.countries import ip_country
from ._compat import patch


class TestIpCountry(unittest.TestCase):
    @patch('proxy_db.countries.geoip2_manager')
    def test_ip_country(self, m):
        ip_country('proxy')
        m.__getitem__.assert_called_once()

    @patch('proxy_db.countries.geoip2_manager.is_license_key_available', return_value=False)
    def test_without_license(self, m):
        self.assertEqual(ip_country('proxy'), '')
        m.__getitem__.assert_not_called()

    @patch('proxy_db.countries.geoip2_manager')
    def test_address_not_found(self, m):
        m.__getitem__.side_effect = AddressNotFoundError
        self.assertEqual(ip_country('proxy'), '')
