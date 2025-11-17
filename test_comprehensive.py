"""
Comprehensive test with multiple MCP servers including Docker and UV-based
Tests various types of MCP servers working together
"""
import asyncio
from rich.console import Console
from config import ConfigParser
from mcp_client import MCPToolLister

console = Console()


async def main():
    # Read config from file
    with open("test_comprehensive.json", "r") as f:
        config_json = f.read()
    
    console.print("[bold cyan]Comprehensive MCP Server Test[/bold cyan]\n")
    console.print("[yellow]Testing multiple server types:[/yellow]")
    console.print("  • Docker containerization (npx)")
    console.print("  • Python-based servers (uvx)")
    console.print("  • Node.js-based servers (npx)")
    console.print("[dim]Note: Docker Desktop should be running for full functionality[/dim]\n")
    
    try:
        parser = ConfigParser()
        servers = parser.parse_config(config_json, auto_resolve=True)
        
        console.print(f"[green]✓ Parsed {len(servers)} server(s)[/green]")
        
        console.print("\n[bold]Configured servers:[/bold]")
        for name in servers.keys():
            console.print(f"  • {name}")
        
        console.print("\n[cyan]Connecting to all MCP servers...[/cyan]")
        lister = MCPToolLister()
        
        try:
            all_tools = await lister.list_all_tools(servers)
            
            console.print("\n" + "="*80)
            console.print("[bold green]Server Summary[/bold green]")
            console.print("="*80)
            
            # Show tool counts per server
            for server_name, tools in all_tools.items():
                if tools:
                    console.print(f"  • [cyan]{server_name}[/cyan]: [green]{len(tools)} tools[/green]")
                else:
                    console.print(f"  • [cyan]{server_name}[/cyan]: [red]Connection failed or no tools[/red]")
            
            total_tools = sum(len(tools) for tools in all_tools.values())
            console.print(f"\n[bold green]Total tools available: {total_tools}[/bold green]")
            
            # Display detailed tool information
            console.print("\n" + "="*80)
            console.print("[bold green]Detailed Tool Listings[/bold green]")
            console.print("="*80)
            
            lister.display_tools(all_tools)
            
        finally:
            console.print("\n[cyan]Closing connections...[/cyan]")
            try:
                await lister.close_all_connections()
            except Exception as close_error:
                console.print(f"[dim]Cleanup completed with minor warnings[/dim]")
    
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
