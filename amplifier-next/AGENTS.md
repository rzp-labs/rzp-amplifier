# Amplifier Agent Guidelines

This file contains guidelines for AI agents working with the Amplifier platform.

## Available Specialized Agents

### Architect Agent
- **Purpose**: System design and architecture planning
- **Temperature**: 0.7 (balanced creativity and precision)
- **Focus**: Ruthless simplicity, clear boundaries
- **Tools**: All tools available

### Researcher Agent
- **Purpose**: Information gathering and analysis
- **Temperature**: 1.0 (standard)
- **Focus**: Comprehensive research, web search
- **Tools**: Web tools primarily

### Implementer Agent
- **Purpose**: Code implementation
- **Temperature**: 0.3 (precise and deterministic)
- **Focus**: Clean, working code
- **Tools**: Filesystem, bash

### Reviewer Agent
- **Purpose**: Code review and quality assessment
- **Temperature**: 0.7
- **Focus**: Finding issues, suggesting improvements
- **Tools**: Filesystem, search tools

## Using Sub-Agents

The task tool enables delegation:
```
"Create a task for the architect agent to design an authentication system"
```

The AI will use the task tool with:
- agent: "architect"
- task: "Design an authentication system"
- context: Additional information if needed

## Agent Behavior Guidelines

1. **Be Direct**: No unnecessary preambles or conclusions
2. **Think First**: Plan before implementing
3. **Use Tools**: Leverage available tools effectively
4. **Fail Gracefully**: Handle errors meaningfully
5. **Stay Focused**: Complete the assigned task

## Tool Usage Patterns

- **Read** before **Write** or **Edit**
- Use **Grep** to find code patterns
- Use **Glob** to discover files
- Use **Task** for complex multi-step work
- Use **/think** for planning without modifications
