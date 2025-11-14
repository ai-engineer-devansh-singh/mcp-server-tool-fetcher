"""
MCP Client wrapper for connecting to servers and retrieving tools.
"""
from typing import Any, Dict, List, Optional

from mcp_use import MCPClient
from rich.console import Console
from rich.table import Table

from config import MCPServerConfig

console = Console()


class MCPToolLister:
    """Connect to MCP servers and list available tools."""
    
    def __init__(self):
        self.client: Optional[MCPClient] = None
        self.server_names: List[str] = []
    
    def _build_client_config(self, servers: Dict[str, MCPServerConfig]) -> Dict[str, Any]:
        """
        Build MCPClient configuration from server configs.
        
        Args:
            servers: Dictionary of server configurations
            
        Returns:
            Configuration dictionary for MCPClient
        """
        config = {"mcpServers": {}}
        
        for name, server_config in servers.items():
            server_def = {
                "command": server_config.command,
                "args": server_config.args,
            }
            if server_config.env:
                server_def["env"] = server_config.env
            
            config["mcpServers"][name] = server_def
            self.server_names.append(name)
            
            # Show resolved command path
            console.print(f"[dim]  {name}: {server_config.command}[/dim]")
        
        return config
    
    async def connect_to_servers(self, servers: Dict[str, MCPServerConfig]) -> None:
        """
        Connect to all MCP servers using MCPClient.
        
        Args:
            servers: Dictionary of server configurations
            
        Raises:
            Exception: If connection fails
        """
        try:
            # Build config dict for MCPClient
            config = self._build_client_config(servers)
            
            console.print(f"\n[cyan]Connecting to {len(servers)} server(s)...[/cyan]")
            
            # Create client and establish sessions
            self.client = MCPClient(config)
            await self.client.create_all_sessions()
            
            console.print(f"[green]✓ Connected to all servers[/green]")
            
        except Exception as e:
            console.print(f"[red]✗ Failed to connect: {e}[/red]")
            raise
    
    @staticmethod
    def _extract_input_schema(tool: Any) -> Dict[str, Any]:
        """
        Extract input schema from a tool object.
        
        Args:
            tool: Tool object with potential inputSchema attribute
            
        Returns:
            Dictionary representation of the input schema
        """
        if not hasattr(tool, 'inputSchema'):
            return {}
        
        schema = tool.inputSchema
        
        # Handle different schema types
        if isinstance(schema, dict):
            return schema
        if hasattr(schema, 'model_dump'):
            return schema.model_dump()
        if hasattr(schema, '__dict__'):
            return schema.__dict__
        
        return {}
    
    async def get_tools_from_server(self, server_name: str) -> List[Dict[str, Any]]:
        """
        Get list of tools from a specific MCP server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            List of tool definitions as dictionaries
        """
        try:
            session = self.client.get_session(server_name)
            result = await session.list_tools()
            
            # Handle different result formats
            tool_list = result.tools if hasattr(result, 'tools') else result
            
            # Convert Tool objects to dictionaries
            return [
                {
                    "name": getattr(tool, 'name', str(tool)),
                    "description": getattr(tool, 'description', "No description"),
                    "inputSchema": self._extract_input_schema(tool)
                }
                for tool in tool_list
            ]
            
        except Exception as e:
            console.print(f"[red]Error listing tools from {server_name}: {e}[/red]")
            return []
    
    async def list_all_tools(self, servers: Dict[str, MCPServerConfig]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Connect to all servers and list their tools.
        
        Args:
            servers: Dictionary of server configurations
            
        Returns:
            Dictionary mapping server names to their tool lists
        """
        all_tools = {}
        
        try:
            await self.connect_to_servers(servers)
            
            # Get tools from each server
            for name in self.server_names:
                tools = await self.get_tools_from_server(name)
                all_tools[name] = tools
                console.print(f"[green]Found {len(tools)} tool(s) in {name}[/green]")
        
        except Exception as e:
            console.print(f"[red]Error during tool listing: {e}[/red]")
        
        return all_tools
    
    async def close_all_connections(self) -> None:
        """Close all active MCP client connections."""
        if self.client:
            try:
                await self.client.close_all_sessions()
                console.print(f"[dim]Closed all connections[/dim]")
            except Exception as e:
                console.print(f"[red]Error closing connections: {e}[/red]")
            finally:
                self.client = None
                self.server_names.clear()
    
    @staticmethod
    def _format_parameters(input_schema: Dict[str, Any]) -> str:
        """
        Format tool parameters for display.
        
        Args:
            input_schema: Tool's input schema
            
        Returns:
            Formatted parameter string
        """
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])
        
        if not properties:
            return "None"
        
        param_info = [
            f"{name} ({details.get('type', 'any')}, "
            f"{'required' if name in required else 'optional'})"
            for name, details in properties.items()
        ]
        
        return "\n".join(param_info)
    
    @classmethod
    def display_tools(cls, all_tools: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        Display tools in formatted tables.
        
        Args:
            all_tools: Dictionary mapping server names to tool lists
        """
        for server_name, tools in all_tools.items():
            if not tools:
                console.print(f"\n[yellow]No tools found for server: {server_name}[/yellow]")
                continue
            
            console.print(f"\n[bold cyan]Server: {server_name}[/bold cyan]")
            console.print(f"[dim]Total tools: {len(tools)}[/dim]\n")
            
            # Create and populate table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Tool Name", style="cyan", no_wrap=True)
            table.add_column("Description", style="white")
            table.add_column("Parameters", style="yellow")
            
            for tool in tools:
                name = tool.get("name", "Unknown")
                description = tool.get("description", "No description")
                params_str = cls._format_parameters(tool.get("inputSchema", {}))
                
                table.add_row(name, description, params_str)
            
            console.print(table)
