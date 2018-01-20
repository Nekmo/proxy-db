import os
import tarfile
import tempfile

import geoip2.database
from geoip2.errors import AddressNotFoundError

from proxy_db.utils import download_file

COUNTRIES_DOWNLOAD_URL = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.tar.gz'
COUNTRIES_FILE = os.environ.get('COUNTRIES_FILE', os.path.expanduser('~/.local/var/lib/proxy-db/countries.mmdb'))
GEOLINE_FILE_NAME = 'GeoLite2-Country.mmdb'


def reload_countries_db():
    proxy_db_dir = os.path.dirname(COUNTRIES_FILE)
    if not os.path.lexists(proxy_db_dir):
        os.makedirs(proxy_db_dir)

    tar_file = download_file(COUNTRIES_DOWNLOAD_URL, tempfile.NamedTemporaryFile().name)
    tar = tarfile.open(tar_file, "r:gz")
    member_path = next(filter(lambda x: x.endswith(GEOLINE_FILE_NAME), tar.getnames()))
    obj = tar.extractfile(member_path)
    with obj as member:
        with open(COUNTRIES_FILE, 'wb') as f:
            f.write(member.read())
    tar.close()
    os.remove(tar_file)


def init_reader():
    if not os.path.lexists(COUNTRIES_FILE):
        reload_countries_db()
    return geoip2.database.Reader(COUNTRIES_FILE)


def ip_country(ip):
    try:
        country = reader.country(ip)
    except AddressNotFoundError:
        return ''
    else:
        return country.country.iso_code


reader = init_reader()
