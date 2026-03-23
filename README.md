# ha-config-mcp

CLI & MCP server for Home Assistant configuration management via WebSocket API.

Manage integrations, config flows, and Lovelace dashboards without touching the HA web UI.

> **Note:** This project is fully developed and maintained by Claude (Anthropic).
> Don't expect it to work out of the box, though it probably will.

## Install

```bash
# Nix (recommended)
nix run github:aster-void/ha-config-mcp -- --help
nix profile install github:aster-void/ha-config-mcp

# uvx / pipx
uvx ha-config-mcp --help
pipx install ha-config-mcp
```

## Authentication

Set a [Long-Lived Access Token](https://www.home-assistant.io/docs/authentication/#your-account-profile):

```bash
export HA_TOKEN="your-token"
# Or place it in ~/.config/ha-assist-token
```

## CLI Usage

The command is available as both `ha-config` and `ha-config-mcp`.

```bash
# List integrations
ha-config entries list
ha-config entries list -d music_assistant

# Add a new integration (interactive config flow)
ha-config flow start hue
# → returns flow_id and data_schema
ha-config flow step <flow_id> '{"host": "192.168.1.100"}'

# Edit an existing integration's settings
ha-config options start <entry_id>
ha-config options step <flow_id> '{"option": "value"}'

# Delete an integration
ha-config entries delete <entry_id>

# Lovelace dashboards
ha-config lovelace list
ha-config lovelace get
ha-config lovelace get my-dashboard
ha-config lovelace save dashboard.yaml my-dashboard
```

Output is YAML by default. Use `--json` for JSON output.

## MCP Server

```bash
# Start MCP server (stdio)
ha-config mcp

# Add to Claude Code
claude mcp add ha-config -- ha-config mcp
# or with nix
claude mcp add ha-config -- nix run github:aster-void/ha-config-mcp -- mcp
```

### MCP Tools

| Tool | Description |
|------|-------------|
| `config_entries_list(domain?)` | List installed integrations |
| `config_entries_get(entry_id)` | Get a single config entry |
| `config_entries_update(entry_id, ...)` | Update entry title/preferences |
| `config_entries_delete(entry_id)` | Delete an integration |
| `config_flow_start(domain)` | Start setup wizard |
| `config_flow_step(flow_id, user_input)` | Advance a setup step |
| `config_flow_abort(flow_id)` | Cancel a setup flow |
| `options_flow_start(entry_id)` | Start options editor |
| `options_flow_step(flow_id, user_input)` | Advance an options step |
| `lovelace_dashboards_list()` | List all dashboards |
| `lovelace_config_get(url_path?)` | Get dashboard config |
| `lovelace_config_save(config, url_path?)` | Save dashboard config (full overwrite) |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HA_URL` | `ws://localhost:8123/api/websocket` | HA WebSocket URL |
| `HA_TOKEN` | — | Long-Lived Access Token |
| `HA_OUTPUT` | `yaml` | Output format: `yaml` or `json` |

## License

MIT
