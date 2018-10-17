#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `proxy-db` package."""
import unittest
from ._compat import Mock, patch

from proxy_db.providers import ProxyNovaCom, Provider

URL = 'https://domain.com/'
PROVIDER_HTML = """
Proxy: 12.131.91.51:8888
<b>Other: 8.10.81.82:7171.</b> 
"""
PROXY_NOVA_HTML = """
    <tr data-proxy-id="00000000">
        <td align="left" onclick="javascript:check_proxy(this)">
            <abbr title="static.190.95.300.123.gtdinternet.com"><script>document.write('12345678190.9'.substr(8) + '5.300.123');</script> </abbr>
        </td>
        <td align="left">
            <a href="/proxy-server-list/port-8080/" title="Port 8080 proxies">8080</a>
        </td>
    </tr>
    <tr data-proxy-id="00000000">
        <td align="left" onclick="javascript:check_proxy(this)">
            <abbr title="static.190.900.48.190.gtdinternet.com"><script>document.write('12345678190.9'.substr(8) + '00.48.190');</script> </abbr>
        </td>
        <td align="left">
            <a href="/proxy-server-list/port-7070/" title="Port 7070 proxies">7070</a>
        </td>
    </tr>
"""


class TestProvider(unittest.TestCase):
    url = URL
    proxies = [{'proxy': ('12.131.91.51', '8888')}, {'proxy': ('8.10.81.82', '7171')}]

    def test_request(self):
        country = 'es'
        provider_request = Provider(self.url).request(self.url, country)
        self.assertEqual(provider_request.url, self.url)
        self.assertEqual(provider_request.options, {'country': country})

    def test_find_page_proxies(self):
        request = Mock()
        request.text = PROVIDER_HTML
        proxies = Provider(self.url).find_page_proxies(request)
        self.assertEqual(proxies, self.proxies)

    @patch('proxy_db.providers.create_session')
    def test_process_proxies(self, mock_session):
        Provider(self.url).process_proxies(self.proxies[:1])
        mock_session.assert_called_once()
        mock_session.return_value.commit.assert_called_once()


class TestProxyNovaCom(unittest.TestCase):
    url = 'https://domain.com/'

    @patch("proxy_db.providers.Provider.request")
    def test_request(self, m):
        provider = ProxyNovaCom()
        provider.request(self.url)
        m.assert_called_with(self.url, None)

    @patch("proxy_db.providers.Provider.request")
    def test_request_country(self, m):
        provider = ProxyNovaCom()
        country = 'es'
        provider.request(self.url, country)
        m.assert_called_with(self.url + 'country-{}/'.format(country), country)

    def test_find_page_proxies(self):
        provider = ProxyNovaCom()
        request = Mock()
        request.text = PROXY_NOVA_HTML
        self.assertEqual(provider.find_page_proxies(request), [
            {'proxy': '190.95.300.123:8080'},
            {'proxy': '190.900.48.190:7070'},
        ])
