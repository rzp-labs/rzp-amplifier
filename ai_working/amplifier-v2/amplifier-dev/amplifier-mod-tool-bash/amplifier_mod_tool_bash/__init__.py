"""
Bash command execution tool for Amplifier.
Includes safety features and approval mechanisms.
"""
import asyncio
import subprocess
import shlex
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from amplifier_core import ModuleCoordinator, ToolResult

logger = logging.getLogger(__name__)


async def mount(coordinator: ModuleCoordinator, config: Optional[Dict[str, Any]] = None):
    """
    Mount the bash tool.
    
    Args:
        coordinator: Module coordinator
        config: Tool configuration
        
    Returns:
        Optional cleanup function
    """
    config = config or {}
    tool = BashTool(config)
    await coordinator.mount('tools', tool, name=tool.name)
    logger.info("Mounted BashTool")
    return None


class BashTool:
    """Execute bash commands with safety features."""
    
    name = "bash"
    description = "Execute bash commands in the shell"
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize bash tool.
        
        Args:
            config: Tool configuration
        """
        self.config = config
        self.require_approval = config.get('require_approval', True)
        self.allowed_commands = config.get('allowed_commands', [])
        self.denied_commands = config.get('denied_commands', [
            'rm -rf /',
            'sudo rm',
            'dd if=/dev/zero',
            'fork bomb',
            ':(){ :|:& };:'
        ])
        self.timeout = config.get('timeout', 30)
        self.working_dir = config.get('working_dir', '.')
        
    async def execute(self, input: Dict[str, Any]) -> ToolResult:
        """
        Execute a bash command.
        
        Args:
            input: Dictionary with 'command' key
            
        Returns:
            Tool result with command output
        """
        command = input.get('command')
        if not command:
            return ToolResult(
                success=False,
                error={'message': 'Command is required'}
            )
        
        # Safety checks
        if not self._is_safe_command(command):
            return ToolResult(
                success=False,
                error={'message': f'Command denied for safety: {command}'}
            )
        
        # Manual approval if required
        if self.require_approval and not self._is_pre_approved(command):
            approved = await self._get_user_approval(command)
            if not approved:
                return ToolResult(
                    success=False,
                    error={'message': 'Command rejected by user'}
                )
        
        try:
            # Execute command
            result = await self._run_command(command)
            
            return ToolResult(
                success=result['returncode'] == 0,
                output={
                    'stdout': result['stdout'],
                    'stderr': result['stderr'],
                    'returncode': result['returncode']
                }
            )
            
        except asyncio.TimeoutError:
            return ToolResult(
                success=False,
                error={'message': f'Command timed out after {self.timeout} seconds'}
            )
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return ToolResult(
                success=False,
                error={'message': str(e)}
            )
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute."""
        command_lower = command.lower()
        
        # Check against denied commands
        for denied in self.denied_commands:
            if denied.lower() in command_lower:
                logger.warning(f"Denied dangerous command: {command}")
                return False
        
        # Check for suspicious patterns
        dangerous_patterns = [
            'rm -rf',
            'rm -fr',
            'dd if=',
            'mkfs',
            'format',
            '> /dev/',
            'sudo',
            'su -',
            'passwd',
            'chmod 777 /',
            'chown -R'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                logger.warning(f"Suspicious pattern detected: {pattern}")
                return False
        
        return True
    
    def _is_pre_approved(self, command: str) -> bool:
        """Check if command is pre-approved."""
        if not self.allowed_commands:
            return False
        
        # Check exact matches
        if command in self.allowed_commands:
            return True
        
        # Check pattern matches
        for allowed in self.allowed_commands:
            if allowed.endswith('*'):
                # Prefix match
                if command.startswith(allowed[:-1]):
                    return True
            elif '*' in allowed:
                # Pattern match (simple)
                pattern = allowed.replace('*', '.*')
                import re
                if re.match(pattern, command):
                    return True
        
        return False
    
    async def _get_user_approval(self, command: str) -> bool:
        """Get user approval for command execution."""
        # In a real implementation, this would integrate with the UI
        # For now, log and auto-approve in non-interactive mode
        logger.info(f"Command requires approval: {command}")
        
        # Check if we're in auto-approve mode
        if self.config.get('auto_approve'):
            return True
        
        # In production, this would prompt the user
        # For now, return True if in development mode
        return self.config.get('development_mode', False)
    
    async def _run_command(self, command: str) -> Dict[str, Any]:
        """Run command asynchronously."""
        # Parse command
        try:
            args = shlex.split(command)
        except ValueError as e:
            raise ValueError(f"Invalid command syntax: {e}")
        
        # Run command
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.working_dir
        )
        
        # Wait for completion with timeout
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            
            return {
                'stdout': stdout.decode('utf-8', errors='replace'),
                'stderr': stderr.decode('utf-8', errors='replace'),
                'returncode': process.returncode
            }
            
        except asyncio.TimeoutError:
            # Kill the process
            process.kill()
            await process.communicate()  # Clean up
            raise
