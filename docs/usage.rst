

Usage
=====
proxy-db uses *free proxy pages* to feed a **local proxy database**. By default the database is created in
``~/.local/var/lib/proxy-db/db.sqlite3``, although you can change the location and use other db engines.
The proxies score is stored in this database. To **increase the score** of a proxy (the proxy works) use the
``proxy.positive()`` method, and use ``proxy.negative()`` if **it fails**.


.. code-block:: python

    >>> from proxy_db.proxies import ProxiesList
    >>> p = next(ProxiesList())
    >>> p
    <Proxy http://5.0.0.0:8080>
    >>> p.positive()  # Increase score
    >>> p.votes  # current score
    1
    >>> str(p)  # return proxy string
    'http://5.0.0.0:8080'
    >>> p.country  # proxy country
    'ES'

By default ProxiesList will return proxies ordered by number of votes.


Use with requests
-----------------
proxy-db is very easy to use with requests. In this example it vote positive if it works and negative if the proxy
fails.

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

In this example test proxies **to find a proxy that works**:

.. code-block:: python

    import requests
    from requests.exceptions import Timeout, ConnectionError, ProxyError
    from proxy_db.proxies import ProxiesList

    resp = None

    for proxy in ProxiesList():
        try:
            resp = requests.get('http://site.com/', proxies=proxy)
        except (Timeout, ConnectionError, ProxyError):
            proxy.negative()
        else:
            proxy.positive()
            break

    if resp is not None:
        print(f'Response: {resp.text}')
    else:
        print('Could not get response')


Countries
---------
To force the country of the proxies use the country code in ``ProxiesList``:

.. code-block::

    >>> from proxy_db.proxies import ProxiesList
    >>> p = next(ProxiesList('es'))
    >>> p.country
    'ES'

Countries use `the 2-character iso code <https://countrycode.org/>`_.


Change list strategy
====================
By default proxy-db sorts proxies by votes and only returns those with more than 1 vote (ignore with negative votes).
There are other strategies available like returning random proxies:

.. code-block::

    >>> from proxy_db.proxies import ProxiesList, RandomListingStrategy
    >>> p = next(ProxiesList(strategy=RandomListingStrategy))

It is also possible to change the default strategy options:

.. code-block::

    >>> from proxy_db.proxies import ProxiesList, VotesListingStrategy
    >>> p = next(ProxiesList(strategy=VotesListingStrategy(min_votes=-5)))


Change database
---------------
To change the path to the sqlite database define the environment variable ``PROXY_DB_FILE``, by default
``~/.local/var/lib/proxy-db/db.sqlite3``. The environment variable ``PROXY_DB_DB_URL`` changes the
database configuration, by default ``sqlite:///{PROXY_DB_FILE}``.

proxy-db uses sqlalchemy. For more information about how to configure the url to the database,
`check its documentation <https://docs.sqlalchemy.org/en/13/core/engines.html>`_.

Add proxies manually
====================
You can add one or more proxies per command line to insert them into the database. To add proxies::

    $ proxy-db add[ <proxy_1>][ <proxy_2>][ <proxy_n>]

For example::

    $ proxy-db add http://5.0.0.0:8080 http://6.0.0.0:8080 http://7.0.0.0:8080

You can also import proxies from a file, with one proxy per line::

    $ proxy-db add --file <filename>

For example::

    $ proxy-db add --file proxies.txt

You can also send the proxies stdin, one proxy per line::

    $ proxy-db add < proxies.txt

By default the proxies are created with the *"manual"* provider but this can be changed using the
``--provider <provider_anem>`` parameter. For example::

    $ proxy-db add --provider "my_provider" http://5.0.0.0:8080

Added proxies have 10 positive votes by default. These votes will increase with successful requests and
will decrease if the proxy fails. To change the default votes use the ``--votes <votes>`` parameter. For example::

    $ proxy-db add --votes 50 http://5.0.0.0:8080


List proxies
============
To list all the proxies already available you can use the following command::

    $ proxy-db list
    http://185.146.167.226:1080
    http://185.89.182.32:86
    http://186.28.217.19:80
    http://185.116.137.248:1080
    http://185.176.129.14:1080
    ...


By default the proxies will be listed line by line as in the previous example. You can change the format
using ``--format <format>``. Available options: line, json. More options are available by installing
the ``tabulate`` package using ``pip install tabulate``. To see all the options after installing
*tabulate* use ``proxy-db list --help``.

.. code-block:: shell

    $ proxy-db list --format json


It is also possible to choose the columns to display. To see the available columns use ``proxy-db list --help``::

    $ proxy-db list --columns <column1[,<column2>]>


For example::

    $ proxy-db list --columns id,votes,country,protocol,providers


Proxies can be filtered using various options::

    $ proxy list[ --min-votes <votes>][ --country <country code>]
                [ --protocol <protocol>][ --provider <provider>]


For example::

    $ proxy list --min-votes 10 --country ES \
                 --protocol https --provider "Nord VPN"


Payment providers
=================
Some providers require a payment and additional steps to use.

Nord VPN
--------

1. Login in Nord VPN.
2. Go to `Nord VPN service details <https://my.nordaccount.com/dashboard/nordvpn/>`_.
3. In **advanced configuration** copy/create your **username** and **password** for *Service credentials
   (manual setup)*. These credentials are different from the username and password to log into the
   Nord VPN website.
4. Set environment variables ``PROXYDB_NORDVPN_USERNAME`` and ``PROXYDB_NORDVPN_PASSWORD`` in your program.

To set **environment variables in Python**:

.. code-block:: python

    import os

    os.environ['PROXYDB_NORDVPN_USERNAME'] = '2dybg3pvxN4XYpLpF2iBE3wz'
    os.environ['PROXYDB_NORDVPN_PASSWORD'] = 'hjFq8QkKsnKM42o4Yzta8y2K'

To set **environment variables in Bash** (before run your program):


.. code-block:: shell

    $ export PROXYDB_NORDVPN_USERNAME=2dybg3pvxN4XYpLpF2iBE3wz
    $ export PROXYDB_NORDVPN_PASSWORD=hjFq8QkKsnKM42o4Yzta8y2K

    $ ./your-program.py

