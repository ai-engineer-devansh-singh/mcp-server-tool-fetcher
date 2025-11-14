# MCP Server Time - Alternative Configuration Options

## Issue
The `uvx` command is not found because `uv` is not installed on your system.

## Solutions

### Option 1: Install uv (Recommended)
Install uv to use uvx command:

**PowerShell (Admin):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installing, restart your terminal and use:
```json
{
  "mcpServers": {
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time", "--local-timezone=America/New_York"]
    }
  }
}
```

### Option 2: Use Python directly
Install the package globally and run it with Python:

```powershell
pip install mcp-server-time
```

Then use this config:
```json
{
  "mcpServers": {
    "time": {
      "command": "python",
      "args": ["-m", "mcp_server_time", "--local-timezone=America/New_York"]
    }
  }
}
```

### Option 3: Use npx with Python MCP servers
If the MCP server is available via npm:

```json
{
  "mcpServers": {
    "time": {
      "command": "npx",
      "args": ["-y", "mcp-server-time", "--local-timezone=America/New_York"]
    }
  }
}
```

## Testing Different Servers

### Playwright (Works with npx - Node.js)
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

### Fetch (Works with npx - Node.js)
```json
{
  "mcpServers": {
    "fetch": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-fetch"]
    }
  }
}
```

### Filesystem (Works with npx - Node.js)
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "D:/Projects"]
    }
  }
}
```

## Why uvx?
- `uvx` is like `npx` but for Python packages
- It automatically installs and runs Python packages in isolated environments
- Part of the `uv` tool: https://docs.astral.sh/uv/
