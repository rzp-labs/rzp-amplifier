"""
Zen Architect agent module for Amplifier.
Designs with ruthless simplicity and clarity.
"""
import logging
from typing import Dict, Any, Optional

from amplifier_core import (
    ModuleCoordinator,
    AgentResult,
    AgentContext
)

logger = logging.getLogger(__name__)


async def mount(coordinator: ModuleCoordinator, config: Optional[Dict[str, Any]] = None):
    """
    Mount the zen architect agent.
    
    Args:
        coordinator: Module coordinator
        config: Agent configuration
        
    Returns:
        Optional cleanup function
    """
    config = config or {}
    agent = ZenArchitectAgent(config)
    await coordinator.mount('agents', agent, name=agent.name)
    logger.info("Mounted ZenArchitectAgent")
    return None


class ZenArchitectAgent:
    """
    Zen architect agent - designs with ruthless simplicity.
    Embodies principles of minimalism and clarity.
    """
    
    name = "zen-architect"
    description = "System design with ruthless simplicity and clarity"
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the zen architect.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.preferred_model = config.get('preferred_model', 'opus-4')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 4096)
        
        # Zen principles to apply
        self.principles = [
            "Simplicity is the ultimate sophistication",
            "Remove everything unnecessary",
            "Make the common case fast and simple",
            "Complexity is debt that compounds",
            "Every line should have a clear purpose",
            "Prefer composition over inheritance",
            "Make it work, make it right, make it simple"
        ]
    
    async def execute(
        self,
        task: Dict[str, Any],
        context: AgentContext
    ) -> AgentResult:
        """
        Execute architectural design task.
        
        Args:
            task: Task specification with requirements
            context: Agent execution context
            
        Returns:
            Agent result with design
        """
        try:
            # Extract task details
            requirements = task.get('requirements', '')
            constraints = task.get('constraints', [])
            existing_system = task.get('existing_system', '')
            
            # Build the design prompt
            prompt = self._build_prompt(requirements, constraints, existing_system)
            
            # Get the appropriate provider
            providers = context.providers
            if not providers:
                return AgentResult(
                    success=False,
                    error={'message': 'No providers available'}
                )
            
            # Select provider (prefer configured model)
            provider = self._select_provider(providers)
            
            # Generate the design
            messages = [
                {
                    'role': 'system',
                    'content': self._get_system_prompt()
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
            
            response = await provider.complete(
                messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Return the design
            return AgentResult(
                success=True,
                text=response.content,
                data={
                    'task': 'architecture_design',
                    'principles_applied': self.principles[:3]
                }
            )
            
        except Exception as e:
            logger.error(f"Zen architect failed: {e}")
            return AgentResult(
                success=False,
                error={'message': str(e)}
            )
    
    def _get_system_prompt(self) -> str:
        """Get the zen architect system prompt."""
        principles_text = '\n'.join(f"- {p}" for p in self.principles)
        
        return f"""You are a zen architect who values simplicity, elegance, and clarity above all else.

Your designs are minimalist yet powerful, removing unnecessary complexity while maintaining full functionality.

You think deeply about trade-offs, always preferring simpler solutions that solve 80% of problems perfectly
over complex solutions that try to solve 100% imperfectly.

Core principles you follow:
{principles_text}

When designing systems:
1. Start with the simplest possible solution
2. Add complexity only when absolutely necessary
3. Question every abstraction and layer
4. Prefer explicit over implicit
5. Make the code obvious, not clever
6. Design for deletion - make components easy to remove
7. Keep interfaces minimal and stable

Your responses should be clear, concise, and focused on practical simplicity."""
    
    def _build_prompt(
        self,
        requirements: str,
        constraints: list,
        existing_system: str
    ) -> str:
        """Build the design prompt."""
        prompt_parts = []
        
        prompt_parts.append(f"Design a system architecture for the following requirements:")
        prompt_parts.append(f"\nRequirements:\n{requirements}")
        
        if constraints:
            constraints_text = '\n'.join(f"- {c}" for c in constraints)
            prompt_parts.append(f"\nConstraints:\n{constraints_text}")
        
        if existing_system:
            prompt_parts.append(f"\nExisting System Context:\n{existing_system}")
        
        prompt_parts.append("\nProvide a clear, simple design that:")
        prompt_parts.append("1. Solves the core problem with minimal complexity")
        prompt_parts.append("2. Can be understood quickly by new developers")
        prompt_parts.append("3. Is easy to test and maintain")
        prompt_parts.append("4. Scales through simplicity, not premature optimization")
        prompt_parts.append("\nFocus on the essential architecture, not implementation details.")
        
        return '\n'.join(prompt_parts)
    
    def _select_provider(self, providers: Dict[str, Any]) -> Any:
        """Select the best provider for architectural design."""
        # Look for preferred provider
        for name, provider in providers.items():
            if 'anthropic' in name.lower() and 'opus' in str(provider):
                return provider
        
        # Fallback to first available
        return next(iter(providers.values()))
