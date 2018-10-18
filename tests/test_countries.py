import unittest

from proxy_db.countries import ip_country, extract_file_to
from ._compat import patch, Mock


class TestIpCountry(unittest.TestCase):
    @patch('proxy_db.countries.init_reader')
    def test_ip_country(self, m):
        ip_country('proxy')
        m.assert_called_once()


class TestExtractFileTo(unittest.TestCase):
    @patch('proxy_db.countries.open')
    def test_extract_file_to(self, open_mock):
        member_path = 'file'
        to = 'extracted_file'
        mock = Mock()
        mock.extractfile.return_value.__enter__ = Mock(return_value=(Mock(), None))
        mock.extractfile.return_value.__exit__ = Mock(return_value=(Mock(), None))
        extract_file_to(mock, member_path, to)
