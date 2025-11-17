# MCP Tool Lister - Test Suite

This directory contains all test files for the MCP Tool Lister application.

## Test Files

### Configuration Files
- `test_config.json` - Basic configuration test
- `test_config_fetch.json` - Fetch server configuration
- `test_websearch.json` - Web search server configuration
- `test_docker.json` - Docker server configuration
- `test_git.json` - Git server configuration
- `test_memory.json` - Memory server configuration
- `test_multi.json` - Multiple servers configuration
- `test_uv.json` - UV server configuration
- `test_comprehensive.json` - Comprehensive multi-server configuration

### Test Scripts
- `test_simple.py` - Simple test with basic configuration
- `test_all.py` - Test all configured servers
- `test_websearch.py` - Web search MCP + OpenAI integration tests
- `test_fetch.py` - Fetch server tests
- `test_docker.py` - Docker MCP tests
- `test_docker_native.py` - Native Docker implementation tests
- `test_docker_advanced.py` - Advanced Docker tests
- `test_git.py` - Git server tests
- `test_memory.py` - Memory server tests
- `test_multi.py` - Multiple servers test
- `test_uv.py` - UV server tests
- `test_comprehensive.py` - Comprehensive test suite

## Running Tests

### Run All Tests
```powershell
cd tests
python test_all.py
```

### Run Specific Test
```powershell
cd tests
python test_websearch.py
```

### Web Search + OpenAI Tests
The web search tests require an OpenAI API key:
```powershell
$env:OPENAI_API_KEY = "your-api-key-here"
cd tests
python test_websearch.py
```

## Test Requirements
All tests use the parent directory's `requirements.txt`. Ensure you have installed all dependencies:
```powershell
pip install -r ../requirements.txt
```

## Notes
- Tests may require specific MCP servers to be available
- Some tests require environment variables (API keys, etc.)
- Tests will automatically connect to and disconnect from MCP servers
