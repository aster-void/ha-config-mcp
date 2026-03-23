"""Home Assistant Config MCP Server — config entries & Lovelace dashboards via WebSocket API."""

import json
import os

import yaml
from mcp.server.fastmcp import FastMCP

from . import ha

HA_OUTPUT = os.environ.get("HA_OUTPUT", "yaml")

mcp = FastMCP(
    "ha-config",
    instructions=(
        "Home Assistant configuration management server. "
        "Provides tools for managing integrations (config entries), "
        "config flows, options flows, and Lovelace dashboards."
    ),
)


def _fmt(data) -> str:
    if HA_OUTPUT == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)
    return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)


@mcp.tool()
async def config_entries_list(domain: str = "") -> str:
    """List installed integrations (config entries). Optionally filter by domain (e.g. 'music_assistant')."""
    return _fmt(await ha.config_entries_list(domain))


@mcp.tool()
async def config_entries_get(entry_id: str) -> str:
    """Get a single config entry by ID."""
    result = await ha.config_entries_get(entry_id)
    return _fmt(result or {"error": "not found"})


@mcp.tool()
async def config_entries_delete(entry_id: str) -> str:
    """Delete an integration (config entry) by ID."""
    return _fmt(await ha.config_entries_delete(entry_id))


@mcp.tool()
async def config_entries_update(
    entry_id: str, title: str = "", pref_disable_new_entities: bool | None = None, pref_disable_polling: bool | None = None
) -> str:
    """Update a config entry's title or preferences."""
    kwargs = {}
    if title:
        kwargs["title"] = title
    if pref_disable_new_entities is not None:
        kwargs["pref_disable_new_entities"] = pref_disable_new_entities
    if pref_disable_polling is not None:
        kwargs["pref_disable_polling"] = pref_disable_polling
    return _fmt(await ha.config_entries_update(entry_id, **kwargs))


@mcp.tool()
async def config_flow_start(domain: str) -> str:
    """Start a config flow to add a new integration. Returns the first step with data_schema describing required fields."""
    return _fmt(await ha.config_flow_start(domain))


@mcp.tool()
async def config_flow_step(flow_id: str, user_input: str = "{}") -> str:
    """Advance a config flow step. user_input is a JSON object matching the data_schema from the previous step. Pass '{}' for steps with no required input."""
    return _fmt(await ha.config_flow_step(flow_id, json.loads(user_input)))


@mcp.tool()
async def config_flow_abort(flow_id: str) -> str:
    """Abort an in-progress config flow."""
    return _fmt(await ha.config_flow_abort(flow_id))


@mcp.tool()
async def options_flow_start(entry_id: str) -> str:
    """Start an options flow to change settings of an existing integration. Returns the first step with data_schema."""
    return _fmt(await ha.options_flow_start(entry_id))


@mcp.tool()
async def options_flow_step(flow_id: str, user_input: str = "{}") -> str:
    """Advance an options flow step. user_input is a JSON object matching the data_schema from the previous step."""
    return _fmt(await ha.options_flow_step(flow_id, json.loads(user_input)))


@mcp.tool()
async def lovelace_dashboards_list() -> str:
    """List all Lovelace dashboards."""
    return _fmt(await ha.lovelace_dashboards_list())


@mcp.tool()
async def lovelace_config_get(url_path: str = "") -> str:
    """Get the full Lovelace config for a dashboard. Empty url_path = default dashboard."""
    return _fmt(await ha.lovelace_config_get(url_path))


@mcp.tool()
async def lovelace_config_save(config: str, url_path: str = "") -> str:
    """Save a full Lovelace config (JSON string). Empty url_path = default dashboard. WARNING: this overwrites the entire dashboard config."""
    return _fmt(await ha.lovelace_config_save(json.loads(config), url_path))


def main():
    mcp.run(transport="stdio")
