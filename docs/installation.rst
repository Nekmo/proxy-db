.. highlight:: console

============
Installation
============


Stable release
--------------

To install proxy-db, run these commands in your terminal:

.. code-block:: console

    $ pip3 install -U proxy-db

This is the preferred method to install proxy-db, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

Geoip support
-------------
Some providers do not have the correct country for proxies. To determine the correct country proxy-db can use geoip.
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

Or from the command line before starting the program::

    $ export MAXMIND_LICENSE_KEY=28xjifHSTxVq93xZ

HTTPS & SOCKS5 proxies
----------------------
To use **socks5 proxies** with requests you need to install socks support::

    $ pip3 install proxy-db[socks]

To use **HTTPS proxies** with requests/urllib3 you need to install the latests urllib3 version from sources::

    $ pip install https://github.com/urllib3/urllib3/archive/master.zip

Version 1.26 of urllib3 finally supports
`TLS-in-TLS tunnels through proxies <( https://github.com/urllib3/urllib3/pull/2001 )>`_. This version will be
available very soon but until then it is necessary to install it from source code. In case of incompatibility,
`this (deprecated) dependency <https://github.com/phuslu/requests_httpsproxy/>`_ allows the use of https proxies with
requests.


Other releases
--------------
You can install other versions from Pypi using::

    $ pip install proxy-db==<version>

For versions that are not in Pypi (it is a development version)::

    $ pip install git+https://github.com/Nekmo/proxy-db.git@<branch>#egg=proxy_db


If you do not have git installed:

    $ pip install https://github.com/Nekmo/proxy-db/archive/<branch>.zip
