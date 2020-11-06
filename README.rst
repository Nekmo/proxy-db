.. image:: https://raw.githubusercontent.com/Nekmo/proxy-db/master/images/proxy-db.png

|

.. image:: https://img.shields.io/travis/Nekmo/proxy-db.svg?style=flat-square
  :target: https://travis-ci.org/Nekmo/proxy-db
  :alt: Latest Travis CI build status

.. image:: https://img.shields.io/pypi/v/proxy-db.svg?style=flat-square
  :target: https://pypi.org/project/proxy-db/
  :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/pyversions/proxy-db.svg?style=flat-square
  :target: https://pypi.org/project/proxy-db/
  :alt: Python versions

.. image:: https://img.shields.io/codeclimate/maintainability/Nekmo/proxy-db.svg?style=flat-square
  :target: https://codeclimate.com/github/Nekmo/proxy-db
  :alt: Code Climate

.. image:: https://img.shields.io/codecov/c/github/Nekmo/proxy-db/master.svg?style=flat-square
  :target: https://codecov.io/github/Nekmo/proxy-db
  :alt: Test coverage

.. image:: https://img.shields.io/requires/github/Nekmo/proxy-db.svg?style=flat-square
     :target: https://requires.io/github/Nekmo/proxy-db/requirements/?branch=master
     :alt: Requirements Status


========
proxy-db
========


Manage free and private proxies on local db for Python Projects. Each proxy has a score according to how it works.
Add a positive vote if the proxy works correctly and a negative vote if it does not work.

.. code-block:: python

    import requests
    from requests.exceptions import Timeout, ConnectionError, ProxyError
    from proxy_db.proxies import ProxiesList

    proxy = next(ProxiesList())
    try:
        requests.get('http://site.com/', proxies=proxy)
    except (Timeout, ConnectionError, ProxyError):
        proxy.negative()
    else:
        proxy.positive()


Proxy-db will return the best proxies first (more positive votes). You can also **filter by country**:

.. code-block:: python

    from proxy_db.proxies import ProxiesList

    spain_proxy = next(ProxiesList('es'))
    # ...


You can also **filter by provider**:

.. code-block:: python

    from proxy_db.proxies import ProxiesList

    proxy_nova_proxy = next(ProxiesList(provider='Proxy Nova'))
    # ...


Free proxies providers included:

* Proxy Nova
* Nord VPN (requires ``PROXYDB_NORDVPN_USERNAME`` & ``PROXYDB_NORDVPN_PASSWORD`` env. variables).

For more information see `the docs <https://docs.nekmo.org/proxy-db/>`_.


Install
=======
If you have **Pip installed on your system**, you can use it to install the latest ProxyDB stable version::

    $ pip3 install proxy-db

Python 2.7 & 3.4-3.7 are supported but Python 3.x is recommended. Use ``pip2`` on install for Python2.
`More info in the documentation <https://docs.nekmo.org/proxy-db/installation.html>`_

Some providers do not have the correct country for proxies. To determine the correct country proxy-db can use **geoip**.
To use this install the optional dependencies::

    $ pip3 install proxy-db[geoip]

You also need a maxmind Geolite2 license (it's free). To obtain the license, follow these steps:

1. `Sign up for a Maxmind Geolite2 account <https://www.maxmind.com/en/geolite2/signup>`_
2. `Log in to your Maxmind account <https://www.maxmind.com/en/account/login>`_
3. In the menu on the left, navigate to ``Services > My License Key``.
4. Click ``Generate new license key``.

Sets the environment variable ``MAXMIND_LICENSE_KEY``. To set it from Python::

    import os
    os.environ['MAXMIND_LICENSE_KEY'] = '28xjifHSTxVq93xZ'

HTTPS & SOCKS5 proxies
----------------------
To use **socks5 proxies** with requests you need to install socks support::

    $ pip3 install proxy-db[socks]

To use **HTTPS proxies** with requests/urllib3 you need to install the latests urllib3 version from sources::

    $ pip install https://github.com/urllib3/urllib3/archive/master.zip
