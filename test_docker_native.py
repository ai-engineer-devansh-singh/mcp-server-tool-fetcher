"""
Native Docker Operations Test
Uses built-in Copilot MCP Docker tools (requires Docker Desktop running)
"""
import asyncio
from rich.console import Console
from rich.table import Table

console = Console()


async def test_docker_operations():
    """Test native Docker operations using Copilot MCP tools"""
    console.print("[bold cyan]Testing Native Docker Operations[/bold cyan]\n")
    
    try:
        # Import the Docker MCP tools
        from mcp_copilot_conta_list_networks import mcp_copilot_conta_list_networks
        
        console.print("[cyan]Attempting to list Docker networks...[/cyan]")
        networks = await mcp_copilot_conta_list_networks()
        
        console.print(f"[green]✓ Found {len(networks)} network(s)[/green]\n")
        
        # Display networks
        if networks:
            table = Table(title="Docker Networks")
            table.add_column("Name", style="cyan")
            table.add_column("Driver", style="yellow")
            table.add_column("Scope", style="green")
            
            for network in networks:
                table.add_row(
                    network.get('Name', 'N/A'),
                    network.get('Driver', 'N/A'),
                    network.get('Scope', 'N/A')
                )
            
            console.print(table)
        
        return True
        
    except ImportError:
        console.print("[yellow]⚠ Docker MCP tools not available in this context[/yellow]")
        console.print("[dim]These tools are available when Docker Desktop is running[/dim]")
        return False
    except Exception as e:
        if "cannot find the file" in str(e).lower() or "connection" in str(e).lower():
            console.print("[red]✗ Docker Desktop is not running[/red]")
            console.print("[yellow]Please start Docker Desktop and try again[/yellow]")
        else:
            console.print(f"[red]Error: {e}[/red]")
        return False


async def main():
    console.print("[bold yellow]Native Docker MCP Test[/bold yellow]\n")
    console.print("[dim]This test requires Docker Desktop to be running[/dim]\n")
    
    success = await test_docker_operations()
    
    if success:
        console.print("\n[bold green]✓ Docker operations working correctly![/bold green]")
    else:
        console.print("\n[bold yellow]Docker Desktop Status:[/bold yellow]")
        console.print("  1. Make sure Docker Desktop is installed")
        console.print("  2. Start Docker Desktop")
        console.print("  3. Wait for it to fully start (Docker icon shows 'Running')")
        console.print("  4. Run this test again")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted[/yellow]")
