"""CLI interface for ha-config-mcp."""

import asyncio
import json
import sys

import click
import yaml

from . import ha


def _output(data, fmt):
    if fmt == "json":
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False), nl=False)


@click.group()
@click.option("--json", "fmt", flag_value="json", default=False, help="Output JSON instead of YAML")
@click.pass_context
def cli(ctx, fmt):
    """Home Assistant config management CLI."""
    ctx.ensure_object(dict)
    ctx.obj["fmt"] = fmt or "yaml"


# --- entries ---


@cli.group()
def entries():
    """Manage config entries (integrations)."""


@entries.command("list")
@click.option("--domain", "-d", default="", help="Filter by domain")
@click.pass_context
def entries_list(ctx, domain):
    """List installed integrations."""
    _output(asyncio.run(ha.config_entries_list(domain)), ctx.obj["fmt"])


@entries.command("get")
@click.argument("entry_id")
@click.pass_context
def entries_get(ctx, entry_id):
    """Get a config entry by ID."""
    result = asyncio.run(ha.config_entries_get(entry_id))
    _output(result or {"error": "not found"}, ctx.obj["fmt"])


@entries.command("delete")
@click.argument("entry_id")
@click.pass_context
def entries_delete(ctx, entry_id):
    """Delete an integration."""
    _output(asyncio.run(ha.config_entries_delete(entry_id)), ctx.obj["fmt"])


@entries.command("update")
@click.argument("entry_id")
@click.option("--title", default="")
@click.pass_context
def entries_update(ctx, entry_id, title):
    """Update a config entry."""
    kwargs = {}
    if title:
        kwargs["title"] = title
    _output(asyncio.run(ha.config_entries_update(entry_id, **kwargs)), ctx.obj["fmt"])


# --- flow ---


@cli.group()
def flow():
    """Config flow — add new integrations."""


@flow.command("start")
@click.argument("domain")
@click.pass_context
def flow_start(ctx, domain):
    """Start a config flow for a domain."""
    _output(asyncio.run(ha.config_flow_start(domain)), ctx.obj["fmt"])


@flow.command("step")
@click.argument("flow_id")
@click.argument("user_input", default="{}")
@click.pass_context
def flow_step(ctx, flow_id, user_input):
    """Advance a config flow step. USER_INPUT is a JSON object."""
    _output(asyncio.run(ha.config_flow_step(flow_id, json.loads(user_input))), ctx.obj["fmt"])


@flow.command("abort")
@click.argument("flow_id")
@click.pass_context
def flow_abort(ctx, flow_id):
    """Abort a config flow."""
    _output(asyncio.run(ha.config_flow_abort(flow_id)), ctx.obj["fmt"])


# --- options ---


@cli.group()
def options():
    """Options flow — edit existing integration settings."""


@options.command("start")
@click.argument("entry_id")
@click.pass_context
def options_start(ctx, entry_id):
    """Start an options flow."""
    _output(asyncio.run(ha.options_flow_start(entry_id)), ctx.obj["fmt"])


@options.command("step")
@click.argument("flow_id")
@click.argument("user_input", default="{}")
@click.pass_context
def options_step(ctx, flow_id, user_input):
    """Advance an options flow step. USER_INPUT is a JSON object."""
    _output(asyncio.run(ha.options_flow_step(flow_id, json.loads(user_input))), ctx.obj["fmt"])


# --- lovelace ---


@cli.group()
def lovelace():
    """Lovelace dashboard management."""


@lovelace.command("list")
@click.pass_context
def lovelace_list(ctx):
    """List all dashboards."""
    _output(asyncio.run(ha.lovelace_dashboards_list()), ctx.obj["fmt"])


@lovelace.command("get")
@click.argument("url_path", default="")
@click.pass_context
def lovelace_get(ctx, url_path):
    """Get dashboard config. Empty URL_PATH = default dashboard."""
    _output(asyncio.run(ha.lovelace_config_get(url_path)), ctx.obj["fmt"])


@lovelace.command("save")
@click.argument("config_file", type=click.File("r"), default="-")
@click.argument("url_path", default="")
@click.pass_context
def lovelace_save(ctx, config_file, url_path):
    """Save dashboard config from a file (or stdin). WARNING: overwrites entire config."""
    content = config_file.read()
    # accept both JSON and YAML input
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = yaml.safe_load(content)
    _output(asyncio.run(ha.lovelace_config_save(data, url_path)), ctx.obj["fmt"])


# --- mcp ---


@cli.command()
def mcp():
    """Start the MCP server (stdio transport)."""
    from .server import mcp as mcp_server
    mcp_server.run(transport="stdio")
