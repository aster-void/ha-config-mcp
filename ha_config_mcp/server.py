"""Home Assistant Config MCP Server — config entries & Lovelace dashboards via WebSocket API."""

import json
import os
from contextlib import asynccontextmanager

import websockets
import yaml
from mcp.server.fastmcp import FastMCP

HA_URL = os.environ.get("HA_URL", "ws://localhost:8123/api/websocket")
HA_OUTPUT = os.environ.get("HA_OUTPUT", "yaml")  # "yaml" or "json"
HA_TOKEN = os.environ.get("HA_TOKEN", "")

mcp = FastMCP(
    "ha-config",
    instructions=(
        "Home Assistant configuration management server. "
        "Provides tools for managing integrations (config entries), "
        "config flows, options flows, and Lovelace dashboards."
    ),
)

_msg_id = 0


def _next_id() -> int:
    global _msg_id
    _msg_id += 1
    return _msg_id


@asynccontextmanager
async def _ha_ws():
    """Connect and authenticate to HA WebSocket API."""
    token = HA_TOKEN or _read_token_file()
    async with websockets.connect(HA_URL) as ws:
        # auth_required
        msg = json.loads(await ws.recv())
        if msg.get("type") != "auth_required":
            raise RuntimeError(f"Unexpected message: {msg}")
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        msg = json.loads(await ws.recv())
        if msg.get("type") != "auth_ok":
            raise RuntimeError(f"Auth failed: {msg}")
        yield ws


def _read_token_file() -> str:
    path = os.path.expanduser("~/.config/ha-assist-token")
    try:
        return open(path).read().strip()
    except FileNotFoundError:
        raise RuntimeError(f"No HA_TOKEN env var and {path} not found")


def _fmt(data) -> str:
    if HA_OUTPUT == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)
    return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)


async def _send(ws, msg_type: str, **kwargs) -> dict:
    mid = _next_id()
    payload = {"id": mid, "type": msg_type, **kwargs}
    await ws.send(json.dumps(payload))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == mid:
            if not resp.get("success", True):
                raise RuntimeError(f"HA error: {resp.get('error', resp)}")
            return resp.get("result", resp)


# --- Config Entries ---


@mcp.tool()
async def config_entries_list(domain: str = "") -> str:
    """List installed integrations (config entries). Optionally filter by domain (e.g. 'music_assistant')."""
    async with _ha_ws() as ws:
        kwargs = {}
        if domain:
            kwargs["domain"] = domain
        result = await _send(ws, "config_entries/get", **kwargs)
        return _fmt(result)


@mcp.tool()
async def config_entries_get(entry_id: str) -> str:
    """Get a single config entry by ID."""
    async with _ha_ws() as ws:
        result = await _send(ws, "config_entries/get")
        for entry in result:
            if entry.get("entry_id") == entry_id:
                return json.dumps(entry, ensure_ascii=False, indent=2)
        return _fmt({"error": "not found"})


@mcp.tool()
async def config_entries_delete(entry_id: str) -> str:
    """Delete an integration (config entry) by ID."""
    async with _ha_ws() as ws:
        result = await _send(ws, "config_entries/delete", entry_id=entry_id)
        return _fmt(result)


@mcp.tool()
async def config_entries_update(
    entry_id: str, title: str = "", pref_disable_new_entities: bool | None = None, pref_disable_polling: bool | None = None
) -> str:
    """Update a config entry's title or preferences."""
    async with _ha_ws() as ws:
        kwargs: dict = {"entry_id": entry_id}
        if title:
            kwargs["title"] = title
        if pref_disable_new_entities is not None:
            kwargs["pref_disable_new_entities"] = pref_disable_new_entities
        if pref_disable_polling is not None:
            kwargs["pref_disable_polling"] = pref_disable_polling
        result = await _send(ws, "config_entries/update", **kwargs)
        return _fmt(result)


# --- Config Flow (add new integration) ---


@mcp.tool()
async def config_flow_start(domain: str) -> str:
    """Start a config flow to add a new integration. Returns the first step with data_schema describing required fields."""
    async with _ha_ws() as ws:
        result = await _send(ws, "config_entries/flow", handler=[domain, None])
        return _fmt(result)


@mcp.tool()
async def config_flow_step(flow_id: str, user_input: str = "{}") -> str:
    """Advance a config flow step. user_input is a JSON object matching the data_schema from the previous step. Pass '{}' for steps with no required input."""
    data = json.loads(user_input)
    async with _ha_ws() as ws:
        result = await _send(ws, "config_entries/flow", flow_id=flow_id, user_input=data)
        return _fmt(result)


@mcp.tool()
async def config_flow_abort(flow_id: str) -> str:
    """Abort an in-progress config flow."""
    async with _ha_ws() as ws:
        result = await _send(ws, "config_entries/flow/abort", flow_id=flow_id)
        return _fmt(result)


# --- Options Flow (edit existing integration settings) ---


@mcp.tool()
async def options_flow_start(entry_id: str) -> str:
    """Start an options flow to change settings of an existing integration. Returns the first step with data_schema."""
    async with _ha_ws() as ws:
        result = await _send(ws, "config_entries/options/flow", handler=entry_id)
        return _fmt(result)


@mcp.tool()
async def options_flow_step(flow_id: str, user_input: str = "{}") -> str:
    """Advance an options flow step. user_input is a JSON object matching the data_schema from the previous step."""
    data = json.loads(user_input)
    async with _ha_ws() as ws:
        result = await _send(ws, "config_entries/options/flow", flow_id=flow_id, user_input=data)
        return _fmt(result)


# --- Lovelace Dashboards ---


@mcp.tool()
async def lovelace_dashboards_list() -> str:
    """List all Lovelace dashboards."""
    async with _ha_ws() as ws:
        result = await _send(ws, "lovelace/dashboards/list")
        return _fmt(result)


@mcp.tool()
async def lovelace_config_get(url_path: str = "") -> str:
    """Get the full Lovelace config for a dashboard. Empty url_path = default dashboard."""
    async with _ha_ws() as ws:
        kwargs = {}
        if url_path:
            kwargs["url_path"] = url_path
        result = await _send(ws, "lovelace/config", **kwargs)
        return _fmt(result)


@mcp.tool()
async def lovelace_config_save(config: str, url_path: str = "") -> str:
    """Save a full Lovelace config (JSON string). Empty url_path = default dashboard. WARNING: this overwrites the entire dashboard config."""
    data = json.loads(config)
    async with _ha_ws() as ws:
        kwargs: dict = {"config": data}
        if url_path:
            kwargs["url_path"] = url_path
        result = await _send(ws, "lovelace/config/save", **kwargs)
        return _fmt(result if result else {"success": True})


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
