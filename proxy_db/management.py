# -*- coding: utf-8 -*-

import click


@click.group()
def cli():
    pass


@cli.command()
@click.option('--file', prompt='File path', help='Path to the file with the proxies.')
def add(file):
    """Add proxies from a file or from stdin."""


if __name__ == '__main__':
    cli()
