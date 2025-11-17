# Web Search MCP Quick Start

## 🚀 Quick Test Commands

### 1. List Available Tools
```powershell
cd 'd:\Projects\MCP python'
python test_websearch.py
```

### 2. Test Without OpenAI (Basic Search)
Set a flag to skip OpenAI tests:
```powershell
$env:SKIP_OPENAI_TESTS = "true"
python test_websearch.py
```

### 3. Test With OpenAI (Full Integration)
```powershell
$env:OPENAI_API_KEY = "sk-your-key-here"
python test_websearch.py
```

## 📋 Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js installed (for npx)
- [ ] OpenAI API key (optional, for AI features)
- [ ] Dependencies installed: `pip install -r requirements.txt`

## 🎯 What Each Test Does

### Test 1: List Tools (Always Runs)
✅ Connects to open-websearch MCP server  
✅ Lists all available search tools  
✅ Shows tool parameters and descriptions  

**Expected Output:**
```
✓ Found 1 server(s)
✓ Connected to all servers
Found X tool(s) in web-search

Available Web Search Tools
----------------------------------------
Tool: search
Description: Search the web using [engine]
Parameters: query, engine, max_results
```

### Test 2: Search + Generate (Requires OpenAI)
✅ Performs actual web search  
✅ Displays search results  
✅ Generates AI summary of results  

**Expected Output:**
```
Searching for: latest AI developments 2025
Using search engine: duckduckgo

Search Results:
1. Title of result
   URL: https://example.com
   Snippet of content...

AI-Generated Summary
----------------------------------------
[Comprehensive summary of search results]

Tokens used: 150 (prompt: 100, completion: 50)
```

### Test 3: Function Calling (Requires OpenAI)
✅ Uses OpenAI function calling  
✅ OpenAI autonomously decides to search  
✅ Generates final response with search data  

**Expected Output:**
```
User Query: What are the latest developments in AI?

OpenAI is calling web search tools...
Calling tool: search
Arguments: {'query': 'latest AI developments', 'engine': 'duckduckgo'}

Final AI Response
----------------------------------------
[AI response incorporating search results]
```

## ⚡ One-Liner Test

```powershell
cd 'd:\Projects\MCP python'; $env:OPENAI_API_KEY = "your-key"; python test_websearch.py
```

## 🔧 Troubleshooting Quick Fixes

### Issue: "npx not found"
```powershell
npm install -g npx
```

### Issue: "OPENAI_API_KEY not set"
```powershell
$env:OPENAI_API_KEY = "sk-your-key-here"
```

### Issue: "Module 'openai' not found"
```powershell
pip install openai
```

### Issue: "Connection timeout"
- Check internet connection
- Verify npx can run: `npx --version`
- Try: `npx open-websearch@latest --version`

## 📊 Expected Success Indicators

✅ Green checkmarks for successful connections  
✅ Tool listing shows search capabilities  
✅ Search results display with titles and URLs  
✅ AI summaries generated (if OpenAI configured)  
✅ No red error messages  

## 🎬 Sample Session

```
Web Search MCP + OpenAI Integration Tests

Configuration:
  OpenAI API Key: ✓ Set
  OpenAI Model: gpt-4-turbo-preview

================================================================================
Test 1: List Web Search MCP Tools
================================================================================

✓ Found 1 server(s)
✓ Connected to all servers
Found 3 tool(s) in web-search

Total tools available: 3

================================================================================
Test 2: Web Search + OpenAI Content Generation
================================================================================

Searching for: latest AI developments 2025
Using search engine: duckduckgo

Search Results:
1. AI News 2025
   https://example.com/ai-news
   Latest developments in artificial intelligence...

Generating AI-powered summary...

AI-Generated Summary
----------------------------------------
Based on recent developments, AI in 2025 has seen...

================================================================================
Test 3: OpenAI Function Calling with Web Search
================================================================================

User Query: What are the latest developments in AI?

OpenAI is calling web search tools...
Calling tool: search

Final AI Response
----------------------------------------
The latest AI developments include...

✓ All tests completed successfully!
```

## 💡 Tips

1. **Start Simple**: Run Test 1 first to verify MCP connection
2. **Save API Costs**: Use `$env:SKIP_OPENAI_TESTS = "true"` for testing
3. **Monitor Tokens**: Watch the token usage in output
4. **Customize Queries**: Edit `test_websearch.py` to test your own queries
5. **Try Different Engines**: Change `"duckduckgo"` to `"bing"` or `"exa"`

## 🔗 Next Steps

After successful testing:
1. ✅ Integrate into your own applications
2. ✅ Create custom search queries
3. ✅ Build AI-powered research tools
4. ✅ Explore other MCP servers
