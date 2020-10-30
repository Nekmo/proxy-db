import unittest

from proxy_db.countries import ip_country
from ._compat import patch


class TestIpCountry(unittest.TestCase):
    @patch('proxy_db.countries.geoip2_manager')
    def test_ip_country(self, m):
        ip_country('proxy')
        m.__getitem__.assert_called_once()
