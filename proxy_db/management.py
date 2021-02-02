# -*- coding: utf-8 -*-

import click


@click.group()
def cli():
    pass


@cli.command()
@click.option('--file', help='Path to the file with the proxies.',
              type=click.File('r'), required=False)
@click.argument('proxies', type=str, required=False, nargs=-1)
def add(file=None, proxies=None):
    """Add proxies in <protocol>://<address>:<port> format or <protocol>://<username>:<password>@<address>:<port>
    format.'"""
    if not file and not proxies:
        click.echo('Trying to read proxies from stdin. Use Ctrl + C to cancel. '
                   'To add proxies in another way use --help.')
        proxies = click.get_text_stream('stdin')
    elif file:
        proxies = file.read()
    click.echo('Read {} proxies.'.format(len(proxies)))


if __name__ == '__main__':
    cli()
