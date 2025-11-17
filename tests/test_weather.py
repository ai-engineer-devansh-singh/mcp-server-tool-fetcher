"""
Test with weather MCP server (AccuWeather API)
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
    with open("test_weather.json", "r") as f:
        config_json = f.read()
    
    console.print("[cyan]Testing Weather MCP Server...[/cyan]\n")
    
    try:
        parser = ConfigParser()
        servers = parser.parse_config(config_json, auto_resolve=True)
        
        console.print(f"[green]✓ Found {len(servers)} server(s)[/green]")
        
        console.print("\n[bold]Configured servers:[/bold]")
        for name, config in servers.items():
            console.print(f"  • {name}")
            console.print(f"    Command: {config.command}")
            console.print(f"    Args: {config.args}")
            console.print(f"    Env vars: {list(config.env.keys()) if config.env else 'None'}")
        
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
            
            # Try to execute a weather tool if available
            if all_tools.get('weather'):
                console.print("\n[cyan]Testing weather tool execution...[/cyan]")
                
                # Get the first available tool
                first_tool = all_tools['weather'][0] if all_tools['weather'] else None
                
                if first_tool:
                    tool_name = first_tool['name']
                    console.print(f"[yellow]Executing tool: {tool_name}[/yellow]")
                    
                    # Try to call the tool with sample arguments
                    session = lister.client.get_session('weather')
                    
                    # Different possible argument structures
                    test_args = [
                        {"location": "London"},
                        {"city": "London"},
                        {"query": "London"},
                        {}
                    ]
                    
                    for args in test_args:
                        try:
                            console.print(f"[dim]Trying with args: {args}[/dim]")
                            result = await session.call_tool(tool_name, args)
                            
                            console.print(f"[green]✓ Tool executed successfully![/green]")
                            console.print(f"[bold]Result:[/bold]")
                            
                            if hasattr(result, 'content') and result.content:
                                for item in result.content:
                                    if hasattr(item, 'text'):
                                        console.print(item.text)
                                    else:
                                        console.print(str(item))
                            else:
                                console.print(str(result))
                            
                            break  # Success, stop trying
                            
                        except Exception as e:
                            console.print(f"[yellow]Failed with {args}: {str(e)[:100]}[/yellow]")
                            continue
            
        finally:
            console.print("\n[cyan]Closing connections...[/cyan]")
            await lister.close_all_connections()
    
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
