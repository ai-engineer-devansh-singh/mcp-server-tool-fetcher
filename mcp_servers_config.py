"""
MCP Servers Configuration and Management
This module provides MCP server configurations and utilities
"""

import json
from typing import Dict, List, Any

class MCPServerConfig:
    """MCP Server Configuration Manager"""
    
    # Popular MCP Server Configurations
    SERVERS = {
        "filesystem": {
            "name": "Filesystem",
            "description": "Access and manage files on the local filesystem",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "d:/Projects"],
            "category": "Core",
            "transport": "stdio"
        },
        "github": {
            "name": "GitHub",
            "description": "Interact with GitHub repositories, issues, and PRs",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {
                "GITHUB_PERSONAL_ACCESS_TOKEN": "<your-token>"
            },
            "category": "Development",
            "transport": "stdio"
        },
        "brave-search": {
            "name": "Brave Search",
            "description": "Web search using Brave Search API",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {
                "BRAVE_API_KEY": "<your-api-key>"
            },
            "category": "Search",
            "transport": "stdio"
        },
        "google-drive": {
            "name": "Google Drive",
            "description": "Access and manage Google Drive files",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-gdrive"],
            "category": "Cloud Storage",
            "transport": "stdio"
        },
        "slack": {
            "name": "Slack",
            "description": "Interact with Slack workspaces",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-slack"],
            "env": {
                "SLACK_BOT_TOKEN": "<your-token>",
                "SLACK_TEAM_ID": "<your-team-id>"
            },
            "category": "Communication",
            "transport": "stdio"
        },
        "postgres": {
            "name": "PostgreSQL",
            "description": "Connect to and query PostgreSQL databases",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"],
            "category": "Database",
            "transport": "stdio"
        },
        "puppeteer": {
            "name": "Puppeteer",
            "description": "Browser automation and web scraping",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
            "category": "Web Automation",
            "transport": "stdio"
        },
        "sqlite": {
            "name": "SQLite",
            "description": "Query and manage SQLite databases",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sqlite", "--db-path", "database.db"],
            "category": "Database",
            "transport": "stdio"
        },
        "memory": {
            "name": "Memory",
            "description": "Persistent memory storage for conversations",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"],
            "category": "Core",
            "transport": "stdio"
        },
        "fetch": {
            "name": "Fetch",
            "description": "Fetch web content and convert to markdown",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-fetch"],
            "category": "Web",
            "transport": "stdio"
        },
        "aws-kb-retrieval": {
            "name": "AWS Knowledge Base Retrieval",
            "description": "Query AWS Bedrock Knowledge Bases",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-aws-kb-retrieval"],
            "env": {
                "AWS_ACCESS_KEY_ID": "<your-key>",
                "AWS_SECRET_ACCESS_KEY": "<your-secret>"
            },
            "category": "AI/ML",
            "transport": "stdio"
        },
        "git": {
            "name": "Git",
            "description": "Git operations and repository management",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-git"],
            "category": "Development",
            "transport": "stdio"
        },
        "sequential-thinking": {
            "name": "Sequential Thinking",
            "description": "Dynamic and reflective problem-solving through thought sequences",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
            "category": "AI/ML",
            "transport": "stdio"
        },
        "everything": {
            "name": "Everything Search",
            "description": "Fast file search on Windows using Everything",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-everything"],
            "category": "Search",
            "transport": "stdio"
        },
        "youtube-transcript": {
            "name": "YouTube Transcript",
            "description": "Fetch YouTube video transcripts",
            "command": "npx",
            "args": ["-y", "@kimtaeyoon83/mcp-server-youtube-transcript"],
            "category": "Media",
            "transport": "stdio"
        },
        "docker": {
            "name": "Docker",
            "description": "Manage Docker containers, images, and networks",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-docker"],
            "category": "Infrastructure",
            "transport": "stdio"
        },
        "kubernetes": {
            "name": "Kubernetes",
            "description": "Manage Kubernetes clusters and resources",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-kubernetes"],
            "category": "Infrastructure",
            "transport": "stdio"
        },
        "sentry": {
            "name": "Sentry",
            "description": "Query Sentry error tracking",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sentry"],
            "env": {
                "SENTRY_AUTH_TOKEN": "<your-token>",
                "SENTRY_ORG": "<your-org>"
            },
            "category": "Monitoring",
            "transport": "stdio"
        },
        "axiom": {
            "name": "Axiom",
            "description": "Query and analyze logs in Axiom",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-axiom"],
            "env": {
                "AXIOM_API_TOKEN": "<your-token>",
                "AXIOM_ORG_ID": "<your-org-id>"
            },
            "category": "Monitoring",
            "transport": "stdio"
        },
        "cloudflare": {
            "name": "Cloudflare",
            "description": "Manage Cloudflare resources",
            "command": "npx",
            "args": ["-y", "@cloudflare/mcp-server-cloudflare"],
            "env": {
                "CLOUDFLARE_API_TOKEN": "<your-token>"
            },
            "category": "Infrastructure",
            "transport": "stdio"
        },
        "raycast": {
            "name": "Raycast",
            "description": "Access Raycast AI commands and notes",
            "command": "npx",
            "args": ["-y", "@raycast/mcp-server-raycast"],
            "category": "Productivity",
            "transport": "stdio"
        }
    }
    
    # Python-based MCP Servers
    PYTHON_SERVERS = {
        "fastmcp-demo": {
            "name": "FastMCP Demo",
            "description": "Example FastMCP server",
            "command": "python",
            "args": ["-m", "fastmcp"],
            "category": "Core",
            "transport": "stdio"
        },
        "qdrant": {
            "name": "Qdrant Vector DB",
            "description": "Vector database operations",
            "command": "uvx",
            "args": ["mcp-server-qdrant"],
            "category": "Database",
            "transport": "stdio"
        },
        "snowflake": {
            "name": "Snowflake",
            "description": "Query Snowflake data warehouse",
            "command": "uvx",
            "args": ["mcp-server-snowflake"],
            "env": {
                "SNOWFLAKE_ACCOUNT": "<your-account>",
                "SNOWFLAKE_USER": "<your-user>",
                "SNOWFLAKE_PASSWORD": "<your-password>"
            },
            "category": "Database",
            "transport": "stdio"
        }
    }
    
    @classmethod
    def get_all_servers(cls) -> Dict[str, Dict[str, Any]]:
        """Get all available MCP servers"""
        all_servers = {}
        all_servers.update(cls.SERVERS)
        all_servers.update(cls.PYTHON_SERVERS)
        return all_servers
    
    @classmethod
    def get_server_config(cls, server_id: str) -> Dict[str, Any]:
        """Get configuration for a specific server"""
        all_servers = cls.get_all_servers()
        return all_servers.get(server_id)
    
    @classmethod
    def get_servers_by_category(cls, category: str) -> Dict[str, Dict[str, Any]]:
        """Get all servers in a specific category"""
        all_servers = cls.get_all_servers()
        return {
            sid: config for sid, config in all_servers.items()
            if config.get('category') == category
        }
    
    @classmethod
    def get_categories(cls) -> List[str]:
        """Get all unique categories"""
        all_servers = cls.get_all_servers()
        categories = set()
        for config in all_servers.values():
            if 'category' in config:
                categories.add(config['category'])
        return sorted(list(categories))
    
    @classmethod
    def generate_claude_config(cls, server_ids: List[str]) -> Dict[str, Any]:
        """Generate Claude Desktop configuration for selected servers"""
        config = {
            "mcpServers": {}
        }
        
        all_servers = cls.get_all_servers()
        for sid in server_ids:
            if sid in all_servers:
                server = all_servers[sid]
                config["mcpServers"][sid] = {
                    "command": server["command"],
                    "args": server["args"]
                }
                if "env" in server:
                    config["mcpServers"][sid]["env"] = server["env"]
        
        return config
    
    @classmethod
    def export_config_json(cls, server_ids: List[str], filepath: str = None) -> str:
        """Export configuration to JSON file"""
        config = cls.generate_claude_config(server_ids)
        json_str = json.dumps(config, indent=2)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
        
        return json_str


# Example usage
if __name__ == "__main__":
    # Get all servers
    all_servers = MCPServerConfig.get_all_servers()
    print(f"Total servers available: {len(all_servers)}")
    
    # Get categories
    categories = MCPServerConfig.get_categories()
    print(f"\nCategories: {categories}")
    
    # Generate config for selected servers
    selected = ["filesystem", "github", "brave-search"]
    config = MCPServerConfig.generate_claude_config(selected)
    print(f"\nGenerated config:\n{json.dumps(config, indent=2)}")
