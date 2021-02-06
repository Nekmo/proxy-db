try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


try:
    from itertools import filterfalse
except ImportError:
    def filterfalse(predicate, iterable):
        # filterfalse(lambda x: x%2, range(10)) --> 0 2 4 6 8
        if predicate is None:
            predicate = bool
        for x in iterable:
            if not predicate(x):
                yield x
