# -*- coding: utf-8 -*-

"""Console script for proxy_db."""

import click

from proxy_db.providers import ProxyNovaCom


@click.command()
def main(args=None):
    """Console script for proxy_db."""
    click.echo("Replace this message by putting your code into "
               "proxy_db.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")
    req = ProxyNovaCom().request('cl')
    if req.requires_update():
        req.now()
