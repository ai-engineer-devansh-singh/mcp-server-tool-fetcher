# Deployment Guide

## Deploying to Render

### Prerequisites
- A Render account (https://render.com)
- GitHub repository connected to Render
- OpenAI API key

### Environment Variables

Add these environment variables in your Render dashboard:

1. **OPENAI_API_KEY** (required)
   - Your OpenAI API key
   - Set as secret

### MCP Server Dependencies

#### For Python-based MCP servers (uvx/uv)

The `uv` package is included in `requirements.txt` and will be installed automatically. However, `uvx` is a command-line wrapper that needs special handling.

**Current limitation on Render:**
- MCP servers that require `uvx` may not work on Render's free tier
- Alternative: Use NPX-based MCP servers instead

#### For Node.js-based MCP servers (npx)

Node.js and npm/npx are pre-installed on Render Python environments, so NPX-based MCP servers work out of the box.

### Recommended MCP Servers for Render Deployment

Use these NPX-based servers that work reliably on Render:

```json
{
    "mcpServers": {
        "fetch": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-fetch"]
        },
        "memory": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"]
        },
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        }
    }
}
```

### Weather Server Alternative

If you need the weather server on Render, consider these alternatives:

1. **Use a different weather MCP server** (if available via NPX)
2. **Deploy your own weather MCP server** as a separate service
3. **Use a weather API directly** via the fetch MCP server

Example using fetch server to call weather APIs:
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

Then query: "Use the fetch tool to get weather data from api.openweathermap.org"

### Build Configuration

The `render.yaml` includes:
- Python 3.11 runtime
- Automatic dependency installation
- Gunicorn with 2 workers
- 120-second timeout for MCP operations

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create Web Service on Render**
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`
   - Add environment variables in the dashboard
   - Deploy

3. **Test Your Deployment**
   - Wait for build to complete
   - Visit your app URL
   - Test with NPX-based MCP servers first

### Troubleshooting

#### Error: "No such file or directory: 'uvx'"
- **Cause**: `uvx` is not available in the deployment environment
- **Solution**: Use NPX-based MCP servers instead (see recommended servers above)

#### Error: "Connection timeout"
- **Cause**: MCP server taking too long to start
- **Solution**: Increase timeout in `render.yaml` (already set to 120s)

#### Error: "Module not found"
- **Cause**: Missing dependency
- **Solution**: Add to `requirements.txt` and redeploy

#### MCP Server Not Responding
- **Check**: Server command is correct (npx vs uvx)
- **Check**: All required environment variables are set
- **Check**: Server package name is correct

### Performance Tips

1. **Use connection caching** (already implemented in `app.py`)
2. **Limit concurrent MCP servers** (max 3-4 on free tier)
3. **Use lightweight servers** (avoid resource-intensive operations)

### Local Testing Before Deployment

Test your configuration locally first:

```bash
# Set environment variables
$env:OPENAI_API_KEY="your-key"

# Run the app
python app.py

# Test with your MCP config
# Visit http://localhost:5000
```

### Cost Optimization

Render free tier includes:
- 750 hours/month
- Automatic sleep after 15 min inactivity
- Cold starts may take 30-60 seconds

For production use, consider:
- Upgrade to paid plan for always-on service
- Use external MCP server hosting
- Implement request caching
