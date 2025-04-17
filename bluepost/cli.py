# Copyright Amethyst Reese
# Licensed under the MIT license

import logging
import os
import sys

import click

from .core import Cache, run


@click.command()
@click.pass_context
@click.option("--clear-cache", is_flag=True)
def main(ctx: click.Context, clear_cache: bool) -> None:
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.debug("running cli")

    username = os.getenv("BLUEPOST_USERNAME")
    password = os.getenv("BLUEPOST_PASSWORD")
    target = os.getenv("BLUEPOST_TARGET")

    if not all((username, password, target)):
        ctx.fail(
            "env must define BLUEPOST_USERNAME, BLUEPOST_PASSWORD, and BLUEPOST_TARGET"
        )

    if clear_cache:
        Cache.clear()

    run(username, password, target)
