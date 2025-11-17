"""
Web application for MCP Tool Lister.
"""
import asyncio
from flask import Flask, render_template, request, jsonify
from config import ConfigParser
from mcp_client import MCPToolLister

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
        # Parse configuration
        parser = ConfigParser()
        servers = parser.parse_config(config_json, auto_resolve=True)
        
        # List tools
        lister = MCPToolLister()
        try:
            all_tools = await lister.list_all_tools(servers)
            
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
            'error': str(e)
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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
