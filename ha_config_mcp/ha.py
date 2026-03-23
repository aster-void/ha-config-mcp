"""Home Assistant WebSocket API client."""

import json
import os
from contextlib import asynccontextmanager

import websockets

HA_URL = os.environ.get("HA_URL", "ws://localhost:8123/api/websocket")
HA_TOKEN = os.environ.get("HA_TOKEN", "")

_msg_id = 0


def _next_id() -> int:
    global _msg_id
    _msg_id += 1
    return _msg_id


def _read_token_file() -> str:
    path = os.path.expanduser("~/.config/ha-assist-token")
    try:
        return open(path).read().strip()
    except FileNotFoundError:
        raise RuntimeError(f"No HA_TOKEN env var and {path} not found")


@asynccontextmanager
async def connect():
    """Connect and authenticate to HA WebSocket API."""
    token = HA_TOKEN or _read_token_file()
    async with websockets.connect(HA_URL) as ws:
        msg = json.loads(await ws.recv())
        if msg.get("type") != "auth_required":
            raise RuntimeError(f"Unexpected message: {msg}")
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        msg = json.loads(await ws.recv())
        if msg.get("type") != "auth_ok":
            raise RuntimeError(f"Auth failed: {msg}")
        yield ws


async def send(ws, msg_type: str, **kwargs) -> dict:
    mid = _next_id()
    payload = {"id": mid, "type": msg_type, **kwargs}
    await ws.send(json.dumps(payload))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == mid:
            if not resp.get("success", True):
                raise RuntimeError(f"HA error: {resp.get('error', resp)}")
            return resp.get("result", resp)


# --- High-level operations ---


async def config_entries_list(domain: str = "") -> list:
    async with connect() as ws:
        kwargs = {}
        if domain:
            kwargs["domain"] = domain
        return await send(ws, "config_entries/get", **kwargs)


async def config_entries_get(entry_id: str) -> dict | None:
    async with connect() as ws:
        result = await send(ws, "config_entries/get")
        for entry in result:
            if entry.get("entry_id") == entry_id:
                return entry
        return None


async def config_entries_delete(entry_id: str) -> dict:
    async with connect() as ws:
        return await send(ws, "config_entries/delete", entry_id=entry_id)


async def config_entries_update(entry_id: str, **kwargs) -> dict:
    async with connect() as ws:
        return await send(ws, "config_entries/update", entry_id=entry_id, **kwargs)


async def config_flow_start(domain: str) -> dict:
    async with connect() as ws:
        return await send(ws, "config_entries/flow", handler=[domain, None])


async def config_flow_step(flow_id: str, user_input: dict | None = None) -> dict:
    async with connect() as ws:
        return await send(ws, "config_entries/flow", flow_id=flow_id, user_input=user_input or {})


async def config_flow_abort(flow_id: str) -> dict:
    async with connect() as ws:
        return await send(ws, "config_entries/flow/abort", flow_id=flow_id)


async def options_flow_start(entry_id: str) -> dict:
    async with connect() as ws:
        return await send(ws, "config_entries/options/flow", handler=entry_id)


async def options_flow_step(flow_id: str, user_input: dict | None = None) -> dict:
    async with connect() as ws:
        return await send(ws, "config_entries/options/flow", flow_id=flow_id, user_input=user_input or {})


async def lovelace_dashboards_list() -> list:
    async with connect() as ws:
        return await send(ws, "lovelace/dashboards/list")


async def lovelace_config_get(url_path: str = "") -> dict:
    async with connect() as ws:
        kwargs = {}
        if url_path:
            kwargs["url_path"] = url_path
        return await send(ws, "lovelace/config", **kwargs)


async def lovelace_config_save(config: dict, url_path: str = "") -> dict:
    async with connect() as ws:
        kwargs: dict = {"config": config}
        if url_path:
            kwargs["url_path"] = url_path
        result = await send(ws, "lovelace/config/save", **kwargs)
        return result if result else {"success": True}
