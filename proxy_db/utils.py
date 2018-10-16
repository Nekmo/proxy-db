from __future__ import absolute_import
import requests
from proxy_db._compat import urlparse


def download_file(url, local_filename=None):
    local_filename = local_filename or url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return local_filename


def get_domain(address):
    netloc = urlparse(address).netloc
    return netloc.split('@')[-1].split(':')[0]
