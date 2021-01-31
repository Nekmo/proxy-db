# -*- coding: utf-8 -*-

import click


@click.group()
def cli():
    pass


@cli.command()
@click.option('--file', prompt='File path', help='Path to the file with the proxies.', default='',
              type=click.File('r'))
def add(file=None):
    """Add proxies from a file or from stdin."""
    if not file:
        lines = click.get_text_stream('stdin')
    else:
        lines = file.read()


if __name__ == '__main__':
    cli()
