import os
from typing import Optional

import click
from click import echo, secho

import bitcaster_sdk
from bitcaster_sdk.client import Client
from bitcaster_sdk.exceptions import AuthenticationError

# client: Optional["Client"] = None

def avoid_double_slash(path):
    parts = path.split('/')
    not_empties = [part for part in parts if part]
    return '/'.join(not_empties)
def clean_bae(bae: str):
    while len(bae) > 0 and bae[-1] == "/":
        bae = bae[:-1]
    return bae


@click.group()
@click.option("--bae", envvar="BITCASTER_BAE")
def cli(bae: str):
    try:
        bitcaster_sdk.init(clean_bae(bae))
    except Exception as e:
        raise click.ClickException(f"Failed to initialize bitcaster. {e}")


@cli.command(name="list")
def list_():
    FMT = "{:>5}: {:<20} {:<20} {:^8} {:^8} {}"
    try:
        ret = bitcaster_sdk.list_events()
        secho(FMT.format("#", "Name", "Slug", "active", "locked", "description"))
        for n, e in enumerate(ret, 1):
            cl = "white"
            if e["locked"]:
                cl = "red"
            elif e["active"]:
                cl = "green"
            elif not e["active"]:
                cl = "yellow"
            secho(
                FMT.format(
                    n,
                    e["name"],
                    e["slug"],
                    "\u2713" if e["active"] else "",
                    "\u2713" if e["locked"] else "",
                    e["description"] or "",
                ),
                fg=cl,
            )

    except AuthenticationError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise
        raise click.ClickException(f"Unable to contact server {client.base_url}")


@cli.command()
def ping():
    try:
        ret = client.ping()
        echo(ret)
    except AuthenticationError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Unable to contact server {client.base_url}")


@click.argument("event")
@click.option("--debug", "-d", type=bool, is_flag=True)
@click.option("--context", "-c", "context", type=(str, str), multiple=True)
@click.option("--options", "-o", "options", type=(str, str), multiple=True)
@cli.command()
def trigger(event, context, options, debug):
    if debug:
        echo(f"Context: {dict(context)}")
        echo(f"Options: {dict(options)}")
    try:
        ret = client.trigger(event, dict(context), dict(options))
        echo(ret)
    except AuthenticationError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Unable to contact server {client.base_url}")


if __name__ == "__main__":
    cli(obj={}, auto_envvar_prefix="BITCASTER")
