"""
Advanced Docker MCP Server Test
Tests both containerization-assist-mcp and native Docker operations
"""
import asyncio
import subprocess
from rich.console import Console
from config import ConfigParser
from mcp_client import MCPToolLister

console = Console()


def check_docker_status():
    """Check if Docker Desktop is running"""
    try:
        result = subprocess.run(
            ["docker", "ps"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


async def test_containerization_mcp():
    """Test containerization-assist-mcp server"""
    console.print("[bold cyan]Testing Containerization MCP Server[/bold cyan]\n")
    
    with open("test_docker.json", "r") as f:
        config_json = f.read()
    
    parser = ConfigParser()
    servers = parser.parse_config(config_json, auto_resolve=True)
    
    console.print(f"[green]✓ Parsed {len(servers)} server(s)[/green]")
    
    lister = MCPToolLister()
    try:
        all_tools = await lister.list_all_tools(servers)
        
        console.print("\n" + "="*80)
        console.print("[bold green]Containerization Tools[/bold green]")
        console.print("="*80)
        
        lister.display_tools(all_tools)
        
        total_tools = sum(len(tools) for tools in all_tools.values())
        console.print(f"\n[bold green]Total tools: {total_tools}[/bold green]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return False
    finally:
        try:
            await lister.close_all_connections()
        except Exception:
            pass


async def main():
    console.print("[bold yellow]Docker MCP Advanced Test Suite[/bold yellow]\n")
    
    # Check Docker status
    console.print("[cyan]Checking Docker Desktop status...[/cyan]")
    docker_running = check_docker_status()
    
    if docker_running:
        console.print("[green]✓ Docker Desktop is running[/green]\n")
    else:
        console.print("[yellow]⚠ Docker Desktop is not running[/yellow]")
        console.print("[dim]Some operations may be limited[/dim]\n")
    
    # Test MCP server
    console.print("="*80)
    await test_containerization_mcp()
    console.print("="*80)
    
    # Show Docker status
    console.print("\n[bold]Docker System Information:[/bold]")
    if docker_running:
        try:
            # Get Docker version
            result = subprocess.run(
                ["docker", "version", "--format", "{{.Server.Version}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                console.print(f"  Docker Version: {result.stdout.strip()}")
            
            # Count containers
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.ID}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                container_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                console.print(f"  Total Containers: {container_count}")
            
            # Count images
            result = subprocess.run(
                ["docker", "images", "--format", "{{.ID}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                image_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                console.print(f"  Total Images: {image_count}")
                
        except Exception as e:
            console.print(f"[dim]Could not retrieve Docker info: {e}[/dim]")
    else:
        console.print("  [yellow]Start Docker Desktop to see system information[/yellow]")
    
    console.print("\n[bold green]Test Complete![/bold green]")


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=ResourceWarning)
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        console.print("\n[yellow]Test interrupted[/yellow]")
