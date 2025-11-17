"""
Test with Git MCP server (NPX-based)
Demonstrates Git operations through MCP
"""
import asyncio
from rich.console import Console
from config import ConfigParser
from mcp_client import MCPToolLister

console = Console()


async def main():
    # Read config from file
    with open("test_git.json", "r") as f:
        config_json = f.read()
    
    console.print("[bold cyan]Testing Git MCP Server[/bold cyan]\n")
    console.print("[yellow]This will test Git operations through MCP[/yellow]\n")
    
    try:
        parser = ConfigParser()
        servers = parser.parse_config(config_json, auto_resolve=True)
        
        console.print(f"[green]✓ Found {len(servers)} server(s)[/green]")
        
        console.print("\n[bold]Configured servers:[/bold]")
        for name in servers.keys():
            console.print(f"  • {name}")
        
        console.print("\n[cyan]Connecting to MCP servers...[/cyan]")
        lister = MCPToolLister()
        
        try:
            all_tools = await lister.list_all_tools(servers)
            
            console.print("\n" + "="*80)
            console.print("[bold green]Available Git Tools[/bold green]")
            console.print("="*80)
            
            lister.display_tools(all_tools)
            
            total_tools = sum(len(tools) for tools in all_tools.values())
            console.print(f"\n[bold green]Total tools available: {total_tools}[/bold green]")
            
        finally:
            console.print("\n[cyan]Closing connections...[/cyan]")
            await lister.close_all_connections()
    
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=ResourceWarning)
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        pass
