import click
from click import echo, secho

import bitcaster_sdk
from bitcaster_sdk.exceptions import AuthenticationError


@click.group()
@click.option("--bae", envvar="BITCASTER_BAE")
@click.option("--debug", default=False, is_flag=True, envvar="BITCASTER_DEBUG")
def cli(bae: str, debug: bool):
    try:
        bitcaster_sdk.init(bae, debug=debug)
    except Exception as e:
        raise click.ClickException(f"Failed to initialize Bitcaster. {e}")


@cli.command(name="list")
def list_() -> None:
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
            else: # e["active"]:
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
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command()
def ping() -> None:
    try:
        ret = bitcaster_sdk.ping()
        echo(ret)
    except Exception as e:
        raise click.ClickException(str(e))


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
        ret = bitcaster_sdk.trigger(event, dict(context), dict(options))
        echo(ret)
    except Exception as e:
        raise click.ClickException(str(e))


if __name__ == "__main__":
    cli(obj={}, auto_envvar_prefix="BITCASTER")
