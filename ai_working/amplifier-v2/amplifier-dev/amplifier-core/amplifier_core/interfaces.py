"""
Standard interfaces for Amplifier modules.
Uses Protocol classes for structural subtyping (no inheritance required).
"""
from typing import Protocol, runtime_checkable, Any, Optional, List, Dict, AsyncIterator
from abc import abstractmethod

from .models import ToolCall, ToolResult, HookResult, AgentResult, ProviderResponse


@runtime_checkable
class Orchestrator(Protocol):
    """Interface for agent loop orchestrator modules."""
    
    async def execute(
        self,
        prompt: str,
        context: 'ContextManager',
        providers: Dict[str, 'Provider'],
        tools: Dict[str, 'Tool'],
        hooks: 'HookRegistry'
    ) -> str:
        """
        Execute the agent loop with given prompt.
        
        Args:
            prompt: User input prompt
            context: Context manager for conversation state
            providers: Available LLM providers
            tools: Available tools
            hooks: Hook registry for lifecycle events
            
        Returns:
            Final response string
        """
        ...


@runtime_checkable
class Provider(Protocol):
    """Interface for LLM provider modules."""
    
    @property
    def name(self) -> str:
        """Provider name."""
        ...
    
    async def complete(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> ProviderResponse:
        """
        Generate completion from messages.
        
        Args:
            messages: Conversation history
            **kwargs: Provider-specific options
            
        Returns:
            Provider response with content and metadata
        """
        ...
    
    def parse_tool_calls(self, response: ProviderResponse) -> List[ToolCall]:
        """
        Parse tool calls from provider response.
        
        Args:
            response: Provider response
            
        Returns:
            List of tool calls to execute
        """
        ...


@runtime_checkable
class Tool(Protocol):
    """Interface for tool modules."""
    
    @property
    def name(self) -> str:
        """Tool name for invocation."""
        ...
    
    @property
    def description(self) -> str:
        """Human-readable tool description."""
        ...
    
    async def execute(self, input: Dict[str, Any]) -> ToolResult:
        """
        Execute tool with given input.
        
        Args:
            input: Tool-specific input parameters
            
        Returns:
            Tool execution result
        """
        ...


@runtime_checkable
class Agent(Protocol):
    """Interface for specialized agent modules."""
    
    @property
    def name(self) -> str:
        """Agent name."""
        ...
    
    @property
    def description(self) -> str:
        """Agent description and capabilities."""
        ...
    
    async def execute(
        self,
        task: Dict[str, Any],
        context: 'AgentContext'
    ) -> AgentResult:
        """
        Execute agent task.
        
        Args:
            task: Task specification
            context: Agent execution context
            
        Returns:
            Agent execution result
        """
        ...


@runtime_checkable
class ContextManager(Protocol):
    """Interface for context management modules."""
    
    async def add_message(self, message: Dict[str, Any]) -> None:
        """Add a message to the context."""
        ...
    
    async def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in the context."""
        ...
    
    async def should_compact(self) -> bool:
        """Check if context should be compacted."""
        ...
    
    async def compact(self) -> None:
        """Compact the context to reduce size."""
        ...
    
    async def clear(self) -> None:
        """Clear all messages."""
        ...


@runtime_checkable
class HookHandler(Protocol):
    """Interface for hook handlers."""
    
    async def __call__(self, event: str, data: Dict[str, Any]) -> HookResult:
        """
        Handle a lifecycle event.
        
        Args:
            event: Event name
            data: Event data
            
        Returns:
            Hook result indicating action to take
        """
        ...


class AgentContext:
    """Context provided to agent modules."""
    
    def __init__(
        self,
        tools: Dict[str, Tool],
        providers: Dict[str, Provider],
        hooks: 'HookRegistry'
    ):
        self.tools = tools
        self.providers = providers
        self.hooks = hooks
