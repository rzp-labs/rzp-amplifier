"""
Hook system for lifecycle events.
Provides deterministic execution with priority ordering.
"""
from typing import Callable, Dict, List, Optional, Any, Awaitable
from dataclasses import dataclass, field
from collections import defaultdict
import asyncio
import logging

from .models import HookResult

logger = logging.getLogger(__name__)


@dataclass
class HookHandler:
    """Registered hook handler with priority."""
    handler: Callable[[str, Dict[str, Any]], Awaitable[HookResult]]
    priority: int = 0
    name: Optional[str] = None
    
    def __lt__(self, other: 'HookHandler') -> bool:
        """Sort by priority (lower number = higher priority)."""
        return self.priority < other.priority


class HookRegistry:
    """
    Manages lifecycle hooks with deterministic execution.
    Hooks execute sequentially by priority with short-circuit on deny.
    """
    
    # Standard lifecycle events
    SESSION_START = 'session:start'
    SESSION_END = 'session:end'
    PROMPT_SUBMIT = 'prompt:submit'
    TOOL_PRE = 'tool:pre'
    TOOL_POST = 'tool:post'
    CONTEXT_PRE_COMPACT = 'context:pre-compact'
    AGENT_SPAWN = 'agent:spawn'
    AGENT_COMPLETE = 'agent:complete'
    
    def __init__(self):
        """Initialize empty hook registry."""
        self._handlers: Dict[str, List[HookHandler]] = defaultdict(list)
        
    def register(
        self,
        event: str,
        handler: Callable[[str, Dict[str, Any]], Awaitable[HookResult]],
        priority: int = 0,
        name: Optional[str] = None
    ) -> Callable[[], None]:
        """
        Register a hook handler for an event.
        
        Args:
            event: Event name to hook into
            handler: Async function that handles the event
            priority: Execution priority (lower = earlier)
            name: Optional handler name for debugging
            
        Returns:
            Unregister function
        """
        hook_handler = HookHandler(
            handler=handler,
            priority=priority,
            name=name or handler.__name__
        )
        
        self._handlers[event].append(hook_handler)
        self._handlers[event].sort()  # Keep sorted by priority
        
        logger.debug(f"Registered hook '{hook_handler.name}' for event '{event}' with priority {priority}")
        
        def unregister():
            """Remove this handler from the registry."""
            if hook_handler in self._handlers[event]:
                self._handlers[event].remove(hook_handler)
                logger.debug(f"Unregistered hook '{hook_handler.name}' from event '{event}'")
                
        return unregister
        
    async def emit(
        self,
        event: str,
        data: Dict[str, Any]
    ) -> HookResult:
        """
        Emit an event to all registered handlers.
        
        Handlers execute sequentially by priority with:
        - Short-circuit on 'deny' action
        - Data modification chaining on 'modify' action
        - Continue on 'continue' action
        
        Args:
            event: Event name
            data: Event data (may be modified by handlers)
            
        Returns:
            Final hook result after all handlers
        """
        handlers = self._handlers.get(event, [])
        
        if not handlers:
            logger.debug(f"No handlers for event '{event}'")
            return HookResult(action='continue')
            
        logger.debug(f"Emitting event '{event}' to {len(handlers)} handlers")
        
        current_data = data.copy()
        
        for hook_handler in handlers:
            try:
                # Call handler with event and current data
                result = await hook_handler.handler(event, current_data)
                
                if not isinstance(result, HookResult):
                    logger.warning(f"Handler '{hook_handler.name}' returned invalid result type")
                    continue
                    
                if result.action == 'deny':
                    logger.info(f"Event '{event}' denied by handler '{hook_handler.name}': {result.reason}")
                    return result
                    
                elif result.action == 'modify':
                    if result.data is not None:
                        current_data = result.data
                        logger.debug(f"Handler '{hook_handler.name}' modified event data")
                        
            except Exception as e:
                logger.error(f"Error in hook handler '{hook_handler.name}' for event '{event}': {e}")
                # Continue with other handlers even if one fails
                
        # Return final result with potentially modified data
        return HookResult(action='continue', data=current_data)
        
    def list_handlers(self, event: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List registered handlers.
        
        Args:
            event: Optional event to filter by
            
        Returns:
            Dict of event names to handler names
        """
        if event:
            handlers = self._handlers.get(event, [])
            return {event: [h.name for h in handlers]}
        else:
            return {
                evt: [h.name for h in handlers]
                for evt, handlers in self._handlers.items()
            }
