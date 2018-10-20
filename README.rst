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
Add a positive vote if the proxy works correctly and a negative vote if it does not work. In addition, proxy-db
determines the real country of the proxy using geoip.

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


Proxy-db will return the best proxies first (more positive votes). You can also filter by country:

.. code-block:: python

    from proxy_db.proxies import ProxiesList

    spain_proxy = next(ProxiesList('es'))
    # ...


Free proxies providers included:

* ProxyNova


Install
=======
If you have Pip installed on your system, you can use it to install the latest ProxyDB stable version::

    $ sudo pip3 install proxy-db

Python 2.7 & 3.4-3.7 are supported but Python 3.x is recommended. Use ``pip2`` on install for Python2.


* Free software: Apache Software License 2.0
