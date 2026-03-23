# ha-config-mcp

MCP server for Home Assistant configuration management via WebSocket API.

> **Note:** This project is fully developed and maintained by Claude (Anthropic).
> Don't expect it to work out of the box, though it probably will.
> Don't expect it to be well-optimized and well-maintained.

## Features

- **Config Entries** — list, get, update, delete integrations
- **Config Flow** — add new integrations (step-by-step wizard via MCP)
- **Options Flow** — edit existing integration settings
- **Lovelace Dashboards** — list, get, and save dashboard configs

## Usage

```bash
# Set HA token
export HA_TOKEN="your-long-lived-access-token"
# Or place it in ~/.config/ha-assist-token

# Run with nix
nix run github:aster-void/ha-config-mcp
# or install it to system (user-wide)
nix profile add github:aster-void/ha-config-mcp

# add to Claude Code
claude mcp add ha-config -- nix run github:aster-void/ha-config-mcp
# or use [mcptools](https://github.com/f/mcptools)
mcp tools nix run github:aster-void/ha-config-mcp
# or use [mcp-cli](https://github.com/philschmid/mcp-cli)
cat > mcp_servers.json << EOF
{
  "mcpServers": {
    "ha-config": {
      "command": "nix",
      "args": ["run" "github:aster-void/ha-config-mcp"]
    }
  }
}
EOF
mcp-cli info ha-config
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HA_URL` | `ws://localhost:8123/api/websocket` | HA WebSocket URL |
| `HA_TOKEN` | — | Long-Lived Access Token (falls back to `~/.config/ha-assist-token`) |

## Tools

### Config Entries
- `config_entries_list(domain?)` — List installed integrations
- `config_entries_get(entry_id)` — Get a single config entry
- `config_entries_update(entry_id, title?, ...)` — Update entry preferences
- `config_entries_delete(entry_id)` — Delete an integration

### Config Flow (add new integration)
- `config_flow_start(domain)` — Start setup wizard, returns first step with `data_schema`
- `config_flow_step(flow_id, user_input)` — Submit step data, returns next step or completion
- `config_flow_abort(flow_id)` — Cancel an in-progress flow

### Options Flow (edit integration settings)
- `options_flow_start(entry_id)` — Start options wizard
- `options_flow_step(flow_id, user_input)` — Submit step data

### Lovelace Dashboards
- `lovelace_dashboards_list()` — List all dashboards
- `lovelace_config_get(url_path?)` — Get full dashboard config
- `lovelace_config_save(config, url_path?)` — Save full dashboard config

## Flags
