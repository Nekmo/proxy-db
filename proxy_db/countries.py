from __future__ import absolute_import
import os
import sys
import tarfile
import tempfile

import geoip2.database
from geoip2.errors import AddressNotFoundError

from proxy_db.utils import download_file

if sys.version_info < (3, 0):
    from itertools import ifilter as filter


COUNTRIES_DOWNLOAD_URL = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.tar.gz'
COUNTRIES_FILE = os.environ.get('COUNTRIES_FILE', os.path.expanduser('~/.local/var/lib/proxy-db/countries.mmdb'))
GEOLINE_FILE_NAME = 'GeoLite2-Country.mmdb'


reader = None


def extract_file_to(tar, member_path, to):
    obj = tar.extractfile(member_path)
    if sys.version_info >= (3, 3):
        with obj as member:
            with open(to, 'wb') as f:
                f.write(member.read())
    else:
        with open(to, 'wb') as f:
            f.write(obj.read())
            obj.close()


def reload_countries_db():
    proxy_db_dir = os.path.dirname(COUNTRIES_FILE)
    if not os.path.lexists(proxy_db_dir):
        os.makedirs(proxy_db_dir)

    tar_file = download_file(COUNTRIES_DOWNLOAD_URL, tempfile.NamedTemporaryFile().name)
    tar = tarfile.open(tar_file, "r:gz")
    member_path = next(filter(lambda x: x.endswith(GEOLINE_FILE_NAME), tar.getnames()))
    extract_file_to(tar, member_path, COUNTRIES_FILE)
    tar.close()
    os.remove(tar_file)


def init_reader():
    if not os.path.lexists(COUNTRIES_FILE):
        reload_countries_db()
    return geoip2.database.Reader(COUNTRIES_FILE)


def ip_country(ip):
    global reader
    if reader is None:
        reader = init_reader()
    try:
        country = reader.country(ip)
    except AddressNotFoundError:
        return ''
    else:
        return country.country.iso_code
