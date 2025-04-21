# Copyright Amethyst Reese
# Licensed under the MIT license

import logging
import sys

from dataclasses import dataclass

import click

from .core import Bluepost, Cache


@dataclass
class Options:
    username: str
    password: str
    target: str


@click.group()
@click.pass_context
@click.option("--clear-cache", is_flag=True, help="Clear cached data before starting")
@click.option("--username", type=str, required=True, help="Bluesky username/handle")
@click.option("--password", type=str, required=True, help="Bluesky password")
@click.option("--target", type=str, required=True, help="Bluesky handle to mirror")
def main(
    ctx: click.Context, clear_cache: bool, username: str, password: str, target: str
) -> None:
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    if clear_cache:
        Cache.clear()

    ctx.obj = Options(username=username, password=password, target=target)


@main.command()
@click.pass_context
def auth(ctx: click.Context) -> None:
    """Validate authentication"""
    options: Options = ctx.obj

    Bluepost.init(options.username, options.password)


@main.command()
@click.pass_context
def run(ctx: click.Context) -> None:
    """Run once and exit"""
    options: Options = ctx.obj

    blue = Bluepost.init(options.username, options.password)
    blue.run_once(options.target)


@main.command()
@click.pass_context
@click.option(
    "--interval",
    type=click.IntRange(min=1),
    default=3,
    show_default=True,
    help="Interval in minutes",
)
def serve(ctx: click.Context, interval: int) -> None:
    """Run periodically until interrupted"""
    options: Options = ctx.obj

    blue = Bluepost.init(options.username, options.password)
    blue.run_forever(options.target, interval=interval)


def run_main() -> None:
    main(auto_envvar_prefix="BLUEPOST")
