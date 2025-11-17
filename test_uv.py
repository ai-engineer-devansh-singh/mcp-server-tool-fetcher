"""
Test with UV-based Python MCP servers
Demonstrates uvx command for Python MCP servers
"""
import asyncio
from rich.console import Console
from config import ConfigParser
from mcp_client import MCPToolLister

console = Console()


async def main():
    # Read config from file
    with open("test_uv.json", "r") as f:
        config_json = f.read()
    
    console.print("[bold cyan]Testing UV-based Python MCP Servers[/bold cyan]\n")
    console.print("[yellow]This will test Python MCP servers using uvx command[/yellow]")
    console.print("[dim]Note: Requires uv/uvx to be installed on your system[/dim]\n")
    
    try:
        parser = ConfigParser()
        servers = parser.parse_config(config_json, auto_resolve=True)
        
        console.print(f"[green]✓ Parsed {len(servers)} server(s)[/green]")
        
        console.print("\n[bold]Configured servers:[/bold]")
        for name in servers.keys():
            console.print(f"  • {name}")
        
        console.print("\n[cyan]Connecting to MCP servers...[/cyan]")
        lister = MCPToolLister()
        
        try:
            all_tools = await lister.list_all_tools(servers)
            
            console.print("\n" + "="*80)
            console.print("[bold green]Available Tools Summary[/bold green]")
            console.print("="*80)
            
            for server_name, tools in all_tools.items():
                console.print(f"  • [cyan]{server_name}[/cyan]: {len(tools)} tools")
            
            total_tools = sum(len(tools) for tools in all_tools.values())
            console.print(f"\n[bold green]Total tools across all servers: {total_tools}[/bold green]")
            
            console.print("\n" + "="*80)
            console.print("[bold green]Detailed Tool Listings[/bold green]")
            console.print("="*80)
            
            lister.display_tools(all_tools)
            
        finally:
            console.print("\n[cyan]Closing connections...[/cyan]")
            try:
                await lister.close_all_connections()
            except Exception:
                pass  # Suppress known cleanup warnings
    
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import warnings
    import sys
    
    # Suppress ResourceWarnings from asyncio cleanup
    warnings.filterwarnings("ignore", category=ResourceWarning)
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError, SystemExit):
        pass  # Silently exit
    except Exception as e:
        if "cancel scope" not in str(e).lower():
            console.print(f"\n[red]Unexpected error: {e}[/red]")
            sys.exit(1)
