# -*- coding: utf-8 -*-

"""Console script for proxy_db."""

import click


@click.group()
def cli():
    pass


@cli.command()
def add():
    """Add proxies from a file or from stdin."""


if __name__ == '__main__':
    cli()
