import unittest

from click.testing import CliRunner

from proxy_db.management import add_command, list_command
from tests._compat import patch


class TestAdd(unittest.TestCase):

    @patch('proxy_db.management.ManualProxy')
    def test_add_proxies(self, m):
        CliRunner().invoke(add_command, ['http://1.2.3.4:999'])
        m.assert_called_once_with('manual')
        m.return_value.add_proxies.assert_called_once_with([{'protocol': 'http', 'proxy': '1.2.3.4:999'}], 10)

    @patch('proxy_db.management.click.get_text_stream', return_value=[])
    def test_get_text_stream(self, m):
        CliRunner().invoke(add_command, [])
        m.assert_called_once()

    @patch('proxy_db.management.click.echo', return_value=[])
    def test_invalid_proxy(self, m):
        CliRunner().invoke(add_command, ['invalid-proxy'])
        self.assertTrue(m.call_args_list[0][1]['err'])  #  click.echo('...', err=True)


class TestList(unittest.TestCase):

    @patch('proxy_db.management.create_session')
    def test_invalid_proxy(self, m):
        CliRunner().invoke(list_command, [
            '--min-votes', '10', '--country', 'ES',
            '--protocol', 'https', '--provider', 'Nord VPN'
        ])
