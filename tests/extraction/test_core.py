"""Unit tests for MemoryExtractor core functionality"""

import json
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from amplifier.extraction.core import MemoryExtractor


@pytest.fixture
def extractor():
    """Create MemoryExtractor instance with mocked Claude CLI check"""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        return MemoryExtractor()


@pytest.fixture
def sample_messages():
    """Sample conversation messages for testing"""
    return [
        {"role": "user", "content": "How do I handle timeouts in Python?"},
        {"role": "assistant", "content": "Use asyncio.timeout() for async operations"},
        {"role": "user", "content": "I'll use 120 seconds as default timeout"},
    ]


@pytest.fixture
def sample_memories_response():
    """Sample valid JSON response from Claude SDK"""
    return json.dumps(
        {
            "memories": [
                {
                    "type": "decision",
                    "content": "Use 120s timeout for extraction",
                    "importance": 0.8,
                    "tags": ["python"],
                }
            ],
            "key_learnings": ["asyncio.timeout() for async operations"],
            "decisions_made": ["120 second timeout"],
            "issues_solved": [],
        }
    )


class TestMemoryExtractor:
    """Unit tests for MemoryExtractor"""

    def test_init_claude_cli_not_found(self):
        """Should raise RuntimeError if Claude CLI not installed"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            with pytest.raises(RuntimeError, match="Claude CLI not found"):
                MemoryExtractor()

    def test_init_claude_cli_timeout(self):
        """Should raise RuntimeError if Claude CLI check times out"""
        with patch("subprocess.run") as mock_run:
            from subprocess import TimeoutExpired

            mock_run.side_effect = TimeoutExpired("which", 2)
            with pytest.raises(RuntimeError, match="Claude CLI not found"):
                MemoryExtractor()

    @pytest.mark.asyncio
    async def test_extract_timeout_propagates(self, extractor, sample_messages):
        """TimeoutError should propagate, not be swallowed"""
        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.side_effect = TimeoutError("Extraction timed out")

            with pytest.raises(TimeoutError, match="Extraction timed out"):
                await extractor.extract_from_messages(sample_messages)

    @pytest.mark.asyncio
    async def test_extract_json_decode_error_propagates(self, extractor, sample_messages):
        """JSONDecodeError should propagate"""
        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

            with pytest.raises(json.JSONDecodeError):
                await extractor.extract_from_messages(sample_messages)

    @pytest.mark.asyncio
    async def test_extract_general_exception_propagates(self, extractor, sample_messages):
        """General exceptions should propagate"""
        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.side_effect = RuntimeError("SDK error")

            with pytest.raises(RuntimeError, match="SDK error"):
                await extractor.extract_from_messages(sample_messages)

    @pytest.mark.asyncio
    async def test_extract_success_returns_memories(self, extractor, sample_messages, sample_memories_response):
        """Successful extraction returns memory dict"""
        expected_result = json.loads(sample_memories_response)
        expected_result["metadata"] = {"extraction_method": "claude_sdk", "timestamp": "2025-01-01T00:00:00"}

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = expected_result

            result = await extractor.extract_from_messages(sample_messages)

            assert result is not None
            assert "memories" in result
            assert len(result["memories"]) == 1
            assert result["memories"][0]["type"] == "decision"

    @pytest.mark.asyncio
    async def test_extract_with_empty_messages(self, extractor):
        """Empty message list should raise RuntimeError"""
        with pytest.raises(RuntimeError, match="No messages provided"):
            await extractor.extract_from_messages([])

    @pytest.mark.asyncio
    async def test_extract_with_invalid_messages(self, extractor):
        """Messages with no conversation content should raise RuntimeError"""
        messages = [
            {"role": "system", "content": "system message"},
            {"role": "tool", "content": "tool output"},
        ]

        with pytest.raises(RuntimeError, match="No valid conversation content"):
            await extractor.extract_from_messages(messages)

    @pytest.mark.asyncio
    async def test_extract_with_no_results(self, extractor, sample_messages):
        """Extraction returning None should raise RuntimeError"""
        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = None

            with pytest.raises(RuntimeError, match="extraction failed"):
                await extractor.extract_from_messages(sample_messages)

    def test_format_messages_filters_system_messages(self, extractor):
        """Should filter out system/hook messages"""
        messages = [
            {"role": "user", "content": "Real message"},
            {"role": "assistant", "content": "PostToolUse: hook message"},
            {"role": "assistant", "content": "[HOOK] system message"},
            {"role": "assistant", "content": "Real response"},
        ]

        formatted = extractor._format_messages(messages)

        assert "Real message" in formatted
        assert "Real response" in formatted
        assert "PostToolUse" not in formatted
        assert "[HOOK]" not in formatted

    def test_format_messages_respects_max_messages(self, extractor):
        """Should only process last N messages"""
        messages = [{"role": "user", "content": f"Message {i}"} for i in range(50)]

        formatted = extractor._format_messages(messages)
        formatted_lines = [line for line in formatted.split("\n") if line.strip()]

        # Should only have last 20 messages (default max_messages)
        assert len(formatted_lines) <= 20

    def test_format_messages_truncates_long_content(self, extractor):
        """Should truncate content exceeding max_content_length"""
        long_content = "x" * 1000
        messages = [{"role": "user", "content": long_content}]

        formatted = extractor._format_messages(messages)

        # Should be truncated to max_content_length (500) + "..."
        assert len(formatted) < len(long_content)
        assert "..." in formatted

    def test_is_system_message_detects_hooks(self, extractor):
        """Should detect various hook patterns"""
        hook_messages = [
            "PostToolUse: running checks",
            "PreToolUse: validating",
            "[HOOK] started",
            "Hook started",
            "Running make check",
            "Extract key memories from this conversation",
            "UNKNOWN:",
        ]

        for msg in hook_messages:
            assert extractor._is_system_message(msg) is True

    def test_is_system_message_allows_real_content(self, extractor):
        """Should not filter real conversation content"""
        real_messages = [
            "How do I implement async timeout?",
            "Use asyncio.timeout() context manager",
            "I decided to use 120 seconds as timeout",
        ]

        for msg in real_messages:
            assert extractor._is_system_message(msg) is False

    def test_extract_tags_finds_technical_terms(self, extractor):
        """Should extract relevant technical tags"""
        text = "I'm using Python with asyncio and JSON for my API"
        tags = extractor._extract_tags(text)

        assert "python" in tags
        assert "json" in tags
        assert "api" in tags


class TestMemoryExtractorIntegration:
    """Integration tests with mocked Claude SDK"""

    @pytest.mark.asyncio
    async def test_extract_from_real_transcript(self, extractor):
        """Extract from actual transcript file"""
        transcript_path = Path(__file__).parent.parent / "fixtures/transcripts/valid_session.jsonl"

        messages = []
        with open(transcript_path) as f:
            for line in f:
                if line.strip():
                    messages.append(json.loads(line))

        mock_response = {
            "memories": [
                {"type": "learning", "content": "Use asyncio.timeout()", "importance": 0.7, "tags": ["python"]}
            ],
            "key_learnings": ["asyncio.timeout() for async operations"],
            "decisions_made": [],
            "issues_solved": [],
            "metadata": {"extraction_method": "claude_sdk"},
        }

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = mock_response

            result = await extractor.extract_from_messages(messages)

            assert result is not None
            assert len(result["memories"]) == 1
            mock_extract.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_handles_large_transcript(self, extractor):
        """Large transcripts should complete within timeout"""
        transcript_path = Path(__file__).parent.parent / "fixtures/transcripts/large_session.jsonl"

        messages = []
        with open(transcript_path) as f:
            for line in f:
                if line.strip():
                    messages.append(json.loads(line))

        mock_response = {
            "memories": [{"type": "decision", "content": "Use pytest fixtures", "importance": 0.8, "tags": []}],
            "key_learnings": [],
            "decisions_made": ["Use pytest fixtures"],
            "issues_solved": [],
            "metadata": {"extraction_method": "claude_sdk"},
        }

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = mock_response

            result = await extractor.extract_from_messages(messages)

            assert result is not None
            # Verify we had more than max_messages so formatting limit was tested
            assert len(messages) > 20
