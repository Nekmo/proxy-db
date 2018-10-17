import unittest

from tests._compat import patch, call

import requests_mock

from proxy_db.utils import download_file, get_domain


class TestDownloadFile(unittest.TestCase):
    url = 'https://domain.com/'

    def setUp(self):
        super(TestDownloadFile, self).setUp()
        self.session_mock = requests_mock.Mocker()
        self.session_mock.start()

    def tearDown(self):
        super(TestDownloadFile, self).tearDown()
        self.session_mock.stop()

    @patch('proxy_db.utils.open')
    def test_request(self, m):
        text = 'foo' * 1000
        self.session_mock.get(self.url, text=text)
        download_file(self.url)
        self.assertEqual(self.session_mock.call_count, 1)
        calls = [call.write(text[i:i+1024].encode('utf-8')) for i in range(0, len(text), 1024)]
        self.assertEqual(m.return_value.__enter__.return_value.mock_calls, calls)


class TestGetDomain(unittest.TestCase):
    def test_get_domain(self):
        self.assertEqual(get_domain('https://user:pass@domain.com:8888/'), 'domain.com')
