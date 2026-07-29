import json
from json import JSONDecodeError

import click
from click import echo, secho

import bitcaster_sdk

from . import client
from .__cli__ import TITLE, cli, json_output_option
from .exceptions import ValidationError
from .helpers import JsonUpdateMode


@cli.group()
def users() -> None:
    pass


@users.command(name="list", help="displays Organization's Users")
@json_output_option
@click.pass_context
def list_(ctx: click.Context, json_output: bool = False) -> None:
    ctx.obj["json"] = ctx.obj.get("json", False) or json_output
    try:
        ret = bitcaster_sdk.list_users()
        if ctx.obj["json"]:
            echo(json.dumps(ret, indent=2))
            return
        fmt = "{:>5}: {:<30} {:<30} {:^8} {:^8}"
        secho(TITLE.format("Organization users"), fg="green")
        secho(fmt.format("#", "Username", "Email", "active", "locked"))
        for n, e in enumerate(ret, 1):
            if e["locked"]:
                cl = "red"
            elif e["is_active"]:
                cl = "green"
            else:  # e["active"]:
                cl = "yellow"
            secho(
                fmt.format(
                    n,
                    e["username"],
                    e["email"],
                    "\u2713" if e["is_active"] else "",
                    "\u2713" if e["locked"] else "",
                ),
                fg=cl,
            )
    except Exception as e:
        raise click.ClickException(str(e)) from None


@users.command(name="add", help="add new user to the current organization")
@click.argument("email")
@click.option("--first-name", "-f", default="")
@click.option("--last-name", "-l", default="")
@click.option("--custom", "-c", default="{}")
@json_output_option
@click.pass_context
def add_(
    ctx: click.Context, email: str, first_name: str, last_name: str, custom: str, json_output: bool = False
) -> None:
    ctx.obj["json"] = ctx.obj.get("json", False) or json_output
    try:
        c = json.loads(custom or "{}")
        res = client.ctx.get().add_user(email, first_name, last_name, c)
        if ctx.obj["json"]:
            echo(json.dumps(res, indent=2))
        else:
            echo(res)
    except Exception:
        raise click.ClickException("Invalid custom fields value. It must be a valid json string") from None


@users.command(name="update", help="add new user to the current organization")
@click.argument("email")
@click.option("--first-name", "-f", default="")
@click.option("--last-name", "-l", default="")
@click.option("--custom", "-c", default="{}")
@click.option("--mode", "-m", default=JsonUpdateMode.IGNORE, type=click.Choice(JsonUpdateMode.choices()))
@json_output_option
@click.pass_context
def update_(
    ctx: click.Context, email: str, first_name: str, last_name: str, custom: str, mode: str, json_output: bool = False
) -> None:
    ctx.obj["json"] = ctx.obj.get("json", False) or json_output
    try:
        c = json.loads(custom or "{}")
        res = client.ctx.get().update_user(email, first_name, last_name, custom_fields=c, mode=mode)
        if ctx.obj["json"]:
            echo(json.dumps(res, indent=2))
        else:
            echo(res)
    except ValidationError as e:
        click.secho(str(e), fg="red")
        click.get_current_context().exit(1)
    except JSONDecodeError:
        raise click.ClickException("Invalid custom fields value. It must be a valid json string") from None
