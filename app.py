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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
