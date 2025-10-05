#!/bin/bash
# Create a new Amplifier module from template

set -e

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <module-name> <module-type>"
    echo "Types: orchestrator, provider, tool, agent, context, hook"
    exit 1
fi

MODULE_NAME="$1"
MODULE_TYPE="$2"
MODULE_DIR="amplifier-mod-${MODULE_NAME}"

# Validate module type
case "$MODULE_TYPE" in
    orchestrator|provider|tool|agent|context|hook)
        ;;
    *)
        echo "Error: Invalid module type '$MODULE_TYPE'"
        echo "Valid types: orchestrator, provider, tool, agent, context, hook"
        exit 1
        ;;
esac

# Check if module already exists
if [ -d "$MODULE_DIR" ]; then
    echo "Error: Module directory '$MODULE_DIR' already exists"
    exit 1
fi

echo "Creating module: $MODULE_NAME (type: $MODULE_TYPE)"

# Create module directory structure
mkdir -p "$MODULE_DIR"
mkdir -p "$MODULE_DIR/amplifier_mod_${MODULE_NAME//-/_}"
mkdir -p "$MODULE_DIR/tests"

# Create pyproject.toml
cat > "$MODULE_DIR/pyproject.toml" << EOF
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "amplifier-mod-${MODULE_NAME}"
version = "0.1.0"
description = "${MODULE_TYPE^} module for Amplifier"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
dependencies = [
    "amplifier-core>=1.0.0",
]

[project.entry-points."amplifier.modules"]
${MODULE_NAME} = "amplifier_mod_${MODULE_NAME//-/_}:mount"

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
]
EOF

# Create module implementation based on type
MODULE_PY_NAME="${MODULE_NAME//-/_}"

case "$MODULE_TYPE" in
    orchestrator)
        cat > "$MODULE_DIR/amplifier_mod_${MODULE_PY_NAME}/__init__.py" << 'EOF'
"""
Custom orchestrator module for Amplifier.
"""
import logging
from typing import Dict, Any, Optional

from amplifier_core import ModuleCoordinator, HookRegistry

logger = logging.getLogger(__name__)


async def mount(coordinator: ModuleCoordinator, config: Optional[Dict[str, Any]] = None):
    """Mount the orchestrator module."""
    config = config or {}
    orchestrator = CustomOrchestrator(config)
    await coordinator.mount('orchestrator', orchestrator)
    logger.info(f"Mounted CustomOrchestrator")
    return None


class CustomOrchestrator:
    """Custom agent loop implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    async def execute(
        self,
        prompt: str,
        context,
        providers: Dict[str, Any],
        tools: Dict[str, Any],
        hooks: HookRegistry
    ) -> str:
        """Execute the agent loop."""
        # TODO: Implement custom orchestration logic
        await hooks.emit('session:start', {'prompt': prompt})
        
        # Your custom loop implementation here
        result = "Custom orchestrator response"
        
        await hooks.emit('session:end', {'response': result})
        return result
EOF
        ;;
        
    provider)
        cat > "$MODULE_DIR/amplifier_mod_${MODULE_PY_NAME}/__init__.py" << 'EOF'
"""
Custom provider module for Amplifier.
"""
import logging
from typing import Dict, Any, List, Optional

from amplifier_core import ModuleCoordinator, ProviderResponse, ToolCall

logger = logging.getLogger(__name__)


async def mount(coordinator: ModuleCoordinator, config: Optional[Dict[str, Any]] = None):
    """Mount the provider module."""
    config = config or {}
    provider = CustomProvider(config)
    await coordinator.mount('providers', provider, name='custom')
    logger.info(f"Mounted CustomProvider")
    return None


class CustomProvider:
    """Custom LLM provider."""
    
    name = "custom"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    async def complete(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> ProviderResponse:
        """Generate completion."""
        # TODO: Implement provider logic
        return ProviderResponse(
            content="Provider response",
            raw=None,
            usage={'input': 0, 'output': 0}
        )
    
    def parse_tool_calls(self, response: ProviderResponse) -> List[ToolCall]:
        """Parse tool calls from response."""
        return response.tool_calls or []
EOF
        ;;
        
    tool)
        cat > "$MODULE_DIR/amplifier_mod_${MODULE_PY_NAME}/__init__.py" << 'EOF'
"""
Custom tool module for Amplifier.
"""
import logging
from typing import Dict, Any, Optional

from amplifier_core import ModuleCoordinator, ToolResult

logger = logging.getLogger(__name__)


async def mount(coordinator: ModuleCoordinator, config: Optional[Dict[str, Any]] = None):
    """Mount the tool module."""
    config = config or {}
    tool = CustomTool(config)
    await coordinator.mount('tools', tool, name=tool.name)
    logger.info(f"Mounted CustomTool")
    return None


class CustomTool:
    """Custom tool implementation."""
    
    name = "custom_tool"
    description = "Description of what this tool does"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    async def execute(self, input: Dict[str, Any]) -> ToolResult:
        """Execute the tool."""
        # TODO: Implement tool logic
        try:
            result = "Tool execution result"
            return ToolResult(success=True, output=result)
        except Exception as e:
            return ToolResult(success=False, error={'message': str(e)})
EOF
        ;;
        
    agent)
        cat > "$MODULE_DIR/amplifier_mod_${MODULE_PY_NAME}/__init__.py" << 'EOF'
"""
Custom agent module for Amplifier.
"""
import logging
from typing import Dict, Any, Optional

from amplifier_core import ModuleCoordinator, AgentResult, AgentContext

logger = logging.getLogger(__name__)


async def mount(coordinator: ModuleCoordinator, config: Optional[Dict[str, Any]] = None):
    """Mount the agent module."""
    config = config or {}
    agent = CustomAgent(config)
    await coordinator.mount('agents', agent, name=agent.name)
    logger.info(f"Mounted CustomAgent")
    return None


class CustomAgent:
    """Custom specialized agent."""
    
    name = "custom_agent"
    description = "Description of agent capabilities"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    async def execute(
        self,
        task: Dict[str, Any],
        context: AgentContext
    ) -> AgentResult:
        """Execute agent task."""
        # TODO: Implement agent logic
        try:
            result = "Agent execution result"
            return AgentResult(success=True, text=result)
        except Exception as e:
            return AgentResult(success=False, error={'message': str(e)})
EOF
        ;;
        
    context)
        cat > "$MODULE_DIR/amplifier_mod_${MODULE_PY_NAME}/__init__.py" << 'EOF'
"""
Custom context manager module for Amplifier.
"""
import logging
from typing import Dict, Any, List, Optional

from amplifier_core import ModuleCoordinator

logger = logging.getLogger(__name__)


async def mount(coordinator: ModuleCoordinator, config: Optional[Dict[str, Any]] = None):
    """Mount the context manager module."""
    config = config or {}
    context = CustomContextManager(config)
    await coordinator.mount('context', context)
    logger.info(f"Mounted CustomContextManager")
    return None


class CustomContextManager:
    """Custom context management."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.messages = []
        
    async def add_message(self, message: Dict[str, Any]) -> None:
        """Add a message to context."""
        self.messages.append(message)
        
    async def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages."""
        return self.messages.copy()
        
    async def should_compact(self) -> bool:
        """Check if compaction needed."""
        return len(self.messages) > 100
        
    async def compact(self) -> None:
        """Compact the context."""
        # TODO: Implement compaction logic
        self.messages = self.messages[-50:]
        
    async def clear(self) -> None:
        """Clear all messages."""
        self.messages = []
EOF
        ;;
        
    hook)
        cat > "$MODULE_DIR/amplifier_mod_${MODULE_PY_NAME}/__init__.py" << 'EOF'
"""
Custom hook module for Amplifier.
"""
import logging
from typing import Dict, Any, Optional

from amplifier_core import ModuleCoordinator, HookRegistry, HookResult

logger = logging.getLogger(__name__)


async def mount(coordinator: ModuleCoordinator, config: Optional[Dict[str, Any]] = None):
    """Mount the hook module."""
    config = config or {}
    hook = CustomHook(config)
    
    hooks = coordinator.get('hooks')
    if not hooks:
        logger.warning("No hook registry found")
        return None
    
    # Register for events
    unregister = hooks.register(
        HookRegistry.SESSION_START,
        hook.on_session_start,
        priority=0,
        name="custom_hook"
    )
    
    logger.info(f"Mounted CustomHook")
    return unregister


class CustomHook:
    """Custom hook implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    async def on_session_start(self, event: str, data: Dict[str, Any]) -> HookResult:
        """Handle session start event."""
        # TODO: Implement hook logic
        logger.info(f"Session started with prompt: {data.get('prompt', '')}")
        return HookResult(action='continue')
EOF
        ;;
esac

# Create README.md
cat > "$MODULE_DIR/README.md" << EOF
# amplifier-mod-${MODULE_NAME}

${MODULE_TYPE^} module for Amplifier.

## Installation

\`\`\`bash
pip install -e .
\`\`\`

## Usage

Add to your Amplifier configuration:

\`\`\`toml
[[${MODULE_TYPE}s]]
module = "${MODULE_NAME}"
\`\`\`

## Development

Run tests:
\`\`\`bash
pytest
\`\`\`
EOF

# Create basic test file
cat > "$MODULE_DIR/tests/test_${MODULE_PY_NAME}.py" << EOF
"""
Tests for ${MODULE_NAME} module.
"""
import pytest
from amplifier_core import ModuleCoordinator
from amplifier_mod_${MODULE_PY_NAME} import mount


@pytest.mark.asyncio
async def test_module_mount():
    """Test module can be mounted."""
    coordinator = ModuleCoordinator()
    cleanup = await mount(coordinator, {})
    
    # Verify module was mounted
    if '${MODULE_TYPE}' == 'orchestrator' or '${MODULE_TYPE}' == 'context':
        assert coordinator.get('${MODULE_TYPE}') is not None
    else:
        # For multi-mount types, check if any mounted
        mounted = coordinator.get('${MODULE_TYPE}s')
        assert mounted is not None and len(mounted) > 0
    
    # Cleanup if provided
    if cleanup:
        if asyncio.iscoroutinefunction(cleanup):
            await cleanup()
        else:
            cleanup()
EOF

# Create .gitignore
cat > "$MODULE_DIR/.gitignore" << EOF
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/
.tox/
.venv
env/
venv/
EOF

echo "✅ Module created successfully at: $MODULE_DIR"
echo ""
echo "Next steps:"
echo "1. cd $MODULE_DIR"
echo "2. pip install -e ."
echo "3. Implement your module logic in amplifier_mod_${MODULE_PY_NAME}/__init__.py"
echo "4. Write tests in tests/"
echo "5. Update README.md with documentation"
