from __future__ import absolute_import
from importlib import import_module
from six import raise_from

from proxy_db._compat import urlparse


def get_domain(address):
    netloc = urlparse(address).netloc
    return netloc.split('@')[-1].split(':')[0]


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
        # raise ImportError("%s doesn't look like a module path" % dotted_path) from err
        raise_from(ImportError("%s doesn't look like a module path" % dotted_path), err)


    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        # raise ImportError('Module "%s" does not define a "%s" attribute/class' % (
        #     module_path, class_name)
        # ) from err
        raise_from(ImportError('Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
        ), err)
