"""
Complete MCP Server Test Suite
Tests all available MCP server formats: NPX, UVX, Docker
"""
import asyncio
from rich.console import Console
from rich.table import Table
from config import ConfigParser
from mcp_client import MCPToolLister

console = Console()


async def test_server(config_file: str, server_type: str) -> dict:
    """Test a single server configuration."""
    try:
        with open(config_file, "r") as f:
            config_json = f.read()
        
        parser = ConfigParser()
        servers = parser.parse_config(config_json, auto_resolve=True)
        
        lister = MCPToolLister()
        try:
            all_tools = await lister.list_all_tools(servers)
            total_tools = sum(len(tools) for tools in all_tools.values())
            
            return {
                "status": "✅ Pass",
                "servers": len(servers),
                "tools": total_tools,
                "type": server_type,
                "config": config_file
            }
        finally:
            try:
                await lister.close_all_connections()
            except:
                pass
    except Exception as e:
        return {
            "status": "❌ Fail",
            "servers": 0,
            "tools": 0,
            "type": server_type,
            "config": config_file,
            "error": str(e)
        }


async def main():
    console.print("[bold cyan]═" * 40 + "[/bold cyan]")
    console.print("[bold cyan]  MCP Server Complete Test Suite[/bold cyan]")
    console.print("[bold cyan]═" * 40 + "[/bold cyan]\n")
    
    # Define test configurations
    tests = [
        ("test_config.json", "NPX - Playwright"),
        ("test_docker.json", "NPX - Docker/Kubernetes"),
        ("test_memory.json", "NPX - Memory/KG"),
        ("test_git.json", "NPX - Git Operations"),
        ("test_uv.json", "UVX - Python Servers"),
        ("test_comprehensive.json", "Mixed - All Types"),
    ]
    
    console.print("[yellow]Running comprehensive tests...[/yellow]\n")
    
    results = []
    for config_file, server_type in tests:
        console.print(f"[cyan]Testing {server_type}...[/cyan]")
        result = await test_server(config_file, server_type)
        results.append(result)
        console.print(f"  {result['status']} {server_type}\n")
    
    # Display summary table
    console.print("\n[bold cyan]═" * 40 + "[/bold cyan]")
    console.print("[bold green]Test Results Summary[/bold green]")
    console.print("[bold cyan]═" * 40 + "[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Server Type", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Servers", justify="center")
    table.add_column("Tools", justify="center")
    table.add_column("Config File", style="dim")
    
    for result in results:
        status_color = "green" if "✅" in result["status"] else "red"
        table.add_row(
            result["type"],
            f"[{status_color}]{result['status']}[/{status_color}]",
            str(result["servers"]),
            str(result["tools"]),
            result["config"]
        )
    
    console.print(table)
    
    # Calculate statistics
    total_tests = len(results)
    passed_tests = sum(1 for r in results if "✅" in r["status"])
    total_tools = sum(r["tools"] for r in results)
    
    console.print(f"\n[bold]Statistics:[/bold]")
    console.print(f"  • Total Tests: {total_tests}")
    console.print(f"  • Passed: [green]{passed_tests}[/green]")
    console.print(f"  • Failed: [red]{total_tests - passed_tests}[/red]")
    console.print(f"  • Total Tools Discovered: [cyan]{total_tools}[/cyan]")
    
    console.print("\n[bold cyan]═" * 40 + "[/bold cyan]")
    console.print("[bold green]✨ Test Suite Complete![/bold green]")
    console.print("[bold cyan]═" * 40 + "[/bold cyan]\n")


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=ResourceWarning)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Test suite interrupted by user[/yellow]")
