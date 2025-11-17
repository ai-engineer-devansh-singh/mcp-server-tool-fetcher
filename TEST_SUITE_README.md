# MCP Server Test Suite

Comprehensive test suite for MCP (Model Context Protocol) servers with support for Docker containerization and UV-based Python servers.

## 📋 Test Files Overview

### Basic Tests

#### `test_simple.py`
- **Purpose**: Tests basic MCP functionality with Playwright
- **Command**: 
  ```powershell
  cd 'd:\Projects\MCP python' ; C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe test_simple.py
  ```
- **Config**: `test_config.json`
- **Servers**: Playwright browser automation

#### `test_fetch.py`
- **Purpose**: Tests fetch MCP server for web content retrieval
- **Command**: 
  ```powershell
  cd 'd:\Projects\MCP python' ; C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe test_fetch.py
  ```
- **Config**: `test_config_fetch.json`
- **Servers**: Fetch server (web content)

#### `test_multi.py`
- **Purpose**: Tests multiple MCP servers simultaneously
- **Command**: 
  ```powershell
  cd 'd:\Projects\MCP python' ; C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe test_multi.py
  ```
- **Config**: `test_multi.json`
- **Servers**: Multiple servers (time, playwright, everything)

### Specialized Tests

#### `test_docker.py` ✅
- **Purpose**: Tests Docker containerization MCP server
- **Command**: 
  ```powershell
  cd 'd:\Projects\MCP python' ; C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe test_docker.py
  ```
- **Config**: `test_docker.json`
- **Servers**: `containerization-assist-mcp` (Docker operations)
- **Tools Available**: 12 tools including:
  - Repository analysis
  - Dockerfile generation and validation
  - Docker image building and scanning
  - Kubernetes manifest generation
  - Container deployment and verification

#### `test_uv.py` ✅
- **Purpose**: Tests UV-based Python MCP servers
- **Command**: 
  ```powershell
  cd 'd:\Projects\MCP python' ; C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe test_uv.py 2>$null
  ```
- **Config**: `test_uv.json`
- **Servers**: 
  - `mcp-server-time` (timezone operations)
  - `mcp-server-sqlite` (database operations)
- **Requirements**: UV/UVX must be installed
- **Tools Available**: 8 tools total
  - Time: 2 tools (get_current_time, convert_time)
  - SQLite: 6 tools (read_query, write_query, create_table, list_tables, describe_table, append_insight)

#### `test_comprehensive.py` ✅
- **Purpose**: Comprehensive test with multiple server types
- **Command**: 
  ```powershell
  cd 'd:\Projects\MCP python' ; C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe test_comprehensive.py 2>$null
  ```
- **Config**: `test_comprehensive.json`
- **Servers**: 
  - Docker (containerization-assist-mcp)
  - Time (mcp-server-time)
  - Playwright (@playwright/mcp)
- **Tools Available**: 36 tools total across all servers

## 🔧 Configuration Files

### Docker Configuration (`test_docker.json`)
```json
{
  "mcpServers": {
    "docker": {
      "command": "npx",
      "args": ["-y", "containerization-assist-mcp"]
    }
  }
}
```

### UV Configuration (`test_uv.json`)
```json
{
  "mcpServers": {
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time", "--local-timezone=UTC"]
    },
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "test.db"]
    }
  }
}
```

### Comprehensive Configuration (`test_comprehensive.json`)
```json
{
  "mcpServers": {
    "docker": {
      "command": "npx",
      "args": ["-y", "containerization-assist-mcp"]
    },
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time", "--local-timezone=UTC"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

## 📦 Requirements

### System Requirements
- Python 3.13+
- Node.js and npm/npx
- UV/UVX for Python-based servers

### Python Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `mcp-use` - MCP client library
- `rich` - Terminal formatting
- `asyncio` - Async operations

### Optional Requirements
- Docker Desktop (for containerization-assist-mcp full functionality)

## 🚀 Usage

### Quick Test
Run any test with:
```powershell
cd 'd:\Projects\MCP python'
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe <test_file>.py
```

### Suppress Warnings
For cleaner output, suppress stderr warnings:
```powershell
cd 'd:\Projects\MCP python'
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe <test_file>.py 2>$null
```

## 🐛 Known Issues & Solutions

### UV Server Cleanup Warnings
**Issue**: UV-based servers show cleanup warnings about cancel scopes.

**Solution**: These warnings are harmless and have been suppressed in the test files. To avoid seeing them:
```powershell
python test_uv.py 2>$null
```

### Docker Server Connection
**Issue**: Docker server may fail if Docker Desktop isn't running.

**Solution**: Start Docker Desktop before running docker tests.

### Fetch Server Issues
**Issue**: Fetch server sometimes fails to connect.

**Solution**: This is a known issue with the server package. Use alternative web scraping MCP servers if needed.

## 📊 Test Results

### Docker Test (`test_docker.py`)
- ✅ Status: Working
- ✅ Servers Connected: 1
- ✅ Tools Available: 12
- ✅ Key Features: Docker image building, Kubernetes deployment, security scanning

### UV Test (`test_uv.py`)
- ✅ Status: Working
- ✅ Servers Connected: 2
- ✅ Tools Available: 8
- ⚠️ Minor cleanup warnings (suppressed)

### Comprehensive Test (`test_comprehensive.py`)
- ✅ Status: Working
- ✅ Servers Connected: 3
- ✅ Tools Available: 36
- ✅ Tests: Multi-server coordination

## 🔍 Features

### Automatic Command Resolution
The system automatically resolves commands for different platforms:
- `uvx` → Finds UV executable in Python Scripts
- `npx` → Finds Node.js npm executable
- Platform-specific paths (Windows/Linux/Mac)

### Error Handling
- Graceful connection failures
- Detailed error messages
- Automatic cleanup of resources
- Suppression of known harmless warnings

### Rich Terminal Output
- Color-coded status messages
- Formatted tables for tool listings
- Progress indicators
- Clear summaries

## 📝 Adding New Tests

To create a new test:

1. **Create config JSON**:
```json
{
  "mcpServers": {
    "your-server": {
      "command": "npx",
      "args": ["-y", "your-mcp-package"]
    }
  }
}
```

2. **Create test file**:
```python
import asyncio
from rich.console import Console
from config import ConfigParser
from mcp_client import MCPToolLister

console = Console()

async def main():
    with open("your_config.json", "r") as f:
        config_json = f.read()
    
    parser = ConfigParser()
    servers = parser.parse_config(config_json, auto_resolve=True)
    
    lister = MCPToolLister()
    try:
        all_tools = await lister.list_all_tools(servers)
        lister.display_tools(all_tools)
    finally:
        await lister.close_all_connections()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🎯 Next Steps

- Add more MCP server tests (GitHub, GitLab, Kubernetes, etc.)
- Implement integration tests with actual tool execution
- Add performance benchmarks
- Create automated test suite with CI/CD

## 📚 Documentation

- [MCP Server Guide](./MCP_SERVER_GUIDE.md)
- [MCP Browser README](./MCP_BROWSER_README.md)
- [MCP Tools List](./MCP_TOOLS_COMPREHENSIVE_LIST.txt)
- [Project README](./README.md)

## 🤝 Contributing

Feel free to add more test files for different MCP servers following the established patterns.
