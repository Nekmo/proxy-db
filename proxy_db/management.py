# -*- coding: utf-8 -*-
import string
from itertools import filterfalse

import click

from proxy_db.providers import ManualProxy
from proxy_db._compat import urlparse


def proxy_is_valid(proxy):
    return proxy.scheme and proxy.netloc


def strip_chars(text, remove_chars=string.whitespace):
    length = len(text)
    start = 0
    end = length
    for i, char in enumerate(text):
        if char not in remove_chars:
            break
        start = i + 1
    for i, char in enumerate(reversed(text)):
        if char not in remove_chars:
            break
        end = length - i - 1
    return text[start:end]


@click.group()
def cli():
    pass


@cli.command()
@click.option('--file', help='Path to the file with the proxies.',
              type=click.File('r'), required=False)
@click.option('--votes', default=10, type=int,
              help='Default votes score. This counter sets the order in which the proxies will be obtained.')
@click.option('--provider', default='manual', type=str,
              help='Provider name for proxies. It allows to know the origin of the proxies and search by provider.')
@click.argument('proxies', type=str, required=False, nargs=-1)
def add(file=None, votes=10, provider='manual', proxies=None):
    """Add proxies in <protocol>://<address>:<port> format or <protocol>://<username>:<password>@<address>:<port>
    format.'"""
    if not file and not proxies:
        click.echo('Trying to read proxies from stdin. Use Ctrl + C to cancel. '
                   'To add proxies in another way use --help.')
        proxies = click.get_text_stream('stdin')
    elif file:
        proxies = file.read()
    parsed_proxies = set([urlparse(strip_chars(proxy)) for proxy in proxies])
    invalid_proxies = set(filterfalse(proxy_is_valid, parsed_proxies))
    if invalid_proxies:
        click.echo('Invalid proxies entered: {}'.format(
            ', '.join(map(lambda x: x.geturl(), invalid_proxies))), err=True)
    parsed_proxies -= invalid_proxies
    proxies_data = [{'protocol': proxy.scheme, 'proxy': proxy.netloc} for proxy in parsed_proxies]
    proxy_instances = ManualProxy(provider).add_proxies(proxies_data, votes)
    created = filter(lambda x: x.updated_at is None, proxy_instances)
    click.echo('Read {} proxies. {} new proxies have been created.'.format(len(parsed_proxies), len(list(created))))


if __name__ == '__main__':
    cli()
