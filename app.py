"""
Web application for MCP Tool Lister.
"""
import asyncio
import json
import time
from flask import Flask, render_template, request, jsonify
from config import ConfigParser, OpenAIConfig
from mcp_client import MCPToolLister
from openai import OpenAI
from functools import lru_cache
import hashlib
from performance_monitor import monitor

app = Flask(__name__)

# Global cache for persistent connections
_connection_cache = {}
_openai_client = None


def get_openai_client():
    """Get or create cached OpenAI client."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=OpenAIConfig.get_api_key())
    return _openai_client


def get_config_hash(config_json: str) -> str:
    """Generate hash for config to use as cache key."""
    return hashlib.md5(config_json.encode()).hexdigest()


async def get_or_create_connection(config_json: str) -> tuple:
    """Get existing connection or create new one."""
    config_hash = get_config_hash(config_json)
    
    if config_hash in _connection_cache:
        return _connection_cache[config_hash]
    
    # Create new connection
    parser = ConfigParser()
    servers = parser.parse_config(config_json, auto_resolve=True)
    lister = MCPToolLister()
    await lister.connect_to_servers(servers)
    
    # Cache it
    _connection_cache[config_hash] = (lister, servers)
    return lister, servers


app = Flask(__name__)


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/list-tools', methods=['POST'])
def list_tools():
    """
    API endpoint to list tools from MCP servers.
    
    Expects JSON: {"config": "...MCP config JSON..."}
    Returns: {"success": bool, "data": {...}, "error": str}
    """
    try:
        data = request.get_json()
        config_json = data.get('config', '')
        
        if not config_json:
            return jsonify({
                'success': False,
                'error': 'No configuration provided'
            }), 400
        
        # Run async tool listing
        result = asyncio.run(fetch_tools(config_json))
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/execute-tool', methods=['POST'])
def execute_tool():
    """
    API endpoint to execute a tool on an MCP server.
    
    Expects JSON: {
        "config": "...MCP config JSON...",
        "server_name": "server_name",
        "tool_name": "tool_name",
        "arguments": {...}
    }
    Returns: {"success": bool, "result": {...}, "error": str}
    """
    try:
        data = request.get_json()
        config_json = data.get('config', '')
        server_name = data.get('server_name', '')
        tool_name = data.get('tool_name', '')
        arguments = data.get('arguments', {})
        
        if not config_json:
            return jsonify({
                'success': False,
                'error': 'No configuration provided'
            }), 400
        
        if not server_name:
            return jsonify({
                'success': False,
                'error': 'No server_name provided'
            }), 400
        
        if not tool_name:
            return jsonify({
                'success': False,
                'error': 'No tool_name provided'
            }), 400
        
        # Run async tool execution
        result = asyncio.run(execute_mcp_tool(config_json, server_name, tool_name, arguments))
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


async def fetch_tools(config_json: str) -> dict:
    """
    Fetch tools from MCP servers.
    
    Args:
        config_json: MCP configuration as JSON string
        
    Returns:
        Dictionary with results or error
    """
    try:
        # Use persistent connection
        lister, servers = await get_or_create_connection(config_json)
        
        # Get tools from all servers
        all_tools = {}
        for name in lister.server_names:
            tools = await lister.get_tools_from_server(name)
            all_tools[name] = tools
        
        # Calculate totals
        total_tools = sum(len(tools) for tools in all_tools.values())
        
        return {
            'success': True,
            'data': {
                'servers': list(servers.keys()),
                'tools': all_tools,
                'total_tools': total_tools,
                'server_count': len(servers)
            }
        }
    
    except ValueError as e:
        return {
            'success': False,
            'error': f'Configuration error: {str(e)}'
        }
    except FileNotFoundError as e:
        error_msg = str(e)
        if 'uvx' in error_msg or 'uv' in error_msg:
            return {
                'success': False,
                'error': 'Command "uvx" not found. On deployment platforms like Render, use NPX-based MCP servers instead. See DEPLOYMENT.md for alternatives.'
            }
        return {
            'success': False,
            'error': f'Command not found: {error_msg}'
        }
    except Exception as e:
        error_msg = str(e)
        if 'No such file or directory' in error_msg and ('uvx' in error_msg or 'uv' in error_msg):
            return {
                'success': False,
                'error': 'Command "uvx" not found. On deployment platforms like Render, use NPX-based MCP servers instead. Examples: npx @modelcontextprotocol/server-fetch'
            }
        return {
            'success': False,
            'error': error_msg
        }


async def execute_mcp_tool(config_json: str, server_name: str, tool_name: str, arguments: dict) -> dict:
    """
    Execute a tool on an MCP server.
    
    Args:
        config_json: MCP configuration as JSON string
        server_name: Name of the MCP server
        tool_name: Name of the tool to execute
        arguments: Arguments to pass to the tool
        
    Returns:
        Dictionary with results or error
    """
    try:
        # Parse configuration
        parser = ConfigParser()
        servers = parser.parse_config(config_json, auto_resolve=True)
        
        if server_name not in servers:
            return {
                'success': False,
                'error': f'Server "{server_name}" not found in configuration'
            }
        
        # Execute tool
        lister = MCPToolLister()
        try:
            await lister.connect_to_servers(servers)
            
            # Get session and call tool
            session = lister.client.get_session(server_name)
            result = await session.call_tool(tool_name, arguments)
            
            # Extract result content
            if hasattr(result, 'content') and result.content:
                content_list = []
                for item in result.content:
                    if hasattr(item, 'text'):
                        content_list.append({
                            'type': 'text',
                            'text': item.text
                        })
                    elif hasattr(item, 'data'):
                        content_list.append({
                            'type': 'resource',
                            'data': item.data
                        })
                    else:
                        content_list.append(str(item))
                
                return {
                    'success': True,
                    'result': {
                        'content': content_list,
                        'isError': getattr(result, 'isError', False)
                    }
                }
            else:
                return {
                    'success': True,
                    'result': {
                        'content': [{'type': 'text', 'text': str(result)}],
                        'isError': False
                    }
                }
        finally:
            await lister.close_all_connections()
    
    except ValueError as e:
        return {
            'success': False,
            'error': f'Configuration error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Execution error: {str(e)}'
        }


@app.route('/api/query', methods=['POST'])
def query():
    """
    API endpoint to process user queries with AI and execute tools.
    
    Expects JSON: {
        "config": "...MCP config JSON...",
        "query": "user question",
        "tools": {...available tools...}
    }
    Returns: {"success": bool, "response": str, "tool_calls": [...], "error": str}
    """
    start_time = time.time()
    try:
        # Check if OpenAI is configured
        if not OpenAIConfig.is_configured():
            return jsonify({
                'success': False,
                'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.'
            }), 400
        
        data = request.get_json()
        config_json = data.get('config', '')
        user_query = data.get('query', '')
        available_tools = data.get('tools', {})
        
        if not config_json or not user_query:
            return jsonify({
                'success': False,
                'error': 'Missing config or query'
            }), 400
        
        # Run async query processing
        result = asyncio.run(process_ai_query(config_json, user_query, available_tools))
        
        # Add performance metrics
        elapsed = time.time() - start_time
        result['elapsed_time'] = round(elapsed, 2)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def build_tools_schema(available_tools: dict) -> tuple:
    """Build OpenAI tools schema and mapping (cached per request)."""
    tools_for_openai = []
    tool_mapping = {}
    
    for server_name, tools in available_tools.items():
        for tool in tools:
            function_name = f"{server_name}_{tool['name']}"
            tool_mapping[function_name] = {
                'server': server_name,
                'tool': tool['name']
            }
            
            tools_for_openai.append({
                'type': 'function',
                'function': {
                    'name': function_name,
                    'description': tool.get('description', 'No description'),
                    'parameters': tool.get('inputSchema', {
                        'type': 'object',
                        'properties': {}
                    })
                }
            })
    
    return tools_for_openai, tool_mapping


async def execute_tool_call(lister, tool_call, tool_mapping):
    """Execute a single tool call (for parallel execution)."""
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    
    if function_name not in tool_mapping:
        return None
    
    server_name = tool_mapping[function_name]['server']
    tool_name = tool_mapping[function_name]['tool']
    
    # Execute the tool
    session = lister.client.get_session(server_name)
    result = await session.call_tool(tool_name, arguments)
    
    # Extract result content
    result_text = ""
    if hasattr(result, 'content') and result.content:
        for item in result.content:
            if hasattr(item, 'text'):
                result_text += item.text
            else:
                result_text += str(item)
    else:
        result_text = str(result)
    
    return {
        'tool_call_id': tool_call.id,
        'role': 'tool',
        'content': result_text,
        'server': server_name,
        'tool': tool_name,
        'function_name': function_name,
    }


async def process_ai_query(config_json: str, user_query: str, available_tools: dict) -> dict:
    """
    Process user query with OpenAI and execute necessary tools.
    
    Args:
        config_json: MCP configuration as JSON string
        user_query: User's natural language query
        available_tools: Dictionary of available tools by server
        
    Returns:
        Dictionary with response and tool execution details
    """
    try:
        # Use cached OpenAI client
        client = get_openai_client()
        
        # Build tools schema (fast)
        tools_for_openai, tool_mapping = build_tools_schema(available_tools)
        
        # Create messages for OpenAI
        messages = [
            {
                'role': 'system',
                'content': 'You are a helpful AI assistant with access to MCP tools. Use the available tools to answer user questions accurately. When using tools, provide clear explanations of what you found.'
            },
            {
                'role': 'user',
                'content': user_query
            }
        ]
        
        # Call OpenAI with function calling
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            tools=tools_for_openai if tools_for_openai else None,
            tool_choice='auto' if tools_for_openai else None
        )
        
        assistant_message = response.choices[0].message
        tool_calls_made = []
        
        # Check if AI wants to call tools
        if assistant_message.tool_calls:
            # Use persistent connection (reuse if exists)
            lister, servers = await get_or_create_connection(config_json)
            
            # Execute all tool calls in parallel for speed
            tool_tasks = [
                execute_tool_call(lister, tool_call, tool_mapping)
                for tool_call in assistant_message.tool_calls
            ]
            
            # Wait for all tools to complete in parallel
            tool_results_raw = await asyncio.gather(*tool_tasks, return_exceptions=True)

            # Map results by tool_call_id for completeness
            results_by_id = {}
            for item in tool_results_raw:
                if isinstance(item, Exception) or item is None:
                    continue
                results_by_id[item['tool_call_id']] = item

            # Build one tool message per tool_call (required by API)
            tool_results = []
            for tc in assistant_message.tool_calls:
                tc_id = tc.id
                if tc_id in results_by_id:
                    r = results_by_id[tc_id]
                    tool_calls_made.append({
                        'server': r['server'],
                        'tool': r['tool']
                    })
                    tool_results.append({
                        'tool_call_id': r['tool_call_id'],
                        'role': 'tool',
                        'content': r['content'],
                    })
                else:
                    # Ensure every tool_call has a corresponding tool message
                    tool_results.append({
                        'tool_call_id': tc_id,
                        'role': 'tool',
                        'content': 'Tool execution failed or returned no result.',
                    })
            
            # Add tool results to conversation and get final response
            # Normalize assistant message into dict to avoid SDK object issues
            assistant_dict = {
                'role': 'assistant',
                'content': assistant_message.content,
                'tool_calls': [
                    {
                        'id': tc.id,
                        'type': 'function',
                        'function': {
                            'name': tc.function.name,
                            'arguments': tc.function.arguments,
                        },
                    }
                    for tc in (assistant_message.tool_calls or [])
                ],
            }

            messages.append(assistant_dict)
            messages.extend(tool_results)
            
            final_response = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=messages
            )
            
            final_answer = final_response.choices[0].message.content
        else:
            # No tool calls needed, use direct response
            final_answer = assistant_message.content
        
        return {
            'success': True,
            'response': final_answer,
            'tool_calls': tool_calls_made
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """Clear connection cache (useful for config changes)."""
    global _connection_cache
    try:
        # Close all cached connections
        for config_hash, (lister, servers) in _connection_cache.items():
            try:
                asyncio.run(lister.close_all_connections())
            except:
                pass
        
        _connection_cache.clear()
        
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get performance statistics."""
    return jsonify({
        'success': True,
        'cache_size': len(_connection_cache),
        'performance': monitor.get_stats()
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
