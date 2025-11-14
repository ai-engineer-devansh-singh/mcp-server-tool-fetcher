"""
MCP Tool Lister - Main Application
List all tools from MCP servers based on user configuration
"""
import asyncio
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from config import ConfigParser
from mcp_client import MCPToolLister

console = Console()


def print_banner():
    """Display application banner"""
    banner = """
[bold cyan]MCP Tool Lister[/bold cyan]
[dim]List all tools from your MCP servers[/dim]
    """
    console.print(Panel(banner, border_style="cyan"))


def get_config_input() -> str:
    """
    Get MCP configuration from user input
    
    Returns:
        JSON configuration string
    """
    console.print("\n[yellow]Paste your MCP configuration (JSON format)[/yellow]")
    console.print("[dim]Press Enter twice when done:[/dim]\n")
    
    lines = []
    empty_line_count = 0
    
    while True:
        try:
            line = input()
            if not line:
                empty_line_count += 1
                if empty_line_count >= 2:
                    break
            else:
                empty_line_count = 0
                lines.append(line)
        except EOFError:
            break
    
    return '\n'.join(lines)


def show_example_config():
    """Display an example configuration"""
    example = """{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest"
      ]
    },
    "fetch": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-fetch"
      ]
    }
  }
}"""
    console.print(Panel(example, title="[bold]Example Configuration[/bold]", border_style="green"))


async def main():
    """Main application entry point"""
    print_banner()
    
    # Ask if user wants to see example
    show_example = Prompt.ask(
        "\n[cyan]Would you like to see an example configuration?[/cyan]",
        choices=["y", "n"],
        default="y"
    )
    
    if show_example.lower() == 'y':
        show_example_config()
    
    # Get configuration from user
    config_json = get_config_input()
    
    if not config_json.strip():
        console.print("[red]No configuration provided. Exiting.[/red]")
        return
    
    try:
        # Parse configuration
        console.print("\n[cyan]Parsing configuration...[/cyan]")
        parser = ConfigParser()
        servers = parser.parse_config(config_json, auto_resolve=True)
        
        console.print(f"[green]✓ Found {len(servers)} server(s)[/green]")
        
        # Validate configuration
        issues = parser.validate_config(servers)
        if issues:
            console.print("\n[yellow]Configuration warnings:[/yellow]")
            for issue in issues:
                console.print(f"  - {issue}")
        
        # List server names with resolved commands
        console.print("\n[bold]Configured servers:[/bold]")
        for name, config in servers.items():
            console.print(f"  • [cyan]{name}[/cyan]")
        
        # Connect to servers and list tools
        console.print("\n[cyan]Connecting to MCP servers...[/cyan]")
        lister = MCPToolLister()
        
        try:
            all_tools = await lister.list_all_tools(servers)
            
            # Display tools
            console.print("\n" + "="*80)
            console.print("[bold green]Available Tools[/bold green]")
            console.print("="*80)
            
            lister.display_tools(all_tools)
            
            # Summary
            total_tools = sum(len(tools) for tools in all_tools.values())
            console.print(f"\n[bold green]Total tools across all servers: {total_tools}[/bold green]")
            
        finally:
            # Clean up connections
            console.print("\n[cyan]Closing connections...[/cyan]")
            await lister.close_all_connections()
    
    except ValueError as e:
        console.print(f"\n[red]Configuration error: {e}[/red]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
