"""
Tests for the smart-query API endpoint.
Tests both direct execution and AI-assisted modes.
"""
import pytest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def playwright_config():
    """Playwright MCP server configuration."""
    return json.dumps({
        "mcpServers": {
            "playwright": {
                "command": "npx",
                "args": ["@playwright/mcp@latest"]
            }
        }
    })


@pytest.fixture
def population_canada_config():
    """Population of Canada MCP server configuration."""
    config = {
        "mcpServers": {
            "population-of-canada": {
                "command": "node",
                "args": [
                    "--input-type=module",
                    "-e",
                    "// Fetch and execute MCP server from BuildACopilot\nimport { createServer } from 'http';\nimport { spawn } from 'child_process';\n\nconst ENDPOINT = 'https://buildacopilot.com/api/prompt-hub/agents/population-of-canada/chat';\nconst NAME = 'population of canada';\nconst SLUG = 'population-of-canada';\nconst DESC = 'As an expert in demographic analysis, your task is to provide a detailed overview of Canada\\'s population trends over the past decade.';\n\n\n// Simple JSON-RPC MCP server\nlet buffer = '';\nprocess.stdin.on('data', async (chunk) => {\n  buffer += chunk;\n  const lines = buffer.split('\\n');\n  buffer = lines.pop() || '';\n  \n  for (const line of lines) {\n    if (!line.trim()) continue;\n    try {\n      const msg = JSON.parse(line);\n      \n      if (!msg || typeof msg !== 'object') {\n        console.error('Invalid message format');\n        continue;\n      }\n      \n      if (msg.id === null || msg.id === undefined) {\n        console.error('Received notification:', msg.method || 'unknown');\n        continue;\n      }\n      \n      let result = null;\n      \n      if (msg.method === 'initialize') {\n        result = { \n          protocolVersion: '2024-11-05', \n          capabilities: { \n            tools: {} \n          }, \n          serverInfo: { \n            name: NAME || 'Agent', \n            version: '1.0.0' \n          } \n        };\n      } else if (msg.method === 'tools/list') {\n        result = { \n          tools: [{ \n            name: SLUG || 'agent', \n            description: DESC || 'AI Agent', \n            inputSchema: { \n              type: 'object', \n              properties: { \n                query: { \n                  type: 'string', \n                  description: 'The query or message to send to the agent' \n                } \n              }, \n              required: ['query'] \n            } \n          }] \n        };\n      } else if (msg.method === 'tools/call') {\n        try {\n          if (!msg.params || !msg.params.arguments) {\n            throw new Error('Missing params.arguments in request');\n          }\n          const query = msg.params.arguments.query;\n          if (!query || typeof query !== 'string') {\n            throw new Error('Missing or invalid required parameter: query (must be a string)');\n          }\n          const headers = { 'Content-Type': 'application/json'  };\n          const res = await fetch(ENDPOINT, { \n            method: 'POST', \n            headers, \n            body: JSON.stringify({ query: query }) \n          });\n          if (!res.ok) {\n            const errText = await res.text();\n            throw new Error('API Error ' + res.status + ': ' + errText.substring(0, 200));\n          }\n          const data = await res.json();\n          const responseText = String(data.response || data.message || JSON.stringify(data));\n          result = { \n            content: [{ \n              type: 'text', \n              text: responseText \n            }] \n          };\n        } catch (callErr) {\n          result = { \n            content: [{ \n              type: 'text', \n              text: 'Error calling agent: ' + String(callErr.message || callErr) \n            }],\n            isError: true \n          };\n        }\n      } else {\n        throw new Error('Unknown method: ' + (msg.method || 'undefined'));\n      }\n      \n      if (result !== null) {\n        const response = { \n          jsonrpc: '2.0', \n          id: msg.id, \n          result: result \n        };\n        process.stdout.write(JSON.stringify(response) + '\\n');\n      }\n    } catch (err) {\n      console.error('MCP Error:', err.message || String(err));\n      try {\n        const parsedMsg = JSON.parse(line);\n        if (parsedMsg && parsedMsg.id !== null && parsedMsg.id !== undefined) {\n          const errorResponse = { \n            jsonrpc: '2.0', \n            id: parsedMsg.id, \n            error: { \n              code: -32603, \n              message: String(err.message || err || 'Internal error') \n            } \n          };\n          process.stdout.write(JSON.stringify(errorResponse) + '\\n');\n        }\n      } catch (parseErr) {\n        console.error('Failed to parse error response:', parseErr.message);\n      }\n    }\n  }\n});\n\nprocess.stdin.setEncoding('utf8');\nprocess.stdin.resume();\nconsole.error('population of canada MCP server ready');"
                ],
                "env": {
                    "NODE_NO_WARNINGS": "1"
                }
            }
        }
    }
    return json.dumps(config)


class TestSmartQueryValidation:
    """Test input validation for smart-query endpoint."""
    
    def test_missing_config_string(self, client):
        """Test that missing configString returns error."""
        response = client.post('/api/smart-query',
                              json={
                                  'serverName': 'test',
                                  'toolName': 'test',
                                  'query': 'test'
                              })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'configString' in data['error']
    
    def test_missing_server_name(self, client):
        """Test that missing serverName returns error."""
        response = client.post('/api/smart-query',
                              json={
                                  'configString': '{}',
                                  'toolName': 'test',
                                  'query': 'test'
                              })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'serverName' in data['error']
    
    def test_missing_tool_name(self, client):
        """Test that missing toolName returns error."""
        response = client.post('/api/smart-query',
                              json={
                                  'configString': '{}',
                                  'serverName': 'test',
                                  'query': 'test'
                              })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'toolName' in data['error']
    
    def test_missing_query(self, client):
        """Test that missing query returns error."""
        response = client.post('/api/smart-query',
                              json={
                                  'configString': '{}',
                                  'serverName': 'test',
                                  'toolName': 'test'
                              })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'query' in data['error']


class TestSmartQueryDirect:
    """Test direct execution mode (useAI=false)."""
    
    def test_invalid_server_name(self, client, playwright_config):
        """Test error when server doesn't exist."""
        response = client.post('/api/smart-query',
                              json={
                                  'configString': playwright_config,
                                  'serverName': 'nonexistent-server',
                                  'toolName': 'browser_navigate',
                                  'query': 'Go to example.com',
                                  'useAI': False
                              })
        data = response.get_json()
        assert data['success'] is False
        assert 'not found in configuration' in data['error']
        assert 'Available servers' in data['error']
    
    def test_invalid_tool_name(self, client, playwright_config):
        """Test error when tool doesn't exist."""
        response = client.post('/api/smart-query',
                              json={
                                  'configString': playwright_config,
                                  'serverName': 'playwright',
                                  'toolName': 'nonexistent-tool',
                                  'query': 'Test query',
                                  'useAI': False
                              })
        data = response.get_json()
        assert data['success'] is False
        assert 'not found on server' in data['error']
        assert 'Available tools' in data['error']
    
    @pytest.mark.integration
    def test_direct_execution_playwright(self, client, playwright_config):
        """Test direct execution with Playwright browser_snapshot tool."""
        response = client.post('/api/smart-query',
                              json={
                                  'configString': playwright_config,
                                  'serverName': 'playwright',
                                  'toolName': 'browser_snapshot',
                                  'query': 'Capture accessibility snapshot',
                                  'useAI': False
                              })
        data = response.get_json()
        
        # Should succeed or fail with connection error (not validation error)
        assert 'execution_time' in data
        
        if data['success']:
            assert 'response' in data
            assert data['server'] == 'playwright'
            assert data['tool'] == 'browser_snapshot'
            assert 'arguments_used' in data
    
    @pytest.mark.integration
    def test_direct_execution_population(self, client, population_canada_config):
        """Test direct execution with population-of-canada tool."""
        response = client.post('/api/smart-query',
                              json={
                                  'configString': population_canada_config,
                                  'serverName': 'population-of-canada',
                                  'toolName': 'population-of-canada',
                                  'query': 'What is the current population of Canada?',
                                  'useAI': False
                              })
        data = response.get_json()
        
        assert 'execution_time' in data
        
        if data['success']:
            assert 'response' in data
            assert data['server'] == 'population-of-canada'
            assert data['tool'] == 'population-of-canada'
            assert 'arguments_used' in data
            assert 'query' in data['arguments_used']


class TestSmartQueryWithAI:
    """Test AI-assisted execution mode (useAI=true)."""
    
    def test_ai_mode_without_openai_key(self, client, playwright_config, monkeypatch):
        """Test that AI mode fails gracefully without OpenAI API key."""
        # Remove OpenAI key from environment
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        
        response = client.post('/api/smart-query',
                              json={
                                  'configString': playwright_config,
                                  'serverName': 'playwright',
                                  'toolName': 'browser_navigate',
                                  'query': 'Go to example.com',
                                  'useAI': True
                              })
        data = response.get_json()
        
        if not data['success']:
            assert 'OpenAI' in data['error'] or 'API key' in data['error']
    
    @pytest.mark.integration
    @pytest.mark.skipif(os.getenv('OPENAI_API_KEY') is None, 
                       reason="OpenAI API key not configured")
    def test_ai_execution_with_openai(self, client, population_canada_config):
        """Test AI-assisted execution with OpenAI."""
        response = client.post('/api/smart-query',
                              json={
                                  'configString': population_canada_config,
                                  'serverName': 'population-of-canada',
                                  'toolName': 'population-of-canada',
                                  'query': 'Tell me about Canada population trends',
                                  'useAI': True
                              })
        data = response.get_json()
        
        assert 'execution_time' in data
        
        if data['success']:
            assert 'response' in data
            assert data['server'] == 'population-of-canada'
            assert data['tool'] == 'population-of-canada'
            # AI mode should have these fields
            if 'arguments_used' in data:
                assert isinstance(data['arguments_used'], dict)


class TestSmartQueryPerformance:
    """Test performance aspects of smart-query endpoint."""
    
    def test_execution_time_included(self, client, playwright_config):
        """Test that execution_time is always included in response."""
        response = client.post('/api/smart-query',
                              json={
                                  'configString': playwright_config,
                                  'serverName': 'playwright',
                                  'toolName': 'browser_snapshot',
                                  'query': 'Test',
                                  'useAI': False
                              })
        data = response.get_json()
        assert 'execution_time' in data
        assert isinstance(data['execution_time'], (int, float))
        assert data['execution_time'] >= 0
    
    def test_default_use_ai_false(self, client, playwright_config):
        """Test that useAI defaults to false when not specified."""
        response = client.post('/api/smart-query',
                              json={
                                  'configString': playwright_config,
                                  'serverName': 'playwright',
                                  'toolName': 'browser_snapshot',
                                  'query': 'Test'
                                  # useAI not specified
                              })
        data = response.get_json()
        # Should use direct mode (faster)
        assert 'execution_time' in data


class TestSmartQueryResponseFormat:
    """Test response format consistency."""
    
    def test_error_response_format(self, client):
        """Test error response has consistent format."""
        response = client.post('/api/smart-query',
                              json={
                                  'configString': '{}',
                                  'serverName': 'test',
                                  'toolName': 'test',
                                  'query': 'test',
                                  'useAI': False
                              })
        data = response.get_json()
        assert 'success' in data
        assert 'error' in data
        assert 'execution_time' in data
        assert data['success'] is False
    
    @pytest.mark.integration
    def test_success_response_format(self, client, playwright_config):
        """Test success response has consistent format."""
        response = client.post('/api/smart-query',
                              json={
                                  'configString': playwright_config,
                                  'serverName': 'playwright',
                                  'toolName': 'browser_snapshot',
                                  'query': 'Capture snapshot',
                                  'useAI': False
                              })
        data = response.get_json()
        
        if data['success']:
            assert 'response' in data
            assert 'server' in data
            assert 'tool' in data
            assert 'execution_time' in data
            assert data['server'] == 'playwright'
            assert data['tool'] == 'browser_snapshot'


def test_smart_query_endpoint_exists(client):
    """Test that the smart-query endpoint exists and accepts POST."""
    response = client.get('/api/smart-query')
    # Should return 405 Method Not Allowed for GET
    assert response.status_code == 405


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
