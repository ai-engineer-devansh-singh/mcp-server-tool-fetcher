"""
Test Render-compatible MCP server configuration
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from config import ConfigParser
from mcp_client import MCPToolLister

console = Console()


async def main():
    # Read config from file
    with open("test_render_config.json", "r") as f:
        config_json = f.read()
    
    console.print("[cyan]Testing Render-Compatible MCP Servers (NPX-based)...[/cyan]\n")
    console.print("[dim]These servers work on Render deployment[/dim]\n")
    
    try:
        parser = ConfigParser()
        servers = parser.parse_config(config_json, auto_resolve=True)
        
        console.print(f"[green]✓ Found {len(servers)} server(s)[/green]")
        
        console.print("\n[bold]Configured servers:[/bold]")
        for name, config in servers.items():
            console.print(f"  • {name}")
            console.print(f"    Command: {config.command}")
            console.print(f"    Args: {config.args}")
        
        console.print("\n[cyan]Connecting to MCP servers...[/cyan]")
        lister = MCPToolLister()
        
        try:
            all_tools = await lister.list_all_tools(servers)
            
            console.print("\n" + "="*80)
            console.print("[bold green]Available Tools[/bold green]")
            console.print("="*80)
            
            lister.display_tools(all_tools)
            
            total_tools = sum(len(tools) for tools in all_tools.values())
            console.print(f"\n[bold green]Total tools across all servers: {total_tools}[/bold green]")
            
            console.print("\n[green]✓ All servers working - ready for Render deployment![/green]")
            
        finally:
            console.print("\n[cyan]Closing connections...[/cyan]")
            await lister.close_all_connections()
    
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        console.print("[yellow]This configuration may not work on Render[/yellow]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
