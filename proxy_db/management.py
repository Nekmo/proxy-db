# -*- coding: utf-8 -*-
import string

import click

from proxy_db.export import get_export_output, DEFAULT_COLUMNS
from proxy_db.models import Proxy, create_session, ProviderRequest
from proxy_db.providers import ManualProxy
from proxy_db.export import get_export_output_classes
from proxy_db._compat import urlparse, filterfalse


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


@cli.command()
@click.option('--format', help='Output format to use. By default "line". '
                               'Options: {}'.format(', '.join([x.name for x in get_export_output_classes()])),
              default='line')
@click.option('--columns', help='Command separated columns to output using format.'
                                'You can use double low bar for related models. '
                                'Choices: {}'.format(', '.join(DEFAULT_COLUMNS)), default='')
@click.option('--min-votes', type=int, help='Minimum votes of proxies to list.', default=None)
@click.option('--country', help='2 character country code to filter. For example US.', default='')
@click.option('--protocol', help='Proxy protocol name. Examples: http, https, socks5.', default='')
@click.option('--provider', help='Provider name to filter.', default='')
def list(format, columns, min_votes, country, protocol, provider):
    """List proxies registered in proxy-db.'"""
    columns = [c.strip() for c in columns.split(',')] if columns else []
    session = create_session()
    proxies = session.query(Proxy)
    if min_votes is not None:
        proxies = proxies.filter(Proxy.votes > min_votes)
    if country:
        proxies = proxies.filter(Proxy.country == country.upper())
    if protocol:
        proxies = proxies.filter(Proxy.protocol == protocol.lower())
    if provider:
        proxies = proxies.join(Proxy.provider_requests).filter(
            ProviderRequest.provider == provider,
        )
    proxies = proxies.all()
    output = get_export_output(format, proxies, columns)
    click.echo(output)


if __name__ == '__main__':
    cli()
