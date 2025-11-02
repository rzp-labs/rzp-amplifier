#!/workspaces/rzp-amplifier/.venv/bin/python3
"""
Claude Code hook for Stop/SubagentStop events - minimal wrapper for memory extraction.
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

logger = HookLogger("stop_hook")

try:
    from amplifier.extraction import MemoryExtractor
    from amplifier.memory import MemoryStore
    from amplifier.orchestration import DelegationAudit
except ImportError as e:
    logger.error(f"Failed to import amplifier modules: {e}")
    # Exit gracefully to not break hook chain
    json.dump({}, sys.stdout)
    sys.exit(0)


def generate_delegation_report(session_id: str) -> str | None:
    """Generate delegation boundary violation report if violations exist.

    Returns:
        Report string if violations found, None if clean session
    """
    try:
        audit = DelegationAudit(session_id)
        result = audit.validate_session()

        if result["status"] == "clean":
            return None

        return audit.report()

    except Exception as e:
        logger.error(f"Failed to generate delegation report: {e}")
        return None


async def main():
    """Read input, extract memories, store and return count"""
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
            json.dump(
                {"metadata": {"memoriesExtracted": 0, "source": "amplifier_extraction", "disabled": True}}, sys.stdout
            )
            return

        logger.info("Starting memory extraction")
        logger.cleanup_old_logs()  # Clean up old logs on each run

        # Timeout must be longer than EXTRACTION_TIMEOUT_SECONDS (120s) + buffer (60s)
        # to allow memory extraction to complete successfully
        async with asyncio.timeout(180):  # Hook timeout: 180s (extraction: 120s + 60s buffer)
            # Read JSON input
            raw_input = sys.stdin.read()
            logger.info(f"Received input length: {len(raw_input)}")

            # Debug: Show first 1000 chars of raw input
            logger.debug(f"Raw input preview: {raw_input[:1000]}")

            input_data = json.loads(raw_input)

            # Debug: Show all keys in input_data
            logger.debug(f"Input keys: {list(input_data.keys())}")

            # Debug: Show structure of input_data (without full content)
            logger.structure_preview("Input structure", input_data)

            # Initialize messages list
            messages = []

            # Check if we have a transcript_path - this is the new format
            if "transcript_path" in input_data:
                transcript_path = input_data["transcript_path"]
                logger.info(f"Found transcript_path: {transcript_path}")

                # Read the JSONL transcript file
                try:
                    transcript_file = Path(transcript_path)
                    if transcript_file.exists():
                        logger.info(f"Reading transcript file: {transcript_file}")

                        # Read and parse JSONL (each line is a separate JSON object)
                        raw_messages = []
                        with open(transcript_file) as f:
                            for line_num, line in enumerate(f, 1):
                                line = line.strip()
                                if not line:
                                    continue
                                try:
                                    # Parse each line as JSON
                                    msg = json.loads(line)
                                    raw_messages.append(msg)
                                except json.JSONDecodeError as e:
                                    logger.error(f"Error parsing line {line_num}: {e}")
                                    logger.debug(f"Line content: {line[:200]}")

                        logger.info(f"Loaded {len(raw_messages)} raw messages from transcript")

                        # Filter and extract actual conversation messages
                        for msg in raw_messages:
                            # Skip non-conversation messages
                            if msg.get("type") in ["summary", "meta", "system"]:
                                continue

                            # Extract nested message structure
                            if "message" in msg and isinstance(msg["message"], dict):
                                inner_msg = msg["message"]
                                # Only include user and assistant messages with content
                                if inner_msg.get("role") in ["user", "assistant"]:
                                    # Handle content array structure
                                    content = inner_msg.get("content", "")
                                    if isinstance(content, list):
                                        # Extract text from content array
                                        text_parts = []
                                        for item in content:
                                            if isinstance(item, dict) and item.get("type") == "text":
                                                text_parts.append(item.get("text", ""))
                                        content = " ".join(text_parts)

                                    if content:  # Only add if there's actual content
                                        messages.append({"role": inner_msg["role"], "content": content})

                        logger.info(f"Filtered to {len(messages)} conversation messages (user/assistant)")

                        # Debug: Show structure of first conversation message if available
                        if messages:
                            first_msg = messages[0]
                            logger.debug(
                                f"First conversation message keys: {list(first_msg.keys()) if isinstance(first_msg, dict) else 'Not a dict'}"
                            )
                            if isinstance(first_msg, dict):
                                # Show message structure without full content
                                msg_preview = {
                                    "role": first_msg.get("role", "NO_ROLE"),
                                    "content_preview": str(first_msg.get("content", ""))[:100]
                                    if "content" in first_msg
                                    else "NO_CONTENT",
                                }
                                logger.json_preview("First conversation message preview", msg_preview)
                    else:
                        logger.warning(f"Transcript file does not exist: {transcript_file}")
                except Exception as e:
                    logger.error(f"Error reading transcript file: {e}")

            # Fall back to looking for messages in the input data directly (old format)
            if not messages:
                logger.info("No transcript_path, looking for messages in input data")

                # Try direct "messages" key
                if "messages" in input_data:
                    messages = input_data.get("messages", [])
                    logger.info("Found messages at root level")

                # Try "conversation" key (alternative name)
                elif "conversation" in input_data:
                    messages = input_data.get("conversation", [])
                    logger.info("Found messages under 'conversation' key")

                # Try "history" key (another alternative)
                elif "history" in input_data:
                    messages = input_data.get("history", [])
                    logger.info("Found messages under 'history' key")

                # Try nested under "data"
                elif "data" in input_data and isinstance(input_data["data"], dict):
                    data_obj = input_data["data"]
                    if "messages" in data_obj:
                        messages = data_obj.get("messages", [])
                        logger.info("Found messages under 'data.messages'")
                    elif "conversation" in data_obj:
                        messages = data_obj.get("conversation", [])
                        logger.info("Found messages under 'data.conversation'")
                    elif "history" in data_obj:
                        messages = data_obj.get("history", [])
                        logger.info("Found messages under 'data.history'")

                # Try looking for any list that looks like messages
                if not messages:
                    logger.info("No standard message location found, checking for message-like lists")
                    for key, value in input_data.items():
                        if isinstance(value, list) and len(value) > 0:
                            # Check if first item looks like a message
                            first_item = value[0]
                            if isinstance(first_item, dict) and "role" in first_item and "content" in first_item:
                                messages = value
                                logger.info(f"Found message-like list under '{key}' key")
                                break

            logger.info(f"Total messages found: {len(messages)}")

            if not messages:
                logger.warning("No messages to process, exiting")
                json.dump({"metadata": {"memoriesExtracted": 0, "source": "amplifier_extraction"}}, sys.stdout)
                return

            # Get context from first user message
            context = None
            for msg in messages:
                if msg.get("role") == "user":
                    context = msg.get("content", "")[:200]
                    logger.debug(f"Found context: {context[:50]}...")
                    break

            # Initialize modules
            logger.info("Initializing extractor and store")
            extractor = MemoryExtractor()
            store = MemoryStore()

            # Check data directory
            logger.debug(f"Data directory: {store.data_dir}")
            logger.debug(f"Data file: {store.data_file}")
            logger.debug(f"Data file exists: {store.data_file.exists()}")

            # Extract memories from messages
            logger.info("Starting extraction from messages")
            extracted = await extractor.extract_from_messages(messages, context)
            logger.json_preview("Extraction result", extracted)

            # Store extracted memories
            memories_count = 0
            if extracted and "memories" in extracted:
                memories_list = extracted.get("memories", [])
                logger.info(f"Found {len(memories_list)} memories to store")

                store.add_memories_batch(extracted)
                memories_count = len(memories_list)

                logger.info(f"Stored {memories_count} memories")
                logger.info(f"Total memories in store: {len(store.get_all())}")
            else:
                logger.warning("No memories extracted")

            # Generate delegation boundary report
            session_id = input_data.get("session_id", "unknown")
            delegation_report = generate_delegation_report(session_id)

            # Track extraction status
            extraction_status = "success" if memories_count > 0 else "failed"
            extraction_error = None

            # Build response
            output = {
                "metadata": {
                    "memoriesExtracted": memories_count,
                    "source": "amplifier_extraction",
                    "extractionStatus": extraction_status,
                    "extractionError": extraction_error,
                    "delegationViolations": delegation_report is not None,
                }
            }

            if delegation_report:
                logger.info("Delegation boundary violations detected")
                logger.info(delegation_report)
                output["metadata"]["delegationReport"] = delegation_report
            else:
                logger.info("Clean session - all modifications properly delegated")

            logger.info(f"Returning output: {json.dumps(output)}")
            json.dump(output, sys.stdout)

    except TimeoutError:
        logger.error("Memory extraction timed out after 180 seconds")
        extraction_error = "Extraction timeout (180s exceeded)"
        json.dump(
            {
                "metadata": {
                    "memoriesExtracted": 0,
                    "extractionStatus": "timeout",
                    "extractionError": extraction_error,
                    "source": "amplifier_extraction",
                }
            },
            sys.stdout,
        )
    except Exception as e:
        logger.exception("Memory extraction failed with error")
        extraction_error = str(e)
        json.dump(
            {
                "metadata": {
                    "memoriesExtracted": 0,
                    "extractionStatus": "error",
                    "extractionError": extraction_error,
                    "source": "amplifier_extraction",
                }
            },
            sys.stdout,
        )


if __name__ == "__main__":
    asyncio.run(main())
