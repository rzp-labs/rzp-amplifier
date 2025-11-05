#!/workspaces/rzp-amplifier/.venv/bin/python3
"""
Claude Code hook for PostToolUse events - validates claims and detects boundary violations.

Detects orchestrator boundary violations and provides feedback for learning.
Enforcement is via system prompt (CLAUDE.md), not blocking.
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
    from amplifier.validation import ClaimValidator
except ImportError as e:
    logger.error(f"Failed to import amplifier modules: {e}")
    # Exit gracefully to not break hook chain
    json.dump({}, sys.stdout)
    sys.exit(0)


def validate_orchestrator_boundary(tool_name: str, tool_input: dict) -> dict:
    """Detect orchestrator boundary violations for feedback.

    System prompt enforcement - this only provides feedback for learning.
    """
    # Modification tools that should be delegated
    modification_tools = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

    if tool_name not in modification_tools:
        return {"status": "allowed"}

    # Violation detected - provide feedback
    file_path = tool_input.get("file_path", "unknown")

    logger.warning(f"⚠️ BOUNDARY VIOLATION: {tool_name} on {file_path}")

    return {"status": "warning", "file": file_path, "tool": tool_name}


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

        # Extract tool information for boundary detection
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Detect orchestrator boundary violations (provides feedback only)
        if tool_name:
            boundary_result = validate_orchestrator_boundary(tool_name, tool_input)

            if boundary_result["status"] == "warning":
                # Log violation for feedback - enforcement is via system prompt
                logger.warning(
                    f"⚠️ BOUNDARY VIOLATION DETECTED: {tool_name} on {boundary_result.get('file', 'unknown')}"
                )
                logger.warning("Reminder: Delegate file modifications via Task tool to specialized agents")

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
