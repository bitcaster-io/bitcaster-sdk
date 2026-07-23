from __future__ import annotations

import http.server
import json
import os
import socketserver
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlparse

import click
from click import echo, secho

import bitcaster_sdk
from bitcaster_sdk import client, log
from bitcaster_sdk.exceptions import AuthenticationError, EventNotFoundError

if TYPE_CHECKING:
    from click.core import Context

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
            log.configure_api()
        else:
            log.configure_cli()

        bitcaster_sdk.init(bae, debug=debug)
    except Exception as e:
        raise click.ClickException(f"Failed to initialize Bitcaster. {e}") from None


@cli.command(name="projects", help="lists Projects")
@click.pass_context
def projects(ctx: Context) -> None:
    fmt = "{:>5}: {:<20} {:<20}"
    try:
        ret = bitcaster_sdk.list_projects()
        if ctx.obj["debug"]:
            secho(client.ctx.get().last_called_url)
        secho(TITLE.format("Project List"), fg="green")
        secho(fmt.format("#", "Slug", "Name"))
        for n, e in enumerate(ret, 1):
            secho(
                fmt.format(n, e["slug"], e["name"]),
            )
    except AuthenticationError:
        raise click.Abort("AuthenticationError") from None
    except EventNotFoundError:
        raise click.Abort("Project or Application not found") from None
    except Exception as e:
        raise click.ClickException(str(e)) from None


@cli.command(name="lists", help="lists Project's DistributionList")
@click.option("--project", "-p", required=True, envvar="BITCASTER_PROJECT", metavar="PROJECT", help="Bitcaster Project")
@click.pass_context
def lists(ctx: Context, project: str) -> None:
    fmt = "{:>5}: {:<20} {:<20}"
    try:
        ret = bitcaster_sdk.list_distribution_lists(project)
        if ctx.obj["debug"]:
            secho(client.ctx.get().last_called_url)
        secho(TITLE.format("Project Distribution Lists"), fg="green")
        secho(fmt.format("#", "Id", "Name"))
        for n, e in enumerate(ret, 1):
            secho(
                fmt.format(n, e["id"], e["name"]),
            )
    except AuthenticationError:
        raise click.Abort("AuthenticationError") from None
    except EventNotFoundError:
        raise click.Abort("Project or Application not found") from None
    except Exception as e:
        raise click.ClickException(str(e)) from None


@cli.command(name="applications", help="lists Project's DistributionList")
@click.option("--project", "-p", required=True, envvar="BITCASTER_PROJECT", metavar="PROJECT", help="Bitcaster Project")
@click.pass_context
def applications(ctx: Context, project: str) -> None:
    fmt = "{:>5}: {:<20} {:<20}"
    try:
        ret = bitcaster_sdk.list_applications(project)
        if ctx.obj["debug"]:
            secho(client.ctx.get().last_called_url)
        secho(TITLE.format("Project Distribution Lists"), fg="green")
        secho(fmt.format("#", "Slug", "Name"))
        for n, e in enumerate(ret, 1):
            secho(
                fmt.format(n, e["slug"], e["name"]),
            )
    except AuthenticationError:
        raise click.Abort("AuthenticationError") from None
    except EventNotFoundError:
        raise click.Abort("Project or Application not found") from None
    except Exception as e:
        raise click.ClickException(str(e)) from None


@cli.command(name="members", help="lists DistributionList Members")
@click.option("--distribution", "-d", required=True, metavar="DISTRIBUTION", help="Project distribution list id")
@click.option("--project", "-p", required=True, envvar="BITCASTER_PROJECT", metavar="PROJECT", help="Bitcaster Project")
@click.pass_context
def members(ctx: Context, project: str, distribution: str) -> None:
    fmt = "{:>3}: {:<4} {:<30} {:<30} {:<30}"
    try:
        ret = bitcaster_sdk.list_members(project, distribution)
        if ctx.obj["debug"]:
            secho(client.ctx.get().last_called_url)
        secho(TITLE.format("Distribution Lists Members"), fg="green")
        secho(fmt.format("#", "Id", "Address", "User", "Channel"))
        for n, e in enumerate(ret, 1):
            secho(
                fmt.format(n, e["id"], e["address"], e["user"], e["channel"]),
            )
    except AuthenticationError:
        raise click.Abort("AuthenticationError") from None
    except EventNotFoundError:
        raise click.Abort("Project or Application not found") from None
    except Exception as e:
        raise click.ClickException(str(e)) from None


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
    fmt = "{:>5}: {:<20} {:<20} {:^8} {:^8} {}"

    try:
        ret = bitcaster_sdk.list_events(project, application)
        secho(TITLE.format("Application events"), fg="green")
        secho(fmt.format("#", "Name", "Slug", "active", "locked", "description"))
        for n, e in enumerate(ret, 1):
            if e["locked"]:
                cl = "red"
            elif e["active"]:
                cl = "green"
            else:  # e["active"]:
                cl = "yellow"
            secho(
                fmt.format(
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
        raise click.Abort("AuthenticationError") from None
    except EventNotFoundError:
        raise click.Abort("Project or Application not found") from None
    except Exception as e:
        raise click.ClickException(str(e)) from None


@cli.command(help="ping Bitcaster server")
def ping() -> None:
    try:
        ret = bitcaster_sdk.ping()
        echo(ret)
    except Exception as e:
        raise click.ClickException(str(e)) from None


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
        raise click.ClickException(str(e)) from None


from . import users  # noqa


@cli.command(name="serve", help="Start a fake Bitcaster server for development. Dumps requests to stdout.")
@click.option("--port", "-p", default=9000, type=int, show_default=True, help="Port to listen on")
@click.option(
    "--response-code", "-c", "response_code", default=200, type=int, show_default=True,
    help="HTTP status code to return",
)
@click.option("--response-body", "-b", "response_body", default="{}", show_default=True, help="JSON body to return")
@click.pass_context
def serve(ctx: Context, port: int, response_code: int, response_body: str) -> None:
    try:
        body = json.loads(response_body)
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON in --response-body: {e}") from None

    class FakeBitcasterHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, fmt_str: str, *args: object) -> None:  # type: ignore[override]
            secho(fmt_str % args, fg="yellow")

        def _handle_request(self, method: str) -> None:
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)

            secho(f"\n{'='*60}", fg="cyan")
            secho(f"{method} {parsed.path}", fg="cyan", bold=True)
            if query:
                secho(f"Query: {query}", fg="magenta")
            secho("Headers:", fg="green", bold=True)

            for key, value in self.headers.items():
                secho(f"  {key}: {value}", fg="green")

            if content_length := int(self.headers.get("Content-Length", 0)):
                raw = self.rfile.read(content_length)
                body_text = raw.decode("utf-8")
                try:
                    body_json = json.loads(body_text)
                    secho(f"Body:\n{json.dumps(body_json, indent=2)}", fg="yellow")
                except json.JSONDecodeError:
                    secho(f"Body:\n{body_text}", fg="yellow")
            else:
                secho("Body: (empty)", fg="yellow")
            secho(f"{'='*60}\n", fg="cyan")

            self.send_response(response_code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(body).encode("utf-8"))

        def do_GET(self) -> None:  # type: ignore[override]
            self._handle_request("GET")

        def do_POST(self) -> None:  # type: ignore[override]
            self._handle_request("POST")

        def do_PATCH(self) -> None:  # type: ignore[override]
            self._handle_request("PATCH")

        def do_PUT(self) -> None:  # type: ignore[override]
            self._handle_request("PUT")

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True
        timeout = None

    try:
        with ReusableTCPServer(("0.0.0.0", port), FakeBitcasterHandler) as httpd:
            secho(f"Fake Bitcaster server listening on port {port}", fg="green", bold=True)
            secho("Press Ctrl+C to stop\n", fg="yellow")
            httpd.serve_forever()
    except OSError as e:
        raise click.ClickException(f"Failed to start server: {e}") from None


if __name__ == "__main__":
    cli(obj={}, auto_envvar_prefix="BITCASTER")
