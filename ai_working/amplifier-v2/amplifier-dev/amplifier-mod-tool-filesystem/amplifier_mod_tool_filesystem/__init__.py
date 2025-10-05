"""
Filesystem tool module.
Provides basic file operations: read, write, edit.
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from amplifier_core import ModuleCoordinator, ToolResult

logger = logging.getLogger(__name__)


async def mount(coordinator: ModuleCoordinator, config: Optional[Dict[str, Any]] = None):
    """Mount filesystem tools."""
    config = config or {}
    
    tools = [
        ReadTool(config),
        WriteTool(config),
    ]
    
    for tool in tools:
        await coordinator.mount('tools', tool, name=tool.name)
        
    logger.info(f"Mounted {len(tools)} filesystem tools")
    return None


class ReadTool:
    """Read file contents."""
    
    name = "read"
    description = "Read the contents of a file"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.allowed_paths = config.get('allowed_paths', ['.'])
        
    async def execute(self, input: Dict[str, Any]) -> ToolResult:
        """Read a file."""
        path = input.get('path')
        if not path:
            return ToolResult(
                success=False,
                error={'message': 'Path is required'}
            )
            
        try:
            file_path = Path(path)
            
            # Basic safety check
            if not any(file_path.is_relative_to(allowed) for allowed in self.allowed_paths):
                return ToolResult(
                    success=False,
                    error={'message': f'Access denied to {path}'}
                )
            
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    error={'message': f'File not found: {path}'}
                )
                
            content = file_path.read_text()
            return ToolResult(
                success=True,
                output=content
            )
            
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return ToolResult(
                success=False,
                error={'message': str(e)}
            )


class WriteTool:
    """Write file contents."""
    
    name = "write"
    description = "Write content to a file"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.allowed_paths = config.get('allowed_paths', ['.'])
        self.require_approval = config.get('require_approval', True)
        
    async def execute(self, input: Dict[str, Any]) -> ToolResult:
        """Write to a file."""
        path = input.get('path')
        content = input.get('content')
        
        if not path or content is None:
            return ToolResult(
                success=False,
                error={'message': 'Path and content are required'}
            )
            
        try:
            file_path = Path(path)
            
            # Basic safety check
            if not any(file_path.is_relative_to(allowed) for allowed in self.allowed_paths):
                return ToolResult(
                    success=False,
                    error={'message': f'Access denied to {path}'}
                )
            
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            file_path.write_text(content)
            
            return ToolResult(
                success=True,
                output=f"Wrote {len(content)} characters to {path}"
            )
            
        except Exception as e:
            logger.error(f"Error writing file: {e}")
            return ToolResult(
                success=False,
                error={'message': str(e)}
            )
