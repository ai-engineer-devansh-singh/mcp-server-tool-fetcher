"""
MCP Servers Web Interface - Flask Application
Browse, search, and configure MCP servers
"""

from flask import Flask, render_template, jsonify, request, send_file
from mcp_servers_config import MCPServerConfig
import json
import io

app = Flask(__name__)

@app.route('/')
def index():
    """Main page - MCP Servers Browser"""
    return render_template('mcp_browser.html')

@app.route('/api/servers')
def get_servers():
    """API endpoint to get all servers"""
    servers = MCPServerConfig.get_all_servers()
    return jsonify(servers)

@app.route('/api/categories')
def get_categories():
    """API endpoint to get all categories"""
    categories = MCPServerConfig.get_categories()
    return jsonify(categories)

@app.route('/api/servers/category/<category>')
def get_servers_by_category(category):
    """API endpoint to get servers by category"""
    servers = MCPServerConfig.get_servers_by_category(category)
    return jsonify(servers)

@app.route('/api/server/<server_id>')
def get_server(server_id):
    """API endpoint to get specific server config"""
    server = MCPServerConfig.get_server_config(server_id)
    if server:
        return jsonify(server)
    return jsonify({"error": "Server not found"}), 404

@app.route('/api/config/generate', methods=['POST'])
def generate_config():
    """Generate Claude Desktop config for selected servers"""
    data = request.get_json()
    server_ids = data.get('servers', [])
    
    config = MCPServerConfig.generate_claude_config(server_ids)
    return jsonify(config)

@app.route('/api/config/download', methods=['POST'])
def download_config():
    """Download configuration as JSON file"""
    data = request.get_json()
    server_ids = data.get('servers', [])
    
    config = MCPServerConfig.generate_claude_config(server_ids)
    json_str = json.dumps(config, indent=2)
    
    # Create a file-like object
    buffer = io.BytesIO()
    buffer.write(json_str.encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/json',
        as_attachment=True,
        download_name='claude_desktop_config.json'
    )

@app.route('/api/search')
def search_servers():
    """Search servers by name or description"""
    query = request.args.get('q', '').lower()
    all_servers = MCPServerConfig.get_all_servers()
    
    results = {}
    for sid, config in all_servers.items():
        if (query in config['name'].lower() or 
            query in config.get('description', '').lower() or
            query in sid.lower()):
            results[sid] = config
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
