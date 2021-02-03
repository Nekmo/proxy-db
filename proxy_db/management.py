# -*- coding: utf-8 -*-

import click

from proxy_db.providers import ManualProxy
from proxy_db._compat import urlparse


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
def add(file=None, votes=10, provider='default', proxies=None):
    """Add proxies in <protocol>://<address>:<port> format or <protocol>://<username>:<password>@<address>:<port>
    format.'"""
    if not file and not proxies:
        click.echo('Trying to read proxies from stdin. Use Ctrl + C to cancel. '
                   'To add proxies in another way use --help.')
        proxies = click.get_text_stream('stdin')
    elif file:
        proxies = file.read()
    proxies = [urlparse(proxy) for proxy in proxies]
    proxies = [{'protocol': proxy.scheme, 'proxy': proxy.netloc} for proxy in proxies]
    proxy_instances = ManualProxy(provider).add_proxies(proxies)
    created = filter(lambda x: x.updated_at is None, proxy_instances)
    click.echo('Read {} proxies. {} new proxies have been created.'.format(len(proxies), len(list(created))))


if __name__ == '__main__':
    cli()
