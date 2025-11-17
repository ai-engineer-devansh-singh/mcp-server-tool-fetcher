# MCP Tool Lister

A Python application that connects to MCP (Model Context Protocol) servers and lists all available tools. Users can paste their MCP configuration and instantly see all tools from configured servers.

## Features

- 🔌 Connect to multiple MCP servers simultaneously
- 📋 List all tools with detailed information (name, description, parameters)
- 🎨 Beautiful CLI interface with Rich formatting
- ✅ Configuration validation
- 🔍 Detailed parameter information for each tool

## Prerequisites

- Python 3.8 or higher
- Node.js and npm (for running MCP servers like playwright, fetch, etc.)

## Installation

1. Clone or download this project

2. Create a virtual environment (recommended):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

## Project Structure

```
MCP python/
├── app.py                 # Flask web application
├── app_mcp_browser.py    # MCP browser application
├── main.py               # CLI interactive tool
├── config.py             # Configuration parser
├── mcp_client.py         # MCP client wrapper
├── mcp_servers_config.py # Server configurations
├── requirements.txt      # Python dependencies
├── static/               # Web UI assets
├── templates/            # HTML templates
├── tests/                # Test suite (see tests/README.md)
└── README.md            # This file
```

## Usage

### Web Application

Run the Flask web application:
```powershell
python app.py
```
Then open http://localhost:5000 in your browser.

### Quick Test

Run the simple test with the included example config:
```powershell
cd tests
python test_simple.py
```

### Interactive Mode

1. Run the application:
```powershell
python main.py
```

2. When prompted, paste your MCP configuration in JSON format. For example:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest"
      ]
    },
    "fetch": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-fetch"
      ]
    }
  }
}
```

3. Press Enter twice after pasting your configuration

4. The application will:
   - Parse your configuration
   - Connect to each MCP server
   - List all available tools with details

## Configuration Format

Your MCP configuration should follow this format:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "command-to-run",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

### Fields:
- `command` (required): The command to execute the MCP server
- `args` (optional): Array of command-line arguments
- `env` (optional): Environment variables to pass to the server

## Examples

### Playwright MCP Server
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

### Multiple Servers
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/directory"]
    },
    "fetch": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-fetch"]
    }
  }
}
```

## Output

The application displays:
- Connection status for each server
- Number of tools found per server
- Detailed table for each server showing:
  - Tool name
  - Description
  - Parameters (with types and required/optional status)

## Resources

- [MCP Use Library](https://github.com/mcp-use/mcp-use)
- [MCP Market](https://mcpmarket.com/) - Find more MCP servers
- [Playwright MCP Server](https://mcpmarket.com/server/playwright-5)

## Additional Features

### Web Search + OpenAI Integration
See `WEB_SEARCH_README.md` for details on using web search MCP servers with OpenAI API.

### MCP Browser
See `MCP_BROWSER_README.md` for details on the browser-based interface.

### MCP Server Guide
See `MCP_SERVER_GUIDE.md` for comprehensive information about MCP servers.

## Testing

All test files are located in the `tests/` directory. See `tests/README.md` for details on running tests.

## Deployment

### Deploy to Render

This application is ready for easy deployment to Render.

#### Quick Deploy (Using Blueprint)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Blueprint"
4. Connect your GitHub repository
5. Render will automatically detect `render.yaml` and configure your service
6. Click "Apply" to deploy

#### Manual Deploy

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: mcp-tool-lister (or your choice)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - **Plan**: Free
6. Add Environment Variables (if needed):
   - `OPENAI_API_KEY`: Your OpenAI API key (optional, for AI features)
7. Click "Create Web Service"

#### Environment Variables

Optional environment variables you can set on Render:
- `OPENAI_API_KEY`: For OpenAI integration features
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4-turbo-preview)

#### After Deployment

Your application will be available at: `https://your-service-name.onrender.com`

**Note**: The free tier on Render may spin down after inactivity. The first request after inactivity may take 30-60 seconds to respond.

## Troubleshooting

### Connection Issues
- Ensure Node.js and npm are installed and in your PATH
- Some MCP servers require additional setup or API keys
- Check that the command and args in your configuration are correct

### Module Not Found
- Make sure you've installed all requirements: `pip install -r requirements.txt`
- Activate your virtual environment if using one

## License

MIT License - Feel free to use and modify this project