"""
Amplifier session management.
The main entry point for using the Amplifier system.
"""
import os
import uuid
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
import tomli

from .coordinator import ModuleCoordinator
from .loader import ModuleLoader
from .models import SessionStatus

logger = logging.getLogger(__name__)


class AmplifierSession:
    """
    A single Amplifier session tying everything together.
    This is the main entry point for users.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize an Amplifier session.
        
        Args:
            config: Optional configuration dict, otherwise loads from files
        """
        self.session_id = str(uuid.uuid4())
        self.coordinator = ModuleCoordinator()
        self.loader = ModuleLoader()
        self.config = config or self._load_config()
        self.status = SessionStatus(session_id=self.session_id)
        self._initialized = False
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration with precedence:
        1. Project config (.amplifier/config.toml)
        2. User config (~/.amplifier/config.toml)
        3. Default config
        """
        config = self._get_default_config()
        
        # Load user config
        user_config_path = Path.home() / '.amplifier' / 'config.toml'
        if user_config_path.exists():
            try:
                with open(user_config_path, 'rb') as f:
                    user_config = tomli.load(f)
                    config = self._merge_configs(config, user_config)
                    logger.info(f"Loaded user config from {user_config_path}")
            except Exception as e:
                logger.warning(f"Failed to load user config: {e}")
                
        # Load project config
        project_config_path = Path('.amplifier') / 'config.toml'
        if project_config_path.exists():
            try:
                with open(project_config_path, 'rb') as f:
                    project_config = tomli.load(f)
                    config = self._merge_configs(config, project_config)
                    logger.info(f"Loaded project config from {project_config_path}")
            except Exception as e:
                logger.warning(f"Failed to load project config: {e}")
                
        return config
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'session': {
                'orchestrator': 'loop-basic',
                'context': 'context-simple',
            },
            'context': {
                'config': {
                    'max_tokens': 200_000,
                    'compact_threshold': 0.92
                }
            },
            'providers': [],
            'tools': [],
            'agents': [],
            'hooks': []
        }
        
    def _merge_configs(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two config dicts."""
        result = base.copy()
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
                
        return result
        
    async def initialize(self) -> None:
        """
        Load and mount all configured modules.
        The orchestrator module determines behavior.
        """
        if self._initialized:
            return
            
        try:
            # Load orchestrator (required)
            orchestrator_id = self.config.get('session', {}).get('orchestrator', 'loop-basic')
            logger.info(f"Loading orchestrator: {orchestrator_id}")
            
            try:
                orchestrator_mount = await self.loader.load(orchestrator_id)
                cleanup = await orchestrator_mount(self.coordinator)
                if cleanup:
                    self.coordinator.register_cleanup(cleanup)
            except Exception as e:
                logger.error(f"Failed to load orchestrator '{orchestrator_id}': {e}")
                raise RuntimeError(f"Cannot initialize without orchestrator: {e}")
                
            # Load context manager (required)
            context_id = self.config.get('session', {}).get('context', 'context-simple')
            logger.info(f"Loading context manager: {context_id}")
            
            try:
                context_config = self.config.get('context', {}).get('config', {})
                context_mount = await self.loader.load(context_id, context_config)
                cleanup = await context_mount(self.coordinator)
                if cleanup:
                    self.coordinator.register_cleanup(cleanup)
            except Exception as e:
                logger.error(f"Failed to load context manager '{context_id}': {e}")
                raise RuntimeError(f"Cannot initialize without context manager: {e}")
                
            # Load providers
            for provider_config in self.config.get('providers', []):
                module_id = provider_config.get('module')
                if not module_id:
                    continue
                    
                try:
                    logger.info(f"Loading provider: {module_id}")
                    provider_mount = await self.loader.load(
                        module_id,
                        provider_config.get('config', {})
                    )
                    cleanup = await provider_mount(self.coordinator)
                    if cleanup:
                        self.coordinator.register_cleanup(cleanup)
                except Exception as e:
                    logger.warning(f"Failed to load provider '{module_id}': {e}")
                    
            # Load tools
            for tool_config in self.config.get('tools', []):
                module_id = tool_config.get('module')
                if not module_id:
                    continue
                    
                try:
                    logger.info(f"Loading tool: {module_id}")
                    tool_mount = await self.loader.load(
                        module_id,
                        tool_config.get('config', {})
                    )
                    cleanup = await tool_mount(self.coordinator)
                    if cleanup:
                        self.coordinator.register_cleanup(cleanup)
                except Exception as e:
                    logger.warning(f"Failed to load tool '{module_id}': {e}")
                    
            # Load agents
            for agent_config in self.config.get('agents', []):
                module_id = agent_config.get('module')
                if not module_id:
                    continue
                    
                try:
                    logger.info(f"Loading agent: {module_id}")
                    agent_mount = await self.loader.load(
                        module_id,
                        agent_config.get('config', {})
                    )
                    cleanup = await agent_mount(self.coordinator)
                    if cleanup:
                        self.coordinator.register_cleanup(cleanup)
                except Exception as e:
                    logger.warning(f"Failed to load agent '{module_id}': {e}")
                    
            # Load hooks
            for hook_config in self.config.get('hooks', []):
                module_id = hook_config.get('module')
                if not module_id:
                    continue
                    
                try:
                    logger.info(f"Loading hook: {module_id}")
                    hook_mount = await self.loader.load(
                        module_id,
                        hook_config.get('config', {})
                    )
                    cleanup = await hook_mount(self.coordinator)
                    if cleanup:
                        self.coordinator.register_cleanup(cleanup)
                except Exception as e:
                    logger.warning(f"Failed to load hook '{module_id}': {e}")
                    
            self._initialized = True
            logger.info(f"Session {self.session_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Session initialization failed: {e}")
            raise
            
    async def execute(self, prompt: str) -> str:
        """
        Execute a prompt using the mounted orchestrator.
        
        Args:
            prompt: User input prompt
            
        Returns:
            Final response string
        """
        if not self._initialized:
            await self.initialize()
            
        orchestrator = self.coordinator.get('orchestrator')
        if not orchestrator:
            raise RuntimeError("No orchestrator module mounted")
            
        context = self.coordinator.get('context')
        if not context:
            raise RuntimeError("No context manager mounted")
            
        providers = self.coordinator.get('providers')
        if not providers:
            raise RuntimeError("No providers mounted")
            
        tools = self.coordinator.get('tools') or {}
        hooks = self.coordinator.get('hooks')
        
        try:
            self.status.status = 'running'
            
            result = await orchestrator.execute(
                prompt=prompt,
                context=context,
                providers=providers,
                tools=tools,
                hooks=hooks
            )
            
            self.status.status = 'completed'
            return result
            
        except Exception as e:
            self.status.status = 'failed'
            self.status.last_error = {'message': str(e)}
            logger.error(f"Execution failed: {e}")
            raise
            
    async def cleanup(self) -> None:
        """Clean up session resources."""
        await self.coordinator.cleanup()
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
