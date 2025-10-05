"""
Amplifier Core - Ultra-thin coordination layer for modular AI agents.
"""

__version__ = "1.0.0"

from .session import AmplifierSession
from .coordinator import ModuleCoordinator
from .loader import ModuleLoader
from .hooks import HookRegistry
from .models import (
    ToolCall,
    ToolResult,
    HookResult,
    AgentResult,
    ProviderResponse,
    ModuleInfo,
    SessionStatus
)
from .interfaces import (
    Orchestrator,
    Provider,
    Tool,
    Agent,
    ContextManager,
    HookHandler,
    AgentContext
)

__all__ = [
    'AmplifierSession',
    'ModuleCoordinator',
    'ModuleLoader',
    'HookRegistry',
    'ToolCall',
    'ToolResult',
    'HookResult',
    'AgentResult',
    'ProviderResponse',
    'ModuleInfo',
    'SessionStatus',
    'Orchestrator',
    'Provider',
    'Tool',
    'Agent',
    'ContextManager',
    'HookHandler',
    'AgentContext'
]
