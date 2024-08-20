import os

import click
from click import echo, secho
from click.core import Context

import bitcaster_sdk
from bitcaster_sdk import client, logging
from bitcaster_sdk.exceptions import AuthenticationError, EventNotFound

TITLE = "  {}"


@click.group()
@click.option("--bae", envvar="BITCASTER_BAE", metavar="BAE", help="Bitcaster BAE. Not needed if $BITCASTER_BAE is set")
@click.option("--debug", default=False, is_flag=True, envvar="BITCASTER_DEBUG")
@click.pass_context
def cli(ctx: Context, bae: str, debug: bool) -> None:
    try:
        if not bae and not os.environ.get("BITCASTER_BAE"):
            raise Exception("Set BITCASTER_BAE environment variable or pass Bitcaster address as argument")
        ctx.obj = {"debug": debug}
        if debug:
            logging.configure_api()
        else:
            logging.configure_cli()

        bitcaster_sdk.init(bae, debug=debug)
    except Exception as e:
        raise click.ClickException(f"Failed to initialize Bitcaster. {e}")


@cli.command(name="lists", help="lists Project's DistributionList")
@click.option("--project", "-p", required=True, envvar="BITCASTER_PROJECT", metavar="PROJECT", help="Bitcaster Project")
@click.pass_context
def lists(ctx: Context, project: str) -> None:
    FMT = "{:>5}: {:<20} {:<20}"
    try:
        ret = bitcaster_sdk.list_distribution_lists(project)
        if ctx.obj["debug"]:
            secho(client.ctx.get().last_called_url)
        secho(TITLE.format("Project Distribution Lists"), fg="green")
        secho(FMT.format("#", "Id", "Name"))
        for n, e in enumerate(ret, 1):
            secho(
                FMT.format(n, e["id"], e["name"]),
            )
    except AuthenticationError:
        raise click.Abort("AuthenticationError")
    except EventNotFound:
        raise click.Abort("Project or Application not found")
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command(name="members", help="lists DistributionList Members")
@click.option("--distribution", "-d", required=True, metavar="DISTRIBUTION", help="Project distribution list id")
@click.option("--project", "-p", required=True, envvar="BITCASTER_PROJECT", metavar="PROJECT", help="Bitcaster Project")
@click.pass_context
def members(ctx: Context, project: str, distribution: str) -> None:
    FMT = "{:>3}: {:<4} {:<30} {:<30} {:<30}"
    try:
        ret = bitcaster_sdk.list_members(project, distribution)
        if ctx.obj["debug"]:
            secho(client.ctx.get().last_called_url)
        secho(TITLE.format("Distribution Lists Members"), fg="green")
        secho(FMT.format("#", "Id", "Address", "User", "Channel"))
        for n, e in enumerate(ret, 1):
            secho(
                FMT.format(n, e["id"], e["address"], e["user"], e["channel"]),
            )
    except AuthenticationError:
        raise click.Abort("AuthenticationError")
    except EventNotFound:
        raise click.Abort("Project or Application not found")
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command(name="events", help="lists Application's Events")
@click.option(
    "--project", "-p", required=True, envvar="BITCASTER_PROJECT", metavar="PROJECT", help="Bitcaster default Project"
)
@click.option(
    "--application",
    "-a",
    required=True,
    envvar="BITCASTER_APPLICATION",
    metavar="APPLICATION",
    help="Bitcaster default Application",
)
@click.pass_context
def events(ctx: Context, project: str, application: str) -> None:
    FMT = "{:>5}: {:<20} {:<20} {:^8} {:^8} {}"

    try:
        ret = bitcaster_sdk.list_events(project, application)
        secho(TITLE.format("Application events"), fg="green")
        secho(FMT.format("#", "Name", "Slug", "active", "locked", "description"))
        for n, e in enumerate(ret, 1):
            if e["locked"]:
                cl = "red"
            elif e["active"]:
                cl = "green"
            else:  # e["active"]:
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
    except AuthenticationError:
        raise click.Abort("AuthenticationError")
    except EventNotFound:
        raise click.Abort("Project or Application not found")
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command(name="users", help="displays Organization's Users")
def list_users() -> None:
    FMT = "{:>5}: {:<30} {:<30} {:^8} {:^8}"
    try:
        ret = bitcaster_sdk.list_users()
        secho(TITLE.format("Organization users"), fg="green")
        secho(FMT.format("#", "Username", "Email", "active", "locked"))
        for n, e in enumerate(ret, 1):
            if e["locked"]:
                cl = "red"
            elif e["is_active"]:
                cl = "green"
            else:  # e["active"]:
                cl = "yellow"
            secho(
                FMT.format(
                    n,
                    e["username"],
                    e["email"],
                    "\u2713" if e["is_active"] else "",
                    "\u2713" if e["locked"] else "",
                ),
                fg=cl,
            )
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command(help="ping Bitcaster server")
def ping() -> None:
    try:
        ret = bitcaster_sdk.ping()
        echo(ret)
    except Exception as e:
        raise click.ClickException(str(e))


@click.argument("event")
@click.option(
    "--project", "-p", required=True, envvar="BITCASTER_PROJECT", metavar="PROJECT", help="Bitcaster default Project"
)
@click.option(
    "--application",
    "-a",
    required=True,
    envvar="BITCASTER_APPLICATION",
    metavar="APPLICATION",
    help="Bitcaster default Application",
)
@click.option("--context", "-c", "context", type=(str, str), multiple=True)
@click.option("--options", "-o", "options", type=(str, str), multiple=True)
@click.option("--verbosity", "-v", type=int, default=1, count=True)
@cli.command(help="trigger Application's Event")
@click.pass_context
def trigger(
    ctx: Context,
    project: str,
    application: str,
    verbosity: int,
    event: str,
    context: dict[str, str],
    options: dict[str, str],
) -> None:
    if verbosity > 1:
        echo(f"Context: {dict(context)}")
        echo(f"Options: {dict(options)}")
    try:
        ret = bitcaster_sdk.trigger(project, application, event, dict(context), dict(options))
        echo(ret)
    except Exception as e:
        raise click.ClickException(str(e))


if __name__ == "__main__":
    cli(obj={}, auto_envvar_prefix="BITCASTER")
