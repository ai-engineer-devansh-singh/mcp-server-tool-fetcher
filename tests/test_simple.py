"""
Simple test script to demonstrate MCP Tool Lister functionality.
"""
import asyncio
import sys
from pathlib import Path

from rich.console import Console

from config import ConfigParser
from mcp_client import MCPToolLister

console = Console()


async def run_test(config_file: str = "test_config.json") -> None:
    """
    Run the MCP Tool Lister test.
    
    Args:
        config_file: Path to the configuration file
    """
    try:
        # Read config from file
        config_path = Path(config_file)
        if not config_path.exists():
            console.print(f"[red]Error: Config file '{config_file}' not found[/red]")
            return
        
        config_json = config_path.read_text(encoding='utf-8')
        
        console.print("[cyan]Testing MCP Tool Lister...[/cyan]\n")
        
        # Parse configuration
        console.print("[cyan]Parsing configuration...[/cyan]")
        parser = ConfigParser()
        servers = parser.parse_config(config_json, auto_resolve=True)
        
        console.print(f"[green]✓ Found {len(servers)} server(s)[/green]")
        
        # List server names
        console.print("\n[bold]Configured servers:[/bold]")
        for name in servers.keys():
            console.print(f"  • {name}")
        
        # Connect to servers and list tools
        console.print("\n[cyan]Connecting to MCP servers...[/cyan]")
        lister = MCPToolLister()
        
        try:
            all_tools = await lister.list_all_tools(servers)
            
            # Display results
            console.print("\n" + "=" * 80)
            console.print("[bold green]Available Tools[/bold green]")
            console.print("=" * 80)
            
            lister.display_tools(all_tools)
            
            # Summary
            total_tools = sum(len(tools) for tools in all_tools.values())
            console.print(f"\n[bold green]Total tools across all servers: {total_tools}[/bold green]")
            
        finally:
            console.print("\n[cyan]Closing connections...[/cyan]")
            await lister.close_all_connections()
    
    except ValueError as e:
        console.print(f"\n[red]Configuration error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    console.print("[yellow]MCP Tool Lister - Test Mode[/yellow]")
    console.print("[dim]Reading configuration from test_config.json[/dim]\n")
    
    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)


if __name__ == "__main__":
    main()
