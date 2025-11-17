# Web Search MCP + OpenAI Integration

## Overview

This integration demonstrates how to use the **open-websearch** MCP server with OpenAI API to create powerful AI-powered search and content generation capabilities.

## Features

✅ **Web Search MCP Integration** - Connect to open-websearch MCP server  
✅ **Multiple Search Engines** - Support for DuckDuckGo, Bing, and Exa  
✅ **OpenAI API Integration** - Generate content based on search results  
✅ **Function Calling** - Use OpenAI's function calling with MCP tools  
✅ **AI-Powered Summaries** - Automatically summarize search results  

## Setup

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- `mcp-use` - MCP client library
- `openai` - OpenAI API client
- `rich` - Beautiful terminal output
- Other required packages

### 2. Install open-websearch MCP Server

The MCP server will be automatically installed when you run the test (via `npx`), but you can pre-install it:

```powershell
npm install -g open-websearch
```

### 3. Set OpenAI API Key

**Option A: Environment Variable (Recommended)**
```powershell
# PowerShell
$env:OPENAI_API_KEY = "your-api-key-here"

# Or permanently in PowerShell profile
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your-api-key-here', 'User')
```

**Option B: .env File**
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

### 4. Verify Configuration

Check that your `test_websearch.json` is configured correctly:

```json
{
  "mcpServers": {
    "web-search": {
      "command": "npx",
      "args": ["open-websearch@latest"],
      "env": {
        "MODE": "stdio",
        "DEFAULT_SEARCH_ENGINE": "duckduckgo",
        "ALLOWED_SEARCH_ENGINES": "duckduckgo,bing,exa"
      }
    }
  }
}
```

## Usage

### Run All Tests

```powershell
cd 'd:\Projects\MCP python'
python test_websearch.py
```

This runs three comprehensive tests:

#### Test 1: List Available Tools
- Connects to web-search MCP server
- Lists all available search tools
- Displays tool parameters and descriptions

#### Test 2: Search + AI Content Generation
- Performs web searches using MCP tools
- Retrieves search results from multiple sources
- Generates AI-powered summaries using OpenAI

#### Test 3: OpenAI Function Calling
- Demonstrates OpenAI function calling with MCP tools
- Lets OpenAI autonomously decide when to search
- Synthesizes search results into coherent responses

## How It Works

### Architecture

```
User Query
    ↓
OpenAI API (decides to search)
    ↓
MCP Client → open-websearch MCP Server
    ↓
Search Engine (DuckDuckGo/Bing/Exa)
    ↓
Search Results
    ↓
OpenAI API (generates summary)
    ↓
Final Response to User
```

### Code Flow

1. **Initialize MCP Client**
   ```python
   ws_ai = WebSearchWithAI()
   await ws_ai.initialize(servers)
   ```

2. **Call Search Tool**
   ```python
   result = await ws_ai.call_tool("search", {
       "query": "AI developments 2025",
       "engine": "duckduckgo",
       "max_results": 5
   })
   ```

3. **Generate AI Content**
   ```python
   response = await openai_client.chat.completions.create(
       model="gpt-4-turbo-preview",
       messages=[...],
       tools=openai_tools,
       tool_choice="auto"
   )
   ```

## Available Search Engines

### DuckDuckGo (Default)
- Privacy-focused
- No API key required
- Good general results

### Bing
- Microsoft's search engine
- Comprehensive results
- May require API key for production

### Exa
- AI-powered semantic search
- Best for technical queries
- Requires API key

## Example Use Cases

### 1. Research Assistant
Search for current information and generate summaries:
```python
await ws_ai.search_and_generate(
    "latest Python 3.13 features",
    "duckduckgo"
)
```

### 2. News Aggregator
Find and summarize recent news:
```python
await ws_ai.search_and_generate(
    "AI developments November 2025",
    "duckduckgo"
)
```

### 3. Technical Documentation Finder
Search for technical docs and create guides:
```python
await ws_ai.search_and_generate(
    "MCP protocol implementation guide",
    "exa"
)
```

### 4. Autonomous AI Agent
Let OpenAI decide when to search:
```python
# OpenAI will automatically call search tools when needed
response = await openai_client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[{"role": "user", "content": "What's new in AI?"}],
    tools=openai_tools,
    tool_choice="auto"
)
```

## Configuration Options

### Search Parameters

```python
{
    "query": str,           # Search query
    "engine": str,          # Search engine (duckduckgo/bing/exa)
    "max_results": int,     # Max results to return (default: 10)
    "time_range": str,      # Optional: day/week/month/year
    "safe_search": bool,    # Optional: Enable safe search
    "region": str           # Optional: Region code (e.g., "us-en")
}
```

### OpenAI Parameters

```python
{
    "model": "gpt-4-turbo-preview",  # or "gpt-3.5-turbo"
    "temperature": 0.7,               # Creativity (0.0-1.0)
    "max_tokens": 1000,              # Response length
    "top_p": 1.0,                    # Nucleus sampling
}
```

## Troubleshooting

### OpenAI API Key Not Set
```
⚠ OPENAI_API_KEY not set. Skipping AI generation.
```
**Solution**: Set the environment variable as described in Setup section

### NPX/Node Not Found
```
Command 'npx' not found
```
**Solution**: Install Node.js from https://nodejs.org/

### MCP Server Connection Failed
```
Failed to connect: [Errno 2] No such file or directory
```
**Solution**: Ensure `npx` is in your PATH and can run `open-websearch`

### Search Returns No Results
**Solution**: 
- Try a different search engine
- Simplify the query
- Check internet connection

## Performance Tips

1. **Batch Searches** - Make multiple searches in parallel when possible
2. **Cache Results** - Store search results to avoid redundant calls
3. **Limit Results** - Use `max_results` to control response size
4. **Choose Right Engine** - DuckDuckGo for general, Exa for technical
5. **Token Management** - Monitor OpenAI token usage for cost control

## Advanced Features

### Custom Tool Formatting
Format MCP tools for OpenAI function calling:
```python
openai_tools = [
    ws_ai.format_tool_for_openai(tool) 
    for tool in ws_ai.tools
]
```

### Multi-Engine Search
Compare results from different engines:
```python
engines = ["duckduckgo", "bing", "exa"]
results = {}
for engine in engines:
    results[engine] = await ws_ai.call_tool("search", {
        "query": query,
        "engine": engine
    })
```

### Streaming Responses
Enable streaming for real-time AI responses:
```python
stream = await openai_client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=messages,
    stream=True
)
```

## Cost Considerations

- **MCP Server**: Free (runs locally via npx)
- **Search APIs**: 
  - DuckDuckGo: Free, no API key needed
  - Bing: Requires Azure subscription
  - Exa: Paid service
- **OpenAI API**: Pay per token
  - GPT-3.5-Turbo: ~$0.001 per 1K tokens
  - GPT-4-Turbo: ~$0.01 per 1K tokens

## Next Steps

1. ✅ Test basic web search functionality
2. ✅ Integrate with OpenAI API
3. ✅ Implement function calling
4. 🔄 Add result caching
5. 🔄 Create web UI for searches
6. 🔄 Add more search engines
7. 🔄 Implement streaming responses

## Related Files

- `test_websearch.py` - Main test file
- `test_websearch.json` - MCP server configuration
- `mcp_client.py` - MCP client wrapper
- `config.py` - Configuration parser
- `requirements.txt` - Python dependencies

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the test output for errors
3. Verify all dependencies are installed
4. Ensure OpenAI API key is valid

## License

This is a demonstration project for MCP + OpenAI integration.
