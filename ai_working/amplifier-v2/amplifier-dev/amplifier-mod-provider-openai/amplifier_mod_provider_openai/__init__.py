"""
OpenAI provider module for Amplifier.
Integrates with OpenAI's GPT models.
"""
import os
import logging
import json
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI

from amplifier_core import (
    ModuleCoordinator,
    ProviderResponse,
    ToolCall
)

logger = logging.getLogger(__name__)


async def mount(coordinator: ModuleCoordinator, config: Optional[Dict[str, Any]] = None):
    """
    Mount the OpenAI provider.
    
    Args:
        coordinator: Module coordinator
        config: Provider configuration including API key
        
    Returns:
        Optional cleanup function
    """
    config = config or {}
    
    # Get API key from config or environment
    api_key = config.get('api_key')
    if not api_key:
        api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        logger.warning("No API key found for OpenAI provider")
        return None
    
    provider = OpenAIProvider(api_key, config)
    await coordinator.mount('providers', provider, name='openai')
    logger.info("Mounted OpenAIProvider")
    
    # Return cleanup function
    async def cleanup():
        if hasattr(provider.client, 'close'):
            await provider.client.close()
    
    return cleanup


class OpenAIProvider:
    """OpenAI API integration."""
    
    name = "openai"
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            config: Additional configuration
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.config = config or {}
        self.default_model = config.get('default_model', 'gpt-4-turbo-preview')
        self.max_tokens = config.get('max_tokens', 4096)
        self.temperature = config.get('temperature', 0.7)
        
    async def complete(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> ProviderResponse:
        """
        Generate completion from messages.
        
        Args:
            messages: Conversation history
            **kwargs: Additional parameters
            
        Returns:
            Provider response
        """
        # Convert messages to OpenAI format
        openai_messages = self._convert_messages(messages)
        
        # Prepare request parameters
        params = {
            'model': kwargs.get('model', self.default_model),
            'messages': openai_messages,
            'max_tokens': kwargs.get('max_tokens', self.max_tokens),
            'temperature': kwargs.get('temperature', self.temperature)
        }
        
        # Add tools if provided
        if 'tools' in kwargs:
            params['tools'] = self._convert_tools(kwargs['tools'])
            params['tool_choice'] = 'auto'
        
        # Add response format if needed
        if kwargs.get('json_mode'):
            params['response_format'] = {'type': 'json_object'}
        
        try:
            response = await self.client.chat.completions.create(**params)
            
            # Get the first choice
            choice = response.choices[0]
            message = choice.message
            
            # Extract content and tool calls
            content = message.content or ""
            tool_calls = []
            
            if message.tool_calls:
                for tc in message.tool_calls:
                    tool_calls.append(ToolCall(
                        tool=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                        id=tc.id
                    ))
            
            return ProviderResponse(
                content=content,
                raw=response,
                usage={
                    'input': response.usage.prompt_tokens,
                    'output': response.usage.completion_tokens,
                    'total': response.usage.total_tokens
                } if response.usage else {},
                tool_calls=tool_calls if tool_calls else None
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def parse_tool_calls(self, response: ProviderResponse) -> List[ToolCall]:
        """
        Parse tool calls from provider response.
        
        Args:
            response: Provider response
            
        Returns:
            List of tool calls
        """
        return response.tool_calls or []
    
    def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert messages to OpenAI format."""
        openai_messages = []
        
        for msg in messages:
            role = msg.get('role')
            content = msg.get('content', '')
            
            # Map roles
            if role == 'tool':
                # Tool results in OpenAI format
                openai_messages.append({
                    'role': 'tool',
                    'tool_call_id': msg.get('tool_call_id', 'unknown'),
                    'content': content
                })
            else:
                # Regular messages (system, user, assistant)
                openai_messages.append({
                    'role': role,
                    'content': content
                })
        
        return openai_messages
    
    def _convert_tools(self, tools: List[Any]) -> List[Dict[str, Any]]:
        """Convert tools to OpenAI format."""
        openai_tools = []
        
        for tool in tools:
            openai_tools.append({
                'type': 'function',
                'function': {
                    'name': tool.name,
                    'description': tool.description,
                    'parameters': {
                        'type': 'object',
                        'properties': {},  # Would need tool schema here
                        'required': []
                    }
                }
            })
        
        return openai_tools
