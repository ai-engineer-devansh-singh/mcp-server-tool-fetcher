"""
Simple integration test for smart-query API.
Run this to quickly test the smart-query endpoint.
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

# Test configurations
PLAYWRIGHT_CONFIG = json.dumps({
    "mcpServers": {
        "playwright": {
            "command": "npx",
            "args": ["@playwright/mcp@latest"]
        }
    }
})

POPULATION_CANADA_CONFIG = json.dumps({
    "mcpServers": {
        "population-of-canada": {
            "command": "node",
            "args": [
                "--input-type=module",
                "-e",
                "// Minimal test server\nlet buffer = '';\nprocess.stdin.on('data', async (chunk) => {\n  buffer += chunk;\n  const lines = buffer.split('\\n');\n  buffer = lines.pop() || '';\n  for (const line of lines) {\n    if (!line.trim()) continue;\n    try {\n      const msg = JSON.parse(line);\n      if (msg.id === null || msg.id === undefined) continue;\n      let result = null;\n      if (msg.method === 'initialize') {\n        result = { protocolVersion: '2024-11-05', capabilities: { tools: {} }, serverInfo: { name: 'Test Agent', version: '1.0.0' } };\n      } else if (msg.method === 'tools/list') {\n        result = { tools: [{ name: 'population-of-canada', description: 'Population data', inputSchema: { type: 'object', properties: { query: { type: 'string' } }, required: ['query'] } }] };\n      } else if (msg.method === 'tools/call') {\n        result = { content: [{ type: 'text', text: 'Test response: Canada population is approximately 39 million' }] };\n      }\n      if (result) process.stdout.write(JSON.stringify({ jsonrpc: '2.0', id: msg.id, result: result }) + '\\n');\n    } catch (err) {}\n  }\n});\nprocess.stdin.setEncoding('utf8');\nprocess.stdin.resume();\nconsole.error('Test server ready');"
            ]
        }
    }
})


def print_test(name):
    """Print test header."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print('='*60)


def print_result(response, execution_time):
    """Print test result."""
    print(f"Status Code: {response.status_code}")
    print(f"Execution Time: {execution_time:.3f}s")
    data = response.json()
    print(f"Success: {data.get('success')}")
    if data.get('success'):
        print(f"Response: {data.get('response', '')[:200]}...")
        print(f"Server: {data.get('server')}")
        print(f"Tool: {data.get('tool')}")
        if 'arguments_used' in data:
            print(f"Arguments: {data.get('arguments_used')}")
    else:
        print(f"Error: {data.get('error')}")
    print()


def test_validation():
    """Test input validation."""
    print_test("Validation - Missing configString")
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/smart-query", json={
        'serverName': 'test',
        'toolName': 'test',
        'query': 'test'
    })
    elapsed = time.time() - start
    
    data = response.json()
    assert response.status_code == 400
    assert data['success'] is False
    assert 'configString' in data['error']
    print(f"✓ Passed - Error: {data['error']}")


def test_direct_mode():
    """Test direct execution mode."""
    print_test("Direct Mode - Population Tool")
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/smart-query", json={
        'configString': POPULATION_CANADA_CONFIG,
        'serverName': 'population-of-canada',
        'toolName': 'population-of-canada',
        'query': 'What is the population of Canada?',
        'useAI': False
    })
    elapsed = time.time() - start
    
    print_result(response, elapsed)
    
    data = response.json()
    if data['success']:
        print("✓ Test Passed")
    else:
        print(f"✗ Test Failed: {data.get('error')}")


def test_ai_mode():
    """Test AI-assisted mode."""
    print_test("AI Mode - Population Tool")
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/smart-query", json={
        'configString': POPULATION_CANADA_CONFIG,
        'serverName': 'population-of-canada',
        'toolName': 'population-of-canada',
        'query': 'Tell me about Canada population',
        'useAI': True
    })
    elapsed = time.time() - start
    
    print_result(response, elapsed)
    
    data = response.json()
    if data['success']:
        print("✓ Test Passed")
    else:
        print(f"✗ Test Failed: {data.get('error')}")
        if 'OpenAI' in data.get('error', ''):
            print("  Note: OpenAI API key may not be configured")


def test_invalid_server():
    """Test with invalid server name."""
    print_test("Error Handling - Invalid Server")
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/smart-query", json={
        'configString': PLAYWRIGHT_CONFIG,
        'serverName': 'nonexistent-server',
        'toolName': 'some-tool',
        'query': 'Test query',
        'useAI': False
    })
    elapsed = time.time() - start
    
    print_result(response, elapsed)
    
    data = response.json()
    assert data['success'] is False
    assert 'not found in configuration' in data['error']
    print("✓ Test Passed - Error handled correctly")


def test_invalid_tool():
    """Test with invalid tool name."""
    print_test("Error Handling - Invalid Tool")
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/smart-query", json={
        'configString': PLAYWRIGHT_CONFIG,
        'serverName': 'playwright',
        'toolName': 'nonexistent-tool',
        'query': 'Test query',
        'useAI': False
    })
    elapsed = time.time() - start
    
    print_result(response, elapsed)
    
    data = response.json()
    assert data['success'] is False
    assert 'not found on server' in data['error']
    print("✓ Test Passed - Error handled correctly")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("SMART-QUERY API INTEGRATION TESTS")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Make sure the Flask app is running on {BASE_URL}")
    print()
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/api/stats", timeout=2)
        print("✓ Server is running\n")
    except requests.exceptions.RequestException:
        print("✗ Server is not running!")
        print(f"Please start the server: python app.py")
        return
    
    tests = [
        ("Validation", test_validation),
        ("Direct Mode", test_direct_mode),
        ("AI Mode", test_ai_mode),
        ("Invalid Server", test_invalid_server),
        ("Invalid Tool", test_invalid_tool),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n✗ Test '{name}' failed with error: {str(e)}\n")
            failed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
