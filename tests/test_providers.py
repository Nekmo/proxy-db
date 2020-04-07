#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `proxy-db` package."""
import datetime
import unittest

import requests_mock

from ._compat import Mock, patch

from proxy_db.providers import ProxyNovaCom, Provider, ProviderRequestBase, PROVIDER_REQUIRES_UPDATE_MINUTES

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
PROXY_NOVA_INVALID_ROWS_HTML = """
    <tr data-proxy-id="00000000">
        Script tag is not available
        <td align="left" onclick="javascript:check_proxy(this)"></td>
        <td align="left">
            <a href="/proxy-server-list/port-7070/" title="Port 7070 proxies">7070</a>
        </td>
    </tr>
    <tr data-proxy-id="00000000">
        Second td is not available
        <td align="left" onclick="javascript:check_proxy(this)">
            <abbr title=""><script>document.write('12345678190.9'.substr(8) + '5.300.123');<</script> </abbr>
        </td>
    </tr>
    <tr data-proxy-id="00000000">
        Invalid script value
        <td align="left" onclick="javascript:check_proxy(this)">
            <abbr title=""><script>'foo' 'bar' 'spam'</script> </abbr>
        </td>
        <td align="left">
            <a href="/proxy-server-list/port-7070/" title="Port 7070 proxies">7070</a>
        </td>
    </tr>
"""


class TestProviderRequestBase(unittest.TestCase):
    url = URL

    @patch('proxy_db.providers.create_session')
    @patch('proxy_db.providers.ProviderRequestBase.get_or_create')
    def test_now(self, m2, m1):
        session_mock = requests_mock.Mocker()
        session_mock.start()
        req_mock = session_mock.get(self.url, text=PROVIDER_HTML)
        self.get_provider_request().now()
        self.assertTrue(req_mock.called_once)
        session_mock.stop()
        m1.return_value.commit.assert_called()
        m2.assert_called_with(m1.return_value, {'results': 2})

    def test_requires_update(self):
        instance = Mock()
        instance.updated_at = datetime.datetime.now() - datetime.timedelta(minutes=PROVIDER_REQUIRES_UPDATE_MINUTES)
        instance.updated_at -= datetime.timedelta(minutes=1)
        with patch('proxy_db.providers.ProviderRequestBase.get_or_create', return_value=(instance, True)):
            self.assertTrue(self.get_provider_request().requires_update())

    def test_requires_update_not_exists(self):
        self.assertTrue(self.get_provider_request().requires_update())

    def test_get_or_create(self):
        request_provider = self.get_provider_request()
        instance, _ = request_provider.get_or_create()
        self.assertEqual(instance.results, 0)
        self.assertEqual(instance.request_id, request_provider.id)
        self.assertEqual(instance.provider, request_provider.provider.name)

    def get_provider(self):
        return Provider(self.url)

    def get_provider_request(self):
        return ProviderRequestBase(self.get_provider(), self.url, options={'country': 'es', 'spam': 1})

    def test_id(self):
        self.assertEqual(self.get_provider_request().id, 'es-1')


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

    @patch("proxy_db.providers.getLogger")
    def test_invalid_rows(self, m):
        provider = ProxyNovaCom()
        request = Mock()
        request.text = PROXY_NOVA_INVALID_ROWS_HTML
        self.assertEqual(provider.find_page_proxies(request), [])
        self.assertEqual(
            m.return_value.warning.call_count, 3,
            "Expected 'warning' to have been called 3 times. Called {}".format(
                m.return_value.warning.call_count
            )
        )


class TestNoProviderInfiniteLoop(unittest.TestCase):
    """Test to make sure that it doesn't fall into an infinite loop when
    next(ProxiesList(country)) is called with a country with no proxies."""

    @patch("proxy_db.proxies.ProxiesList.reload_provider")
    @patch("proxy_db.proxies.ProxiesList.find_db_proxy")
    def test_infinite_recursion_loop_solution(self, reload_provider_mock, find_db_proxy_mock):
        """This call was falling into a recursion loop. Now tries only twice and then raise
        an StopIteration exception."""
        from proxy_db.proxies import ProxiesList
        reload_provider_mock.return_value = None
        find_db_proxy_mock.return_value = None

        self.assertRaises(StopIteration, lambda: next(ProxiesList("country")))
        self.assertEqual(find_db_proxy_mock.call_count, 2)
        self.assertEqual(reload_provider_mock.call_count, 2)
