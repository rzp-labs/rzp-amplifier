"""
Core data models for Amplifier.
Uses Pydantic for validation and serialization.
"""
from typing import Any, Dict, List, Optional, Literal, Union
from pydantic import BaseModel, Field
from datetime import datetime


class ToolCall(BaseModel):
    """Represents a tool invocation request."""
    tool: str = Field(..., description="Tool name to invoke")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    id: Optional[str] = Field(default=None, description="Unique tool call ID")


class ToolResult(BaseModel):
    """Result from tool execution."""
    success: bool = Field(default=True, description="Whether execution succeeded")
    output: Optional[Any] = Field(default=None, description="Tool output data")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error details if failed")
    
    def __str__(self) -> str:
        if self.success:
            return str(self.output) if self.output else "Success"
        else:
            return f"Error: {self.error.get('message', 'Unknown error')}" if self.error else "Failed"


class HookResult(BaseModel):
    """Result from hook execution."""
    action: Literal['continue', 'deny', 'modify'] = Field(
        default='continue',
        description="Action to take: continue normally, deny operation, or modify data"
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Modified data if action is 'modify'"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Reason for deny or modification"
    )


class AgentResult(BaseModel):
    """Result from agent execution."""
    success: bool = Field(default=True, description="Whether agent succeeded")
    text: Optional[str] = Field(default=None, description="Agent response text")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Structured output data")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error details if failed")


class ProviderResponse(BaseModel):
    """Response from LLM provider."""
    content: str = Field(..., description="Response text content")
    raw: Optional[Any] = Field(default=None, description="Raw provider response object")
    usage: Optional[Dict[str, int]] = Field(
        default=None,
        description="Token usage statistics"
    )
    tool_calls: Optional[List[ToolCall]] = Field(
        default=None,
        description="Parsed tool calls from response"
    )


class ModuleInfo(BaseModel):
    """Module metadata."""
    id: str = Field(..., description="Module identifier")
    name: str = Field(..., description="Module display name")
    version: str = Field(..., description="Module version")
    type: Literal['orchestrator', 'provider', 'tool', 'agent', 'context', 'hook'] = Field(
        ...,
        description="Module type"
    )
    mount_point: str = Field(..., description="Where module should be mounted")
    description: str = Field(..., description="Module description")
    config_schema: Optional[Dict[str, Any]] = Field(
        default=None,
        description="JSON schema for module configuration"
    )


class SessionStatus(BaseModel):
    """Session status and metadata."""
    session_id: str = Field(..., description="Unique session ID")
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    status: Literal['running', 'completed', 'failed', 'cancelled'] = 'running'
    
    # Counters
    total_messages: int = 0
    tool_invocations: int = 0
    tool_successes: int = 0
    tool_failures: int = 0
    
    # Token usage
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    
    # Cost tracking (if available)
    estimated_cost: Optional[float] = None
    
    # Last activity
    last_activity: Optional[datetime] = None
    last_error: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return self.model_dump(mode='json', exclude_none=True)
