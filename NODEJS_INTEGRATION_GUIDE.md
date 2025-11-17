# Node.js Integration Guide for MCP Tool Lister API

## Overview
This guide explains how to integrate the Python MCP Tool Lister API (`/api/list-tools`) into your Node.js project to dynamically fetch and use MCP tools with OpenAI.

## Architecture Flow
```
User Config → Node.js App → Python API → MCP Servers → Tools List → OpenAI Function Calling
```

## API Endpoint Details

### Endpoint
```
POST /api/list-tools
```

### Request Format
```json
{
  "config": "<MCP configuration as JSON string>"
}
```

### Response Format
```json
{
  "success": true,
  "data": {
    "servers": ["server1", "server2"],
    "tools": {
      "server1": [
        {
          "name": "tool_name",
          "description": "Tool description",
          "inputSchema": {
            "type": "object",
            "properties": {...}
          }
        }
      ]
    },
    "total_tools": 10,
    "server_count": 2
  }
}
```

## Node.js Implementation

### 1. Installation
```bash
npm install axios
npm install openai
```

### 2. Create MCP Tool Fetcher Module

**`mcpToolFetcher.js`**
```javascript
const axios = require('axios');

class MCPToolFetcher {
  constructor(pythonApiUrl = 'http://localhost:5000') {
    this.apiUrl = pythonApiUrl;
  }

  /**
   * Fetch tools from Python MCP API
   * @param {string} mcpConfig - MCP configuration JSON string
   * @returns {Promise<Object>} Tools data
   */
  async fetchTools(mcpConfig) {
    try {
      const response = await axios.post(`${this.apiUrl}/api/list-tools`, {
        config: mcpConfig
      }, {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 30000 // 30 seconds timeout
      });

      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.error || 'Failed to fetch tools');
      }
    } catch (error) {
      if (error.response) {
        throw new Error(`API Error: ${error.response.data.error || error.message}`);
      } else if (error.request) {
        throw new Error('Python API is not responding. Make sure it\'s running.');
      } else {
        throw new Error(`Request Error: ${error.message}`);
      }
    }
  }

  /**
   * Execute a tool on MCP server via Python API
   * @param {string} mcpConfig - MCP configuration JSON string
   * @param {string} serverName - Name of the MCP server
   * @param {string} toolName - Name of the tool to execute
   * @param {Object} arguments - Tool arguments
   * @returns {Promise<Object>} Tool execution result
   */
  async executeTool(mcpConfig, serverName, toolName, arguments) {
    try {
      const response = await axios.post(`${this.apiUrl}/api/execute-tool`, {
        config: mcpConfig,
        server_name: serverName,
        tool_name: toolName,
        arguments: arguments
      }, {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 60000 // 60 seconds timeout for tool execution
      });

      if (response.data.success) {
        return response.data.result;
      } else {
        throw new Error(response.data.error || 'Failed to execute tool');
      }
    } catch (error) {
      if (error.response) {
        throw new Error(`API Error: ${error.response.data.error || error.message}`);
      } else if (error.request) {
        throw new Error('Python API is not responding. Make sure it\'s running.');
      } else {
        throw new Error(`Request Error: ${error.message}`);
      }
    }
  }

  /**
   * Convert MCP tools to OpenAI function format
   * @param {Object} toolsData - Tools data from Python API
   * @returns {Array} OpenAI functions array
   */
  convertToOpenAIFunctions(toolsData) {
    const functions = [];
    
    for (const [serverName, tools] of Object.entries(toolsData.tools)) {
      for (const tool of tools) {
        functions.push({
          name: `${serverName}_${tool.name}`,
          description: tool.description || `Tool from ${serverName}`,
          parameters: tool.inputSchema || {
            type: 'object',
            properties: {}
          }
        });
      }
    }
    
    return functions;
  }
}

module.exports = MCPToolFetcher;
```

### 3. Integrate with OpenAI

**`openaiIntegration.js`**
```javascript
const OpenAI = require('openai');
const MCPToolFetcher = require('./mcpToolFetcher');

class OpenAIWithMCPTools {
  constructor(openaiApiKey, pythonApiUrl) {
    this.openai = new OpenAI({ apiKey: openaiApiKey });
    this.toolFetcher = new MCPToolFetcher(pythonApiUrl);
    this.availableFunctions = [];
    this.mcpConfig = null;
    this.toolMap = new Map(); // Map function names to server/tool info
  }

  /**
   * Initialize MCP tools from config
   * @param {string|Object} mcpConfig - MCP configuration
   */
  async initializeTools(mcpConfig) {
    try {
      // Convert config to string if it's an object
      const configString = typeof mcpConfig === 'string' 
        ? mcpConfig 
        : JSON.stringify(mcpConfig);

      this.mcpConfig = configString;

      // Fetch tools from Python API
      const toolsData = await this.toolFetcher.fetchTools(configString);
      
      // Convert to OpenAI function format and build tool map
      this.availableFunctions = this.toolFetcher.convertToOpenAIFunctions(toolsData);
      
      // Build tool map for execution
      for (const [serverName, tools] of Object.entries(toolsData.tools)) {
        for (const tool of tools) {
          const functionName = `${serverName}_${tool.name}`;
          this.toolMap.set(functionName, {
            serverName: serverName,
            toolName: tool.name
          });
        }
      }
      
      console.log(`Loaded ${toolsData.total_tools} tools from ${toolsData.server_count} servers`);
      
      return {
        success: true,
        toolCount: toolsData.total_tools,
        servers: toolsData.servers
      };
    } catch (error) {
      console.error('Failed to initialize MCP tools:', error.message);
      throw error;
    }
  }

  /**
   * Execute a function call from OpenAI
   * @param {string} functionName - Name of the function to execute
   * @param {Object} functionArgs - Arguments for the function
   * @returns {Promise<Object>} Execution result
   */
  async executeFunction(functionName, functionArgs) {
    try {
      const toolInfo = this.toolMap.get(functionName);
      
      if (!toolInfo) {
        throw new Error(`Unknown function: ${functionName}`);
      }

      const result = await this.toolFetcher.executeTool(
        this.mcpConfig,
        toolInfo.serverName,
        toolInfo.toolName,
        functionArgs
      );

      return result;
    } catch (error) {
      console.error(`Failed to execute ${functionName}:`, error.message);
      throw error;
    }
  }

  /**
   * Chat completion with MCP tools and automatic function execution
   * @param {Array} messages - Chat messages
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Chat response with function results
   */
  async chat(messages, options = {}) {
    try {
      const response = await this.openai.chat.completions.create({
        model: options.model || 'gpt-4-turbo-preview',
        messages: messages,
        functions: this.availableFunctions,
        function_call: options.function_call || 'auto',
        temperature: options.temperature || 0.7,
        max_tokens: options.max_tokens || 1000
      });

      const message = response.choices[0].message;

      // If OpenAI wants to call a function, execute it automatically
      if (message.function_call && options.autoExecute !== false) {
        const functionName = message.function_call.name;
        const functionArgs = JSON.parse(message.function_call.arguments);

        console.log(`Executing function: ${functionName}`);

        try {
          const functionResult = await this.executeFunction(functionName, functionArgs);

          // Add function result to messages and get final response
          const updatedMessages = [
            ...messages,
            message,
            {
              role: 'function',
              name: functionName,
              content: JSON.stringify(functionResult)
            }
          ];

          // Get final response from OpenAI
          const finalResponse = await this.openai.chat.completions.create({
            model: options.model || 'gpt-4-turbo-preview',
            messages: updatedMessages,
            temperature: options.temperature || 0.7,
            max_tokens: options.max_tokens || 1000
          });

          return {
            ...finalResponse,
            functionExecuted: true,
            functionName: functionName,
            functionResult: functionResult
          };
        } catch (error) {
          console.error('Function execution failed:', error.message);
          
          // Return error to OpenAI
          const errorMessages = [
            ...messages,
            message,
            {
              role: 'function',
              name: functionName,
              content: JSON.stringify({ error: error.message })
            }
          ];

          const errorResponse = await this.openai.chat.completions.create({
            model: options.model || 'gpt-4-turbo-preview',
            messages: errorMessages,
            temperature: options.temperature || 0.7,
            max_tokens: options.max_tokens || 1000
          });

          return {
            ...errorResponse,
            functionExecuted: false,
            functionError: error.message
          };
        }
      }

      return response;
    } catch (error) {
      console.error('OpenAI API error:', error.message);
      throw error;
    }
  }

  /**
   * Get available tools
   */
  getAvailableTools() {
    return this.availableFunctions;
  }
}

module.exports = OpenAIWithMCPTools;
```

### 4. Express.js API Example

**`server.js`**
```javascript
const express = require('express');
const OpenAIWithMCPTools = require('./openaiIntegration');

const app = express();
app.use(express.json());

// Initialize OpenAI with MCP tools
const aiClient = new OpenAIWithMCPTools(
  process.env.OPENAI_API_KEY,
  process.env.PYTHON_API_URL || 'http://localhost:5000'
);

/**
 * Initialize tools endpoint
 */
app.post('/api/initialize-tools', async (req, res) => {
  try {
    const { config } = req.body;
    
    if (!config) {
      return res.status(400).json({
        success: false,
        error: 'MCP configuration is required'
      });
    }

    const result = await aiClient.initializeTools(config);
    
    res.json({
      success: true,
      data: result,
      tools: aiClient.getAvailableTools()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Chat endpoint with MCP tools
 */
app.post('/api/chat', async (req, res) => {
  try {
    const { messages, options } = req.body;
    
    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({
        success: false,
        error: 'Messages array is required'
      });
    }

    // Make sure tools are initialized
    if (aiClient.getAvailableTools().length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Tools not initialized. Call /api/initialize-tools first'
      });
    }

    const response = await aiClient.chat(messages, options);
    
    res.json({
      success: true,
      data: response
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get available tools
 */
app.get('/api/tools', (req, res) => {
  res.json({
    success: true,
    tools: aiClient.getAvailableTools(),
    count: aiClient.getAvailableTools().length
  });
});

/**
 * Execute a specific MCP tool directly
 */
app.post('/api/execute-tool', async (req, res) => {
  try {
    const { functionName, arguments: functionArgs } = req.body;
    
    if (!functionName) {
      return res.status(400).json({
        success: false,
        error: 'Function name is required'
      });
    }

    // Make sure tools are initialized
    if (aiClient.getAvailableTools().length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Tools not initialized. Call /api/initialize-tools first'
      });
    }

    const result = await aiClient.executeFunction(functionName, functionArgs || {});
    
    res.json({
      success: true,
      result: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### 5. Usage Example

**`example.js`**
```javascript
const OpenAIWithMCPTools = require('./openaiIntegration');

async function main() {
  // Initialize
  const aiClient = new OpenAIWithMCPTools(
    'your-openai-api-key',
    'http://localhost:5000'
  );

  // MCP Configuration
  const mcpConfig = {
    "mcpServers": {
      "memory": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-memory"]
      },
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/files"]
      }
    }
  };

  try {
    // Step 1: Initialize tools
    console.log('Initializing MCP tools...');
    const initResult = await aiClient.initializeTools(mcpConfig);
    console.log('Initialized:', initResult);

    // Step 2: Chat with AI using MCP tools
    console.log('\nChatting with AI...');
    const messages = [
      {
        role: 'user',
        content: 'List the available tools and their capabilities'
      }
    ];

    const response = await aiClient.chat(messages, {
      autoExecute: true  // Automatically execute tools when OpenAI requests them
    });
    
    console.log('AI Response:', response.choices[0].message);

    // Check if a function was executed
    if (response.functionExecuted) {
      console.log('\nFunction executed:', response.functionName);
      console.log('Function result:', response.functionResult);
    }

    // Step 3: Example of manually executing a tool
    console.log('\n--- Manual Tool Execution Example ---');
    const manualResult = await aiClient.executeFunction(
      'memory_store_entity',  // Assuming you have a memory server
      {
        name: 'test-entity',
        value: 'test-value'
      }
    );
    console.log('Manual execution result:', manualResult);

  } catch (error) {
    console.error('Error:', error.message);
  }
}

main();
```

## Frontend Integration (React/Vue/Angular)

**`mcpService.js`**
```javascript
class MCPService {
  constructor(baseUrl = 'http://localhost:3000') {
    this.baseUrl = baseUrl;
  }

  async initializeTools(config) {
    const response = await fetch(`${this.baseUrl}/api/initialize-tools`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ config })
    });

    return await response.json();
  }

  async chat(messages, options = {}) {
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ messages, options })
    });

    return await response.json();
  }

  async getAvailableTools() {
    const response = await fetch(`${this.baseUrl}/api/tools`);
    return await response.json();
  }

  async executeTool(functionName, functionArgs = {}) {
    const response = await fetch(`${this.baseUrl}/api/execute-tool`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        functionName: functionName,
        arguments: functionArgs 
      })
    });

    return await response.json();
  }
}

export default MCPService;
```

## Environment Variables

Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
PYTHON_API_URL=http://localhost:5000
PORT=3000
NODE_ENV=development
```

## Deployment Considerations

### 1. Running Both Services

**Option A: Separate Processes**
```bash
# Terminal 1 - Python API
cd /path/to/python/project
python app.py

# Terminal 2 - Node.js API
cd /path/to/nodejs/project
node server.js
```

**Option B: Docker Compose**
```yaml
version: '3.8'

services:
  python-api:
    build: ./python-project
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production

  nodejs-api:
    build: ./nodejs-project
    ports:
      - "3000:3000"
    environment:
      - PYTHON_API_URL=http://python-api:5000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - python-api
```

### 2. Production Considerations

- **Error Handling**: Implement retry logic for API calls
- **Caching**: Cache tool definitions to reduce API calls
- **Rate Limiting**: Implement rate limiting on both APIs
- **Monitoring**: Log all API interactions
- **Security**: Use HTTPS, API keys, and CORS properly

## Error Handling Best Practices

```javascript
async function safeInitializeTools(config) {
  const maxRetries = 3;
  let retries = 0;

  while (retries < maxRetries) {
    try {
      return await aiClient.initializeTools(config);
    } catch (error) {
      retries++;
      console.warn(`Retry ${retries}/${maxRetries}:`, error.message);
      
      if (retries === maxRetries) {
        throw new Error(`Failed after ${maxRetries} attempts: ${error.message}`);
      }
      
      // Wait before retry (exponential backoff)
      await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, retries)));
    }
  }
}
```

## Testing

**`test.js`**
```javascript
const MCPToolFetcher = require('./mcpToolFetcher');

async function test() {
  const fetcher = new MCPToolFetcher('http://localhost:5000');
  
  const testConfig = {
    "mcpServers": {
      "memory": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-memory"]
      }
    }
  };

  try {
    console.log('Testing tool fetching...');
    const tools = await fetcher.fetchTools(JSON.stringify(testConfig));
    console.log('Success:', tools);
    
    console.log('\nConverting to OpenAI format...');
    const functions = fetcher.convertToOpenAIFunctions(tools);
    console.log('Functions:', functions);
  } catch (error) {
    console.error('Test failed:', error.message);
  }
}

test();
```

## Complete Flow Example

1. **User provides MCP config** → Your Node.js frontend/API
2. **Node.js sends config** → Python API (`/api/list-tools`)
3. **Python fetches tools** → From MCP servers
4. **Python returns tools** → To Node.js
5. **Node.js converts tools** → OpenAI function format
6. **OpenAI uses tools** → For intelligent responses
7. **User gets results** → Enhanced AI capabilities

## Support

For issues or questions:
- Python API: Check `app.py` and `mcp_client.py`
- Node.js Integration: Review this guide
- MCP Servers: See [MCP Documentation](https://modelcontextprotocol.io/)

## License

Same as the main project.
