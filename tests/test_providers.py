#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `proxy-db` package."""
import copy
import datetime
import unittest

import requests_mock

from ._compat import Mock, patch

from proxy_db.providers import ProxyNovaCom, Provider, ProviderRequestBase, PROVIDER_REQUIRES_UPDATE_MINUTES, NordVpn

URL = 'https://domain.com/'
PROVIDER_HTML = """
Proxy: 12.131.91.51:8888
<b>Other: 8.10.81.82:7171.</b>
"""
PROXY_NOVA_HTML = """
<tr data-proxy-id="00000000">
    <td align="left">
        <abbr title="proxy.site.name">
            <script>document.write('91.217.28.125');</script>
        </abbr>
    </td>
    <td align="left">
        3128
    </td>
    <td align="left">
        <img src="/assets/images/blank.gif" class="flag flag-ua inline-block align-middle" alt="ua" />
        <a href="/proxy-server-list/country-ua/"
           title="Proxies from Ukraine">Ukraine
            <span class="proxy-city"> - Kyiv </span>
        </a>
    </td>
</tr>
<tr data-proxy-id="00000000">
    <td align="left">
        <abbr title="proxy.site.name">
            <script>document.write('89.145.199.64');</script>
        </abbr>
    </td>
    <td align="left">
        8080
    </td>
    <td align="left">
        <img src="/assets/images/blank.gif" class="flag flag-hu inline-block align-middle" alt="hu">
        <a href="/proxy-server-list/country-hu/" title="Proxies from Hungary">Hungary
            <span class="proxy-city"> - Debrecen </span>
        </a>
    </td>
</tr>
"""
PROXY_NOVA_INVALID_ROWS_HTML = """
<tr data-proxy-id="00000000">
    <td align="left">
        <abbr title="proxy.site.name">
            <script>document.write('91.217.2incomplete ip address</script>
        </abbr>
    </td>
    <td align="left">
        3128
    </td>
</tr>
<tr data-proxy-id="00000000">
    <td align="left">
        <abbr title="proxy.site.name">
            <script>document.write('89.145.199.64');</script>
        </abbr>
    </td>
    without port
</tr>
<tr data-proxy-id="00000000">
    <td align="left">
        without script
    </td>
    <td align="left">
        3128
    </td>
</tr>
"""
PROXY_NOVA_INVALID_COUNTRY = """
<tr data-proxy-id="00000000">
    <td align="left">
        <abbr title="proxy.site.name">
            <script>document.write('91.217.28.125');</script>
        </abbr>
    </td>
    <td align="left">
        3128
    </td>
    <td align="left">
        <img src="/assets/images/blank.gif" class="flag flag-ua inline-block align-middle" />
        Country is not available
    </td>
</tr>
<tr data-proxy-id="00000000">
    <td align="left">
        <abbr title="proxy.site.name">
            <script>document.write('89.145.199.64');</script>
        </abbr>
    </td>
    <td align="left">
        8080
    </td>
    <td align="left">
        <img src="/assets/images/blank.gif" class="flag flag-hu inline-block align-middle" alt="INVALID">
    </td>
</tr>
"""
NORDVPN_SERVERS = [
    {
        "id":0, "ip_address":"123.123.123.123", "search_keywords":[], "load":55,
        "categories":[{"name":"Standard VPN servers"}, {"name":"P2P"}], "name":"United States #0",
        "domain":"us0.nordvpn.com", "price":0, "flag":"US", "country":"United States", "location": {"lat":0, "long":0},
        "features": {
            "ikev2": True, "openvpn_udp": True, "openvpn_tcp": True, "socks": True, "proxy": True, "pptp": False,
            "l2tp": False, "openvpn_xor_udp": False, "openvpn_xor_tcp": False, "proxy_cybersec": False,
            "proxy_ssl": True, "proxy_ssl_cybersec": True, "ikev2_v6": False, "openvpn_udp_v6": False,
            "openvpn_tcp_v6": False, "wireguard_udp": False, "openvpn_udp_tls_crypt": False,
            "openvpn_tcp_tls_crypt": False, "openvpn_dedicated_udp": False, "openvpn_dedicated_tcp": False,
            "skylark": False
        }
    }
]


class TestProviderRequestBase(unittest.TestCase):
    url = URL

    @patch('proxy_db.providers.create_session')
    @patch('proxy_db.providers.ProviderRequestBase.get_or_create', return_value=(Mock(), None))
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
            {'proxy': '91.217.28.125:3128', 'country_code': 'UA'},
            {'proxy': '89.145.199.64:8080', 'country_code': 'HU'},
        ])

    @patch("proxy_db.providers.getLogger")
    def test_invalid_country(self, m):
        provider = ProxyNovaCom()
        request = Mock()
        request.text = PROXY_NOVA_INVALID_COUNTRY
        self.assertEqual(provider.find_page_proxies(request), [
            {'proxy': '91.217.28.125:3128', 'country_code': None},
            {'proxy': '89.145.199.64:8080', 'country_code': None},
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


class TestNordVPN(unittest.TestCase):
    url = NordVpn.base_url

    @patch("proxy_db.providers.Provider.request")
    def test_request(self, m):
        provider = NordVpn()
        provider.request(self.url)
        m.assert_called_with(self.url, None)

    def test_find_page_proxies(self):
        provider = NordVpn()
        request = Mock()
        request.json.return_value = NORDVPN_SERVERS
        self.assertEqual(provider.find_page_proxies(request), [
            {'country_code': 'US', 'protocol': 'socks5', 'proxy': '123.123.123.123:1080'},
            {'country_code': 'US', 'protocol': 'http', 'proxy': '123.123.123.123:80'},
            {'country_code': 'US', 'protocol': 'https', 'proxy': 'us0.nordvpn.com:89'}
        ])

    def test_invalid_country(self):
        provider = NordVpn()
        request = Mock()
        servers = copy.deepcopy(NORDVPN_SERVERS)
        servers[0]['flag'] = 'FOO'
        servers[0]['features'] = {'socks': True}
        request.json.return_value = servers
        self.assertEqual(provider.find_page_proxies(request), [
            {'country_code': None, 'protocol': 'socks5', 'proxy': '123.123.123.123:1080'},
        ])


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
