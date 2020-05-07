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


Other releases
--------------
You can install other versions from Pypi using::

    $ pip install proxy-db==<version>

For versions that are not in Pypi (it is a development version)::

    $ pip install git+https://github.com/Nekmo/proxy-db.git@<branch>#egg=proxy_db


If you do not have git installed:

    $ pip install https://github.com/Nekmo/proxy-db/archive/<branch>.zip
