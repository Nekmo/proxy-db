# -*- coding: utf-8 -*-

"""Top-level package for proxy-db."""
import logging

__author__ = """Nekmo Com"""
__email__ = 'contacto@nekmo.com'
__version__ = '0.2.5'

logging.basicConfig()
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)
