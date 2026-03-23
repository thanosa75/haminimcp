# Home Assistant MCP Server

MCP server for Home Assistant light and calendar control via stdio. This server allows you to integrate Home Assistant with Claude and other MCP clients for intelligent home automation.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
  - [Option 1: Using `uvx` (Recommended)](#option-1-using-uvx-recommended)
  - [Option 2: Local Development Installation](#option-2-local-development-installation)
  - [Option 3: Traditional pip Installation](#option-3-traditional-pip-installation)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [MCP Client Configuration](#mcp-client-configuration)
- [Usage](#usage)
- [Available Tools](#available-tools)
- [Troubleshooting](#troubleshooting)

## Requirements

- **Python**: 3.11 or later
- **Home Assistant**: An accessible Home Assistant instance with API token
- **Internet**: Network connectivity to your Home Assistant instance

## Installation

### Option 1: Using `uvx` (Recommended)

`uvx` is a command-line tool runner that automatically manages dependencies and isolated Python environments. This is the **recommended approach** for MCP servers.

#### Install `uv` (if not already installed)

On macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On Windows (PowerShell):
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Running with `uvx`

```bash
uvx --from git+https://github.com/thanosa75/haminimcp homeassistant_mcp
```

This command will:
1. Automatically download and cache the `homeassistant-mcp` package
2. Create an isolated environment with all dependencies
3. Run the server immediately

### Option 2: Local Development Installation

For development or when running directly from the repository:

1. **Clone or navigate to the repository**
   ```bash
   cd /path/to/homeassistant-mcp
   ```

2. **Create a virtual environment** (optional but recommended)
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in editable mode**
   ```bash
   pip install -e .
   ```

4. **Run the server**
   ```bash
   python -m homeassistant_mcp
   ```

### Option 3: Traditional pip Installation

For production deployments without `uvx`:

```bash
pip install homeassistant-mcp
homeassistant_mcp
```

## Configuration

### Environment Variables

Before running the server, set the following environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `HA_BASE_URL` | The base URL of your Home Assistant instance | `http://localhost:8123` or `https://ha.example.com` |
| `HA_TOKEN` | Long-lived access token for Home Assistant API authentication | `eyJhbGc...` (see instructions below) |

#### Getting Your Home Assistant Token

1. Go to your Home Assistant instance at `http://<your-ha-ip>:8123` (or your domain)
2. Click on your user profile icon (bottom left)
3. Scroll down to **"Long-Lived Access Tokens"**
4. Click **"Create Token"**
5. Enter a name (e.g., "MCP Server")
6. Copy the generated token (you won't be able to view it again)

#### Setting Environment Variables

**Linux/macOS (bash/zsh):**
```bash
export HA_BASE_URL="http://localhost:8123"
export HA_TOKEN="your_long_lived_token_here"
```

**Linux/macOS (persistent in `~/.bashrc` or `~/.zshrc`):**
```bash
echo 'export HA_BASE_URL="http://localhost:8123"' >> ~/.bashrc
echo 'export HA_TOKEN="your_long_lived_token_here"' >> ~/.bashrc
source ~/.bashrc
```

**Windows (PowerShell):**
```powershell
$env:HA_BASE_URL = "http://localhost:8123"
$env:HA_TOKEN = "your_long_lived_token_here"
```

**Windows (persistent via System Environment Variables):**
1. Press `Win + R`, type `sysdm.cpl`, and press Enter
2. Click the **"Environment Variables..."** button
3. Click **"New..."** under "User variables"
4. Add `HA_BASE_URL` and `HA_TOKEN` with your values

**Using a `.env` file (with python-dotenv):**
```bash
# .env file in your project directory
HA_BASE_URL=http://localhost:8123
HA_TOKEN=your_long_lived_token_here
```

Then load it before running:
```bash
python -c "from dotenv import load_dotenv; load_dotenv()" && homeassistant_mcp
```

### MCP Client Configuration

The MCP server communicates via stdio (standard input/output). To use it with Claude Desktop or other MCP clients, add the server to your MCP client configuration file.

#### Claude Desktop Configuration

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Linux**: `~/.config/Claude/claude_desktop_config.json`

Add the following configuration:

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "uvx",
      "args": [
        "-n",
        "--from",
        "git+https://github.com/thanosa75/haminimcp",
        "homeassistant_mcp"
      ],
      "env": {
        "HA_BASE_URL": "http://localhost:8123",
        "HA_TOKEN": "your_long_lived_token_here"
      }
    }
  }
}
```

**Note:** The `-n` flag ensures the package is installed in a virtual environment.

#### Generic MCP Client Configuration (mcp.json)

If using a custom MCP client, use the following `mcp.json` format:

```json
{
  "version": "1.0",
  "mcpServers": {
    "homeassistant": {
      "description": "Home Assistant light and calendar control",
      "command": "uvx",
      "args": [
        "-n",
        "--from",
        "git+https://github.com/thanosa75/haminimcp",
        "homeassistant_mcp"
      ],
      "env": {
        "HA_BASE_URL": "http://localhost:8123",
        "HA_TOKEN": "your_long_lived_token_here"
      }
    }
  }
}
```

**Environment Variables in `mcp.json`:**

| Variable | Description | Default |
|----------|-------------|---------|
| `HA_BASE_URL` | Home Assistant instance URL | (required) |
| `HA_TOKEN` | Long-lived access token | (required) |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |


## Usage

### Quick Start

1. **Set environment variables** (see [Environment Variables](#environment-variables) section)

2. **Run using `uvx`** (easiest):
   ```bash
   uvx homeassistant-mcp
   ```

3. **Or run locally**:
   ```bash
   pip install -e .
   python -m homeassistant_mcp
   ```

The server will start listening on stdio and be ready to receive MCP requests from your client.

### Verification

To verify the server is running correctly:

1. The server should start without errors
2. Environment variables should be properly loaded
3. Connection to Home Assistant should be established
4. Your MCP client should be able to list available tools

## Available Tools

The following tools are available through this MCP server:

### Light Control

- **`ha_list_lights`**: List all lights in Home Assistant
- **`ha_get_light`**: Get state and attributes of a single light
- **`ha_operate_light`**: Turn on/off/toggle a light with optional attributes (brightness, color, etc.)
- **`ha_set_light_brightness`**: Set light brightness as a percentage (0-100)

### Calendar Access

- **`ha_list_calendars`**: List all calendars in Home Assistant
- **`ha_get_calendar_events`**: Get events from a calendar within a date range
- **`ha_get_today_events`**: Get today's events from one or all calendars

### Example Tool Usage

In your MCP client (e.g., Claude):

```
Turn on the bedroom light at 50% brightness.

→ Use ha_operate_light with entity_id="light.bedroom", service="turn_on", brightness=127 (50% of 255)

What meetings do I have today?

→ Use ha_get_today_events to fetch events from all calendars

List all my lights.

→ Use ha_list_lights to retrieve all available lights
```

## Troubleshooting

### Server Fails to Start

**Error: `HA_BASE_URL or HA_TOKEN not set`**
- Verify that both environment variables are properly set
- Check: `echo $HA_BASE_URL` and `echo $HA_TOKEN`
- On Windows: `echo %HA_BASE_URL%` and `echo %HA_TOKEN%`

**Error: `Connection refused` or `Cannot connect to Home Assistant`**
- Verify `HA_BASE_URL` is correct and accessible
- Check that Home Assistant is running
- If using HTTPS, ensure SSL certificates are valid
- Check firewall rules if accessing remotely

### Token Issues

**Error: `Invalid token` or `Unauthorized`**
- Generate a new long-lived access token (see [Getting Your Home Assistant Token](#getting-your-home-assistant-token))
- Ensure the token has not expired
- Verify no trailing spaces in the token value

### `uvx` Issues

**Error: `uvx: command not found`**
- Install `uv` first: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Or use traditional pip installation

**Error: `Failed to fetch package`**
- Check internet connectivity
- Verify package name is correct: `homeassistant-mcp`
- Try specifying a version: `uvx homeassistant-mcp==0.1.0`

### Logging

The server logs to both console and rotating log files in `/workspace/logs/`:

- **Console output**: Real-time logging at INFO level
- **Log files**: Detailed rotating logs with timestamp
- **Set log level**: Export `LOG_LEVEL=DEBUG` for verbose output

```bash
export LOG_LEVEL=DEBUG
uvx homeassistant-mcp
```

### Support

For additional help:
1. Check Home Assistant documentation: https://www.home-assistant.io/
2. Review MCP specification: https://modelcontextprotocol.io/
3. Open an issue on the project repository
