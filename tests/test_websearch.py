"""
Test Web Search MCP with OpenAI API Integration
Demonstrates web search capabilities with AI-powered content generation
"""
import asyncio
import os
import sys
import warnings
from typing import Dict, List, Any
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from config import ConfigParser
from mcp_client import MCPToolLister
from mcp_use import MCPClient

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

console = Console()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")


class WebSearchWithAI:
    """Integrate web search MCP tools with OpenAI API."""
    
    def __init__(self):
        self.client = None
        self.tools = []
        self.openai_client = None
        
    async def initialize(self, servers: Dict[str, Any]):
        """Initialize MCP client and connect to servers."""
        try:
            # Build config for MCPClient
            config = {"mcpServers": {}}
            for name, server_config in servers.items():
                server_def = {
                    "command": server_config.command,
                    "args": server_config.args,
                }
                if server_config.env:
                    server_def["env"] = server_config.env
                config["mcpServers"][name] = server_def
            
            # Create client and establish sessions
            self.client = MCPClient(config)
            await self.client.create_all_sessions()
            console.print("[green]✓ Connected to web-search MCP server[/green]")
            
            # Get available tools
            session = self.client.get_session("web-search")
            result = await session.list_tools()
            self.tools = result.tools if hasattr(result, 'tools') else result
            console.print(f"[green]✓ Found {len(self.tools)} tools[/green]")
            
            return True
        except Exception as e:
            console.print(f"[red]✗ Failed to initialize: {e}[/red]")
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an MCP tool with given arguments."""
        try:
            session = self.client.get_session("web-search")
            result = await session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            console.print(f"[red]Error calling tool {tool_name}: {e}[/red]")
            return None
    
    def format_tool_for_openai(self, tool: Any) -> Dict[str, Any]:
        """Format MCP tool for OpenAI function calling."""
        tool_dict = {
            "type": "function",
            "function": {
                "name": getattr(tool, 'name', str(tool)),
                "description": getattr(tool, 'description', "No description"),
            }
        }
        
        # Extract input schema
        if hasattr(tool, 'inputSchema'):
            schema = tool.inputSchema
            if isinstance(schema, dict):
                tool_dict["function"]["parameters"] = schema
            elif hasattr(schema, 'model_dump'):
                tool_dict["function"]["parameters"] = schema.model_dump()
            elif hasattr(schema, '__dict__'):
                tool_dict["function"]["parameters"] = schema.__dict__
        
        return tool_dict
    
    async def search_and_generate(self, query: str, search_engine: str = "duckduckgo"):
        """
        Perform web search and generate content using OpenAI.
        
        Args:
            query: Search query
            search_engine: Search engine to use (duckduckgo, bing, or exa)
        """
        console.print(f"\n[bold cyan]Searching for: {query}[/bold cyan]")
        console.print(f"[dim]Using search engine: {search_engine}[/dim]\n")
        
        # Step 1: Perform web search using MCP tool
        search_result = await self.call_tool("search", {
            "query": query,
            "engines": [search_engine],  # Note: parameter is 'engines' (array) not 'engine'
            "limit": 5
        })
        
        if not search_result:
            console.print("[red]Search failed[/red]")
            return
        
        # Display search results
        console.print("[bold green]Search Results:[/bold green]")
        search_data = self._extract_search_data(search_result)
        self._display_search_results(search_data)
        
        # Step 2: Use OpenAI to generate content based on search results
        if not OPENAI_API_KEY:
            console.print("\n[yellow]⚠ OPENAI_API_KEY not set. Skipping AI generation.[/yellow]")
            console.print("[dim]Set OPENAI_API_KEY environment variable to enable AI features.[/dim]")
            return
        
        console.print("\n[cyan]Generating AI-powered summary...[/cyan]")
        await self._generate_content_with_openai(query, search_data)
    
    def _extract_search_data(self, search_result: Any) -> List[Dict[str, Any]]:
        """Extract search results from MCP tool response."""
        try:
            import json
            
            # Handle different result formats
            if hasattr(search_result, 'content'):
                content = search_result.content
                if isinstance(content, list) and len(content) > 0:
                    first_item = content[0]
                    if hasattr(first_item, 'text'):
                        text_content = first_item.text
                        # Try to parse as JSON
                        try:
                            parsed = json.loads(text_content)
                            # If it's already a list, return it
                            if isinstance(parsed, list):
                                return parsed
                            # If it's a dict with results, return those
                            if isinstance(parsed, dict) and 'results' in parsed:
                                return parsed['results']
                            # Single result, wrap in list
                            return [parsed]
                        except json.JSONDecodeError:
                            # Not JSON, treat as plain text result
                            return [{"title": "Search Result", "snippet": text_content, "url": ""}]
            
            # Handle string response
            if isinstance(search_result, str):
                try:
                    parsed = json.loads(search_result)
                    if isinstance(parsed, list):
                        return parsed
                    if isinstance(parsed, dict) and 'results' in parsed:
                        return parsed['results']
                    return [parsed]
                except json.JSONDecodeError:
                    return [{"title": "Search Result", "snippet": search_result, "url": ""}]
            
            # Fallback: try to convert to dict
            if hasattr(search_result, '__dict__'):
                return [search_result.__dict__]
            
            return []
        except Exception as e:
            console.print(f"[red]Error extracting search data: {e}[/red]")
            import traceback
            traceback.print_exc()
            return []
    
    def _display_search_results(self, results: List[Dict[str, Any]]):
        """Display search results in formatted output."""
        if not results:
            console.print("[yellow]No results found[/yellow]")
            return
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            url = result.get('url', 'No URL')
            snippet = result.get('snippet', result.get('description', 'No description'))
            
            console.print(f"\n[bold]{i}. {title}[/bold]")
            console.print(f"[blue]{url}[/blue]")
            console.print(f"[dim]{snippet}[/dim]")
    
    async def _generate_content_with_openai(self, query: str, search_data: List[Dict[str, Any]]):
        """Generate content using OpenAI API based on search results."""
        try:
            # Import OpenAI only if API key is available
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            
            # Prepare context from search results
            context = self._prepare_search_context(search_data)
            
            # Create prompt
            prompt = f"""Based on the following search results about "{query}", create a comprehensive and informative summary:

{context}

Provide a well-structured summary that:
1. Answers the search query clearly
2. Synthesizes information from multiple sources
3. Highlights key facts and insights
4. Is written in a clear, engaging style
"""
            
            # Call OpenAI API
            response = await client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates comprehensive summaries based on web search results."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Display generated content
            generated_text = response.choices[0].message.content
            console.print(Panel(
                Markdown(generated_text),
                title="[bold green]AI-Generated Summary[/bold green]",
                border_style="green"
            ))
            
            # Display usage stats
            usage = response.usage
            console.print(f"\n[dim]Tokens used: {usage.total_tokens} (prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})[/dim]")
            
        except ImportError:
            console.print("[red]OpenAI library not installed. Install with: pip install openai[/red]")
        except Exception as e:
            console.print(f"[red]Error generating content: {e}[/red]")
    
    def _prepare_search_context(self, search_data: List[Dict[str, Any]]) -> str:
        """Prepare search results as context for OpenAI."""
        context_parts = []
        for i, result in enumerate(search_data, 1):
            title = result.get('title', 'No title')
            url = result.get('url', '')
            snippet = result.get('snippet', result.get('description', ''))
            
            context_parts.append(f"Source {i}: {title}\nURL: {url}\n{snippet}\n")
        
        return "\n---\n".join(context_parts)
    
    async def close(self):
        """Close all connections."""
        if self.client:
            try:
                await self.client.close_all_sessions()
                console.print("[dim]Closed all connections[/dim]")
            except Exception as e:
                if "cancel scope" not in str(e).lower():
                    console.print(f"[red]Error closing connections: {e}[/red]")


async def test_list_tools():
    """Test 1: List all available web search tools."""
    console.print(Panel.fit(
        "[bold]Test 1: List Web Search MCP Tools[/bold]",
        border_style="cyan"
    ))
    
    with open("test_websearch.json", "r") as f:
        config_json = f.read()
    
    try:
        parser = ConfigParser()
        servers = parser.parse_config(config_json, auto_resolve=True)
        
        console.print(f"[green]✓ Found {len(servers)} server(s)[/green]")
        
        lister = MCPToolLister()
        try:
            all_tools = await lister.list_all_tools(servers)
            
            console.print("\n" + "="*80)
            console.print("[bold green]Available Web Search Tools[/bold green]")
            console.print("="*80)
            
            lister.display_tools(all_tools)
            
            total_tools = sum(len(tools) for tools in all_tools.values())
            console.print(f"\n[bold green]Total tools available: {total_tools}[/bold green]")
            
        finally:
            await lister.close_all_connections()
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


async def test_search_and_generate():
    """Test 2: Perform search and generate content with OpenAI."""
    console.print(Panel.fit(
        "[bold]Test 2: Web Search + OpenAI Content Generation[/bold]",
        border_style="cyan"
    ))
    
    with open("test_websearch.json", "r") as f:
        config_json = f.read()
    
    try:
        parser = ConfigParser()
        servers = parser.parse_config(config_json, auto_resolve=True)
        
        ws_ai = WebSearchWithAI()
        if not await ws_ai.initialize(servers):
            return
        
        try:
            # Test searches
            test_queries = [
                ("latest events in Jaipur Rajasthan", "duckduckgo"),
            ]
            
            for query, engine in test_queries:
                await ws_ai.search_and_generate(query, engine)
                console.print("\n" + "="*80 + "\n")
        
        finally:
            await ws_ai.close()
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


async def test_openai_function_calling():
    """Test 3: Use web search tools with OpenAI function calling."""
    console.print(Panel.fit(
        "[bold]Test 3: OpenAI Function Calling with Web Search[/bold]",
        border_style="cyan"
    ))
    
    if not OPENAI_API_KEY:
        console.print("[yellow]⚠ OPENAI_API_KEY not set. Skipping this test.[/yellow]")
        console.print("[dim]Set OPENAI_API_KEY environment variable to enable AI features.[/dim]")
        return
    
    with open("test_websearch.json", "r") as f:
        config_json = f.read()
    
    try:
        from openai import AsyncOpenAI
        
        parser = ConfigParser()
        servers = parser.parse_config(config_json, auto_resolve=True)
        
        ws_ai = WebSearchWithAI()
        if not await ws_ai.initialize(servers):
            return
        
        try:
            # Prepare tools for OpenAI
            openai_tools = [ws_ai.format_tool_for_openai(tool) for tool in ws_ai.tools]
            
            console.print(f"[green]✓ Prepared {len(openai_tools)} tools for OpenAI[/green]")
            
            # Create OpenAI client
            openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            
            # User query
            user_query = "What are the latest events happening in Jaipur, Rajasthan? Please search and summarize."
            
            console.print(f"\n[bold cyan]User Query:[/bold cyan] {user_query}\n")
            
            # First API call - let OpenAI decide to use tools
            messages = [
                {"role": "system", "content": "You are a helpful assistant with access to web search tools. Use them to provide accurate, up-to-date information."},
                {"role": "user", "content": user_query}
            ]
            
            response = await openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                tools=openai_tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            
            # Check if OpenAI wants to call a tool
            if response_message.tool_calls:
                console.print("[cyan]OpenAI is calling web search tools...[/cyan]\n")
                
                messages.append(response_message)
                
                # Execute each tool call
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = eval(tool_call.function.arguments)
                    
                    console.print(f"[bold]Calling tool:[/bold] {function_name}")
                    console.print(f"[dim]Arguments: {function_args}[/dim]")
                    
                    # Call the MCP tool
                    tool_result = await ws_ai.call_tool(function_name, function_args)
                    
                    # Add tool response to messages
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(tool_result)
                    })
                
                # Second API call - get final response
                console.print("\n[cyan]Getting final response from OpenAI...[/cyan]\n")
                
                final_response = await openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=messages
                )
                
                final_message = final_response.choices[0].message.content
                
                console.print(Panel(
                    Markdown(final_message),
                    title="[bold green]Final AI Response[/bold green]",
                    border_style="green"
                ))
            else:
                # No tool call needed
                console.print(Panel(
                    response_message.content,
                    title="[bold yellow]Direct Response (No Tool Call)[/bold yellow]",
                    border_style="yellow"
                ))
        
        finally:
            await ws_ai.close()
    
    except ImportError:
        console.print("[red]OpenAI library not installed. Install with: pip install openai[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests."""
    console.print("[bold cyan]Web Search MCP + OpenAI Integration Tests[/bold cyan]\n")
    
    # Show configuration info
    console.print("[bold]Configuration:[/bold]")
    console.print(f"  OpenAI API Key: {'✓ Set' if OPENAI_API_KEY else '✗ Not set'}")
    console.print(f"  OpenAI Model: {OPENAI_MODEL}")
    console.print()
    
    # Run tests
    await test_list_tools()
    console.print("\n" + "="*80 + "\n")
    
    await test_search_and_generate()
    console.print("\n" + "="*80 + "\n")
    
    await test_openai_function_calling()


if __name__ == "__main__":
    asyncio.run(main())
