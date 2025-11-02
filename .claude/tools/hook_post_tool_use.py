#!/workspaces/rzp-amplifier/.venv/bin/python3
"""
Claude Code hook for PostToolUse events - minimal wrapper for claim validation.
Reads JSON from stdin, calls amplifier modules, writes JSON to stdout.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add amplifier to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import logger from the same directory
sys.path.insert(0, str(Path(__file__).parent))
from hook_logger import HookLogger

logger = HookLogger("post_tool_use")

try:
    from amplifier.memory import MemoryStore
    from amplifier.orchestration import DelegationAudit
    from amplifier.validation import ClaimValidator
except ImportError as e:
    logger.error(f"Failed to import amplifier modules: {e}")
    # Exit gracefully to not break hook chain
    json.dump({}, sys.stdout)
    sys.exit(0)


def detect_agent_session() -> bool:
    """Determine if this is an agent session or main orchestrator.

    Agents are spawned via Task tool, so check for markers:
    - Environment variable set by Task spawning
    - Session context metadata
    """
    import os

    # Method 1: Check session metadata
    session_context = os.getenv("CLAUDE_SESSION_CONTEXT", "")
    if "agent:" in session_context:
        return True

    # Method 2: Check if Task tool was used in parent chain
    parent_tools = os.getenv("CLAUDE_PARENT_TOOLS", "").split(",")
    return "Task" in parent_tools


def validate_orchestrator_boundary(tool_name: str, tool_input: dict, session_id: str | None = None) -> dict:
    """Enforce main orchestrator cannot modify files directly.

    Phase 2: Validation (log warnings, don't block yet)
    Phase 3: Enforcement (will block violations)
    """
    # Modification tools that require delegation
    modification_tools = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

    if tool_name not in modification_tools:
        return {"status": "allowed"}

    if detect_agent_session():
        return {"status": "allowed"}  # Agents can modify

    # Main orchestrator attempting modification
    file_path = tool_input.get("file_path", "unknown")

    # Record violation in audit log if session_id provided
    if session_id:
        try:
            audit = DelegationAudit(session_id)
            audit.record_modification(file_path, tool_name, "main")
        except Exception as e:
            logger.error(f"Failed to record delegation audit: {e}")

    violation_msg = f"""
⚠️  ORCHESTRATOR BOUNDARY VIOLATION (Phase 2: Validation)

Main Claude attempted to use {tool_name} on: {file_path}

Your Role: Orchestrator
  ✅ Allowed: Read, Grep, TodoWrite, Task, Bash, AskUserQuestion
  ❌ Blocked: Edit, Write, MultiEdit (must delegate via Task)

Required Action: Use Task tool to delegate to specialized agent

Available Agents:
  • modular-builder: Code implementation and module creation
  • bug-hunter: Bug diagnosis and fix implementation
  • test-coverage: Test creation and coverage
  • refactor-architect: Code refactoring

Example Delegation:
  Task: modular-builder
  Prompt: "Implement fix for {file_path}: [specification]"

Phase 2: This is a WARNING only. Logging violation.
Phase 3: Will BLOCK this operation completely.
    """.strip()

    logger.warning(violation_msg)

    # Phase 2: Allow but warn
    # Phase 3: Will return error and block
    return {"status": "warning", "message": violation_msg, "file": file_path, "tool": tool_name}


async def main():
    """Read input, validate claims, return warnings if contradictions found"""
    try:
        # Load .env file to get environment variables
        import os

        from dotenv import load_dotenv

        # Load .env from repository root (3 levels up from this script)
        env_path = Path(__file__).parent.parent.parent / ".env"
        load_dotenv(dotenv_path=env_path)

        # Check if memory system is enabled

        memory_enabled = os.getenv("MEMORY_SYSTEM_ENABLED", "false").lower() in ["true", "1", "yes"]
        if not memory_enabled:
            logger.info("Memory system disabled via MEMORY_SYSTEM_ENABLED env var")
            # Return empty response and exit gracefully
            json.dump({}, sys.stdout)
            return

        logger.info("Starting post-tool-use validation")
        logger.cleanup_old_logs()  # Clean up old logs on each run

        # Read JSON input
        raw_input = sys.stdin.read()
        logger.info(f"Received input length: {len(raw_input)}")

        input_data = json.loads(raw_input)

        # Extract tool information for boundary validation
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        session_id = input_data.get("session_id")

        # Validate orchestrator boundary (Phase 2: warnings only)
        if tool_name:
            boundary_result = validate_orchestrator_boundary(tool_name, tool_input, session_id)
            if boundary_result["status"] == "warning":
                # In Phase 2, we log the warning but don't block
                logger.warning(f"Boundary violation detected: {tool_name} on {boundary_result.get('file', 'unknown')}")

        # Extract message for claim validation
        message = input_data.get("message", {})
        role = message.get("role", "")
        content = message.get("content", "")

        logger.debug(f"Message role: {role}")
        logger.debug(f"Content length: {len(content)}")

        # Skip if not assistant message or too short
        if role != "assistant" or not content or len(content) < 50:
            logger.info(f"Skipping: role={role}, content_len={len(content)}")
            json.dump({}, sys.stdout)
            return

        # Initialize modules
        logger.info("Initializing store and validator")
        store = MemoryStore()
        validator = ClaimValidator()

        # Get all memories for validation
        memories = store.get_all()
        logger.info(f"Total memories for validation: {len(memories)}")

        # Validate text for claims
        logger.info("Validating text for claims")
        validation_result = validator.validate_text(content, memories)
        logger.info(f"Has contradictions: {validation_result.has_contradictions}")
        logger.info(f"Claims found: {len(validation_result.claims)}")

        # Build response if contradictions found
        output = {}
        if validation_result.has_contradictions:
            warnings = []
            for claim_validation in validation_result.claims:
                if claim_validation.contradicts and claim_validation.confidence > 0.6:
                    claim_text = claim_validation.claim[:100]
                    warnings.append(f"⚠️ Claim may be incorrect: '{claim_text}...'")

                    if claim_validation.evidence:
                        evidence = claim_validation.evidence[0][:150]
                        warnings.append(f"   Memory says: {evidence}")

            if warnings:
                output = {
                    "warning": "\n".join(warnings),
                    "metadata": {
                        "contradictionsFound": sum(1 for c in validation_result.claims if c.contradicts),
                        "claimsChecked": len(validation_result.claims),
                        "source": "amplifier_validation",
                    },
                }

        json.dump(output, sys.stdout)

        if output:
            logger.info(f"Returned {len(warnings) if 'warnings' in locals() else 0} warnings")
        else:
            logger.info("No contradictions found")

    except Exception as e:
        logger.exception("Error during claim validation", e)
        json.dump({}, sys.stdout)


if __name__ == "__main__":
    asyncio.run(main())
