# Weather MCP Server Issue on Render - Solution

## Problem
When deploying to Render, you get this error:
```
[Errno 2] No such file or directory: 'uvx'
```

## Root Cause
- The weather MCP server uses `uvx` command (Python UV package manager)
- `uvx` is not available in Render's default Python environment
- Even though `uv` package can be installed via pip, the `uvx` command wrapper may not work properly

## Solutions

### Solution 1: Use NPX-based MCP Servers (Recommended for Render)

Instead of the weather server, use these reliable NPX-based alternatives:

```json
{
    "mcpServers": {
        "fetch": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-fetch"]
        }
    }
}
```

Then query the AI: "Use the fetch tool to get weather from wttr.in/London?format=j1"

### Solution 2: Use a Different Weather API

Use OpenWeather, WeatherAPI, or other services through the fetch server:

```json
{
    "mcpServers": {
        "fetch": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-fetch"]
        }
    }
}
```

Query: "Fetch weather data from api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY"

### Solution 3: Deploy Weather Server Separately

1. Deploy the weather MCP server as a separate service on a platform that supports `uvx`
2. Connect to it via HTTP/SSE transport instead of stdio

### Solution 4: Local Development Only

Keep the weather server for local development, but use NPX servers for production:

**Local (development):**
```json
{
    "mcpServers": {
        "weather": {
            "command": "uvx",
            "args": ["--from", "git+https://github.com/adhikasp/mcp-weather.git", "mcp-weather"],
            "env": {
                "ACCUWEATHER_API_KEY": "your-key"
            }
        }
    }
}
```

**Production (Render):**
```json
{
    "mcpServers": {
        "fetch": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-fetch"]
        }
    }
}
```

## Recommended MCP Servers for Render

These work reliably on Render's free tier:

```json
{
    "mcpServers": {
        "fetch": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-fetch"],
            "description": "Fetch web content, APIs, convert to markdown"
        },
        "memory": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"],
            "description": "Persistent memory for conversations"
        },
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
            "description": "File operations (read/write in /tmp)"
        },
        "git": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-git"],
            "description": "Git repository operations"
        }
    }
}
```

## Weather Data Alternatives

### 1. wttr.in (Free, No API Key)
```
Query: "Use fetch to get weather from https://wttr.in/London?format=j1"
```

### 2. Open-Meteo (Free, No API Key)
```
Query: "Fetch weather from https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&current_weather=true"
```

### 3. WeatherAPI (Free tier available)
```json
{
    "mcpServers": {
        "fetch": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-fetch"]
        }
    }
}
```
Query: "Fetch from http://api.weatherapi.com/v1/current.json?key=YOUR_KEY&q=London"

## Testing Locally

Before deploying, test your config:

```bash
cd "d:\Projects\MCP python\tests"
python test_render_config.py
```

## Deployment Checklist

- [ ] Replace `uvx` commands with `npx` commands
- [ ] Test configuration locally first
- [ ] Set OPENAI_API_KEY in Render dashboard
- [ ] Push changes to GitHub
- [ ] Deploy on Render
- [ ] Test with simple query first

## Summary

**For Render deployment:**
- ❌ Don't use: `uvx`-based MCP servers
- ✅ Do use: `npx`-based MCP servers
- ✅ Weather data: Use fetch server + free weather APIs
- ✅ Local development: Weather server works fine with your API key
