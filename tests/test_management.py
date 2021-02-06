import unittest
from unittest.mock import patch

from click.testing import CliRunner

from proxy_db.management import add


class TestAdd(unittest.TestCase):

    @patch('proxy_db.management.ManualProxy')
    def test_add_proxies(self, m):
        CliRunner().invoke(add, ['http://1.2.3.4:999'])
        m.assert_called_once_with('manual')
        m.return_value.add_proxies.assert_called_once_with([{'protocol': 'http', 'proxy': '1.2.3.4:999'}], 10)
