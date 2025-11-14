"""
Configuration handler for MCP servers with automatic command resolution.
"""
import json
import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class MCPServerConfig:
    """Represents a single MCP server configuration."""
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)


class CommandResolver:
    """Resolve and normalize commands for different platforms."""
    
    # Command alternatives for fallback resolution
    COMMAND_ALTERNATIVES = {
        'uvx': ['uvx', 'uv'],
        'npx': ['npx', 'npm'],
        'python': ['python', 'python3', 'py'],
        'node': ['node', 'nodejs'],
    }
    
    @staticmethod
    def _get_windows_search_paths(command: str) -> List[str]:
        """Get platform-specific search paths for Windows."""
        username = os.getenv('USERNAME', '')
        return [
            f"C:/Users/{username}/AppData/Local/Programs/Python/Python313/Scripts/{command}.exe",
            f"C:/Users/{username}/AppData/Roaming/npm/{command}.cmd",
            f"C:/Program Files/nodejs/{command}.cmd",
        ]
    
    @staticmethod
    def find_command(command: str) -> Optional[str]:
        """
        Find the full path to a command.
        
        Args:
            command: Command name (e.g., 'uvx', 'npx', 'python')
            
        Returns:
            Full path to command or None if not found
        """
        # Return if already a valid full path
        if os.path.isfile(command):
            return command
        
        # Try system PATH first
        found = shutil.which(command)
        if found:
            return found
        
        # Try platform-specific locations
        if sys.platform == 'win32':
            for path in CommandResolver._get_windows_search_paths(command):
                if os.path.isfile(path):
                    return path
        
        return None
    
    @staticmethod
    def resolve_command(command: str) -> str:
        """
        Resolve command to full path, trying common alternatives.
        
        Args:
            command: Original command from config
            
        Returns:
            Resolved command path (original if not found)
        """
        # Return if already a valid full path
        if os.path.isfile(command):
            return command
        
        # Try to find the command as-is
        resolved = CommandResolver.find_command(command)
        if resolved:
            return resolved
        
        # Try common alternatives for known commands
        base_cmd = command.lower()
        if base_cmd in CommandResolver.COMMAND_ALTERNATIVES:
            for alt in CommandResolver.COMMAND_ALTERNATIVES[base_cmd]:
                resolved = CommandResolver.find_command(alt)
                if resolved:
                    return resolved
        
        # Return original if nothing found (let MCPClient handle the error)
        return command
    
    @classmethod
    def normalize_server_config(cls, config: MCPServerConfig) -> MCPServerConfig:
        """
        Normalize server configuration by resolving command paths.
        
        Args:
            config: Original server configuration
            
        Returns:
            Normalized configuration with resolved command paths
        """
        return MCPServerConfig(
            name=config.name,
            command=cls.resolve_command(config.command),
            args=config.args,
            env=config.env
        )


class ConfigParser:
    """Parse and validate MCP server configurations."""
    
    @staticmethod
    def parse_config(config_json: str, auto_resolve: bool = True) -> Dict[str, MCPServerConfig]:
        """
        Parse MCP configuration JSON string.
        
        Args:
            config_json: JSON string containing mcpServers configuration
            auto_resolve: Automatically resolve command paths (default: True)
            
        Returns:
            Dictionary mapping server names to MCPServerConfig objects
            
        Raises:
            ValueError: If JSON is invalid or required fields are missing
        """
        try:
            config_data = json.loads(config_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        
        if "mcpServers" not in config_data:
            raise ValueError("Configuration must contain 'mcpServers' key")
        
        servers = {}
        for name, server_config in config_data["mcpServers"].items():
            if "command" not in server_config:
                raise ValueError(f"Server '{name}' missing required 'command' field")
            
            config_obj = MCPServerConfig(
                name=name,
                command=server_config["command"],
                args=server_config.get("args", []),
                env=server_config.get("env", {})
            )
            
            # Auto-resolve command paths if enabled
            if auto_resolve:
                config_obj = CommandResolver.normalize_server_config(config_obj)
            
            servers[name] = config_obj
        
        return servers
    
    @staticmethod
    def validate_config(servers: Dict[str, MCPServerConfig]) -> List[str]:
        """
        Validate server configurations.
        
        Args:
            servers: Dictionary of server configurations to validate
            
        Returns:
            List of validation warnings (empty list if no issues)
        """
        issues = []
        
        if not servers:
            issues.append("No servers configured")
            return issues
        
        for name, server in servers.items():
            if not server.command:
                issues.append(f"Server '{name}' has empty command")
            if not server.name:
                issues.append(f"Server has empty name")
        
        return issues
