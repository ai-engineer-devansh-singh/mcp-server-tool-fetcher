# MCP Servers Browser

A beautiful web interface to browse, search, and configure Model Context Protocol (MCP) servers.

## Features

- 📱 **Browse all MCP servers** - View 20+ popular MCP servers
- 🔍 **Search functionality** - Find servers by name or description
- 🏷️ **Category filtering** - Filter servers by category (Core, Development, Database, etc.)
- ✅ **Multi-select** - Select multiple servers to configure
- 📋 **Generate config** - Automatically generate Claude Desktop configuration
- 💾 **Download JSON** - Export configuration as JSON file
- 📊 **Statistics** - View total servers, categories, and selection count

## Installation

1. Install required dependencies:
```bash
pip install flask
```

2. Run the application:
```bash
python app_mcp_browser.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Browse Servers
- The main page displays all available MCP servers in a card layout
- Each card shows the server name, description, command, and required environment variables

### Search
- Use the search box to find servers by name or description
- Results update in real-time as you type

### Filter by Category
- Click on category buttons to filter servers
- Categories include: Core, Development, Database, Search, Communication, and more

### Select Servers
- Click the checkbox on any server card to select it
- Selected servers are highlighted
- The selection count updates automatically

### Generate Configuration
1. Select one or more servers
2. Click "Generate Config" button
3. View the generated Claude Desktop configuration
4. Click "Copy to Clipboard" to copy the configuration

### Download Configuration
1. Select one or more servers
2. Click "Download JSON" button
3. A `claude_desktop_config.json` file will be downloaded
4. Place this file in your Claude Desktop configuration folder:
   - Windows: `%APPDATA%\Claude\`
   - macOS: `~/Library/Application Support/Claude/`
   - Linux: `~/.config/Claude/`

## Available Servers

The application includes 20+ pre-configured MCP servers:

### Core
- Filesystem - File operations
- Memory - Persistent storage

### Development
- GitHub - Repository management
- Git - Version control
- Sequential Thinking - Problem-solving

### Database
- PostgreSQL - SQL database
- SQLite - Embedded database
- Qdrant - Vector database
- Snowflake - Data warehouse

### Search & Web
- Brave Search - Web search
- Fetch - Web content
- Everything - Windows file search
- Puppeteer - Browser automation

### Communication
- Slack - Workspace integration

### Cloud Storage
- Google Drive - File management
- AWS KB - Knowledge base

### Infrastructure
- Docker - Container management
- Kubernetes - Orchestration
- Cloudflare - CDN management

### Monitoring
- Sentry - Error tracking
- Axiom - Log analysis

### Media
- YouTube Transcript - Video transcripts

### Productivity
- Raycast - Launcher integration

## Configuration Format

The generated configuration follows the Claude Desktop format:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-name"],
      "env": {
        "API_KEY": "your-key-here"
      }
    }
  }
}
```

## Adding More Servers

To add more servers, edit `mcp_servers_config.py` and add entries to the `SERVERS` or `PYTHON_SERVERS` dictionaries:

```python
"server-id": {
    "name": "Server Name",
    "description": "Server description",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-name"],
    "category": "Category",
    "transport": "stdio",
    "env": {  # Optional
        "API_KEY": "<your-key>"
    }
}
```

## API Endpoints

The Flask app provides several API endpoints:

- `GET /api/servers` - Get all servers
- `GET /api/categories` - Get all categories
- `GET /api/servers/category/<category>` - Get servers by category
- `GET /api/server/<server_id>` - Get specific server config
- `GET /api/search?q=<query>` - Search servers
- `POST /api/config/generate` - Generate configuration
- `POST /api/config/download` - Download configuration

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Custom CSS with gradient design
- **Icons**: Unicode emoji

## Screenshot

The interface features:
- Purple gradient header
- Responsive card layout
- Real-time search
- Category filtering
- Dark code preview
- Statistics dashboard

## License

MIT License - Feel free to use and modify!

## Contributing

To contribute new servers or features:
1. Fork the repository
2. Add your servers to `mcp_servers_config.py`
3. Test the configuration
4. Submit a pull request

## Support

For issues or questions:
- Check the MCP documentation: https://modelcontextprotocol.io/
- Review the server list: https://github.com/modelcontextprotocol/servers

## Notes

- Environment variables shown in angle brackets (`<your-key>`) must be replaced with actual values
- Some servers require API keys or authentication
- Test your configuration before deploying to production
- The app runs in debug mode by default (disable for production)
