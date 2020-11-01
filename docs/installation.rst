.. highlight:: console

============
Installation
============


Stable release
--------------

To install proxy-db, run these commands in your terminal:

.. code-block:: console

    $ sudo pip3 install -U proxy-db

This is the preferred method to install proxy-db, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

Geoip support
-------------
Some providers do not have the correct country for proxies. To determine the correct country proxy-db can use geoip.
To use this install the optional dependencies::

    $ sudo pip3 install proxy-db[geoip]

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

Other releases
--------------
You can install other versions from Pypi using::

    $ pip install proxy-db==<version>

For versions that are not in Pypi (it is a development version)::

    $ pip install git+https://github.com/Nekmo/proxy-db.git@<branch>#egg=proxy_db


If you do not have git installed:

    $ pip install https://github.com/Nekmo/proxy-db/archive/<branch>.zip
