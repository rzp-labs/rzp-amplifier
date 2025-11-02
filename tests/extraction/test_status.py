"""Tests for extraction status reporting and metadata"""

import json
from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from amplifier.extraction.core import MemoryExtractor


@pytest.fixture
def extractor():
    """Create MemoryExtractor instance"""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        return MemoryExtractor()


class TestExtractionMetadata:
    """Tests for extraction metadata structure"""

    @pytest.mark.asyncio
    async def test_success_metadata_structure(self, extractor):
        """Success metadata should have required fields"""
        messages = [{"role": "user", "content": "Test message"}]

        mock_response = {
            "memories": [{"type": "learning", "content": "Test learning", "importance": 0.5, "tags": []}],
            "key_learnings": ["Test"],
            "decisions_made": [],
            "issues_solved": [],
            "metadata": {"extraction_method": "claude_sdk", "timestamp": datetime.now().isoformat()},
        }

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = mock_response

            result = await extractor.extract_from_messages(messages)

            assert "metadata" in result
            assert result["metadata"]["extraction_method"] == "claude_sdk"
            assert "timestamp" in result["metadata"]
            assert "memories" in result
            assert len(result["memories"]) == 1

    @pytest.mark.asyncio
    async def test_timeout_error_has_clear_message(self, extractor):
        """TimeoutError should have informative message"""
        messages = [{"role": "user", "content": "Test"}]

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.side_effect = TimeoutError("Operation timed out")

            with pytest.raises(TimeoutError) as exc_info:
                await extractor.extract_from_messages(messages)

            assert "timed out" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_json_decode_error_has_clear_message(self, extractor):
        """JSONDecodeError should have informative message"""
        messages = [{"role": "user", "content": "Test"}]

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.side_effect = json.JSONDecodeError("Expecting value", "{invalid", 0)

            with pytest.raises(json.JSONDecodeError):
                await extractor.extract_from_messages(messages)

    @pytest.mark.asyncio
    async def test_extraction_error_messages_are_informative(self, extractor):
        """Error messages should describe actual problem"""
        messages = []

        with pytest.raises(RuntimeError) as exc_info:
            await extractor.extract_from_messages(messages)

        error_msg = str(exc_info.value)
        assert "No messages provided" in error_msg
        assert "error occurred" not in error_msg.lower()

    @pytest.mark.asyncio
    async def test_no_content_error_is_specific(self, extractor):
        """Error for no valid content should be specific"""
        messages = [{"role": "system", "content": "System message only"}]

        with pytest.raises(RuntimeError) as exc_info:
            await extractor.extract_from_messages(messages)

        error_msg = str(exc_info.value)
        assert "No valid conversation content" in error_msg

    @pytest.mark.asyncio
    async def test_empty_response_error_is_specific(self, extractor):
        """Error for empty SDK response should be specific"""
        messages = [{"role": "user", "content": "Test"}]

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = None

            with pytest.raises(RuntimeError) as exc_info:
                await extractor.extract_from_messages(messages)

            error_msg = str(exc_info.value)
            assert "extraction failed" in error_msg.lower()
            assert "no results" in error_msg.lower()


class TestMemoryStructure:
    """Tests for memory object structure"""

    @pytest.mark.asyncio
    async def test_memories_have_required_fields(self, extractor):
        """Each memory should have type, content, importance, tags"""
        messages = [{"role": "user", "content": "I learned something"}]

        mock_response = {
            "memories": [
                {"type": "learning", "content": "Test learning", "importance": 0.7, "tags": ["python", "testing"]}
            ],
            "key_learnings": [],
            "decisions_made": [],
            "issues_solved": [],
            "metadata": {"extraction_method": "claude_sdk"},
        }

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = mock_response

            result = await extractor.extract_from_messages(messages)

            memory = result["memories"][0]
            assert "type" in memory
            assert "content" in memory
            assert "importance" in memory
            assert "tags" in memory
            assert memory["type"] in ["learning", "decision", "issue_solved", "pattern", "preference"]

    @pytest.mark.asyncio
    async def test_metadata_includes_extraction_method(self, extractor):
        """Metadata should indicate extraction method"""
        messages = [{"role": "user", "content": "Test"}]

        mock_response = {
            "memories": [],
            "key_learnings": [],
            "decisions_made": [],
            "issues_solved": [],
            "metadata": {"extraction_method": "claude_sdk", "timestamp": datetime.now().isoformat()},
        }

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = mock_response

            result = await extractor.extract_from_messages(messages)

            assert result["metadata"]["extraction_method"] == "claude_sdk"

    @pytest.mark.asyncio
    async def test_metadata_includes_timestamp(self, extractor):
        """Metadata should include extraction timestamp"""
        messages = [{"role": "user", "content": "Test"}]

        mock_response = {
            "memories": [],
            "key_learnings": [],
            "decisions_made": [],
            "issues_solved": [],
            "metadata": {"extraction_method": "claude_sdk", "timestamp": datetime.now().isoformat()},
        }

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = mock_response

            result = await extractor.extract_from_messages(messages)

            assert "timestamp" in result["metadata"]
            # Verify it's a valid ISO format timestamp
            datetime.fromisoformat(result["metadata"]["timestamp"])


class TestExtractionCounts:
    """Tests for extraction result counts"""

    @pytest.mark.asyncio
    async def test_multiple_memories_counted_correctly(self, extractor):
        """Should correctly count multiple extracted memories"""
        messages = [{"role": "user", "content": "Multiple learnings"}]

        mock_response = {
            "memories": [
                {"type": "learning", "content": "Learning 1", "importance": 0.5, "tags": []},
                {"type": "decision", "content": "Decision 1", "importance": 0.8, "tags": []},
                {"type": "pattern", "content": "Pattern 1", "importance": 0.6, "tags": []},
            ],
            "key_learnings": ["Learning 1"],
            "decisions_made": ["Decision 1"],
            "issues_solved": [],
            "metadata": {"extraction_method": "claude_sdk"},
        }

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = mock_response

            result = await extractor.extract_from_messages(messages)

            assert len(result["memories"]) == 3
            assert len(result["key_learnings"]) == 1
            assert len(result["decisions_made"]) == 1

    @pytest.mark.asyncio
    async def test_empty_memories_handled_correctly(self, extractor):
        """Should handle case where no memories extracted"""
        messages = [{"role": "user", "content": "Nothing memorable"}]

        mock_response = {
            "memories": [],
            "key_learnings": [],
            "decisions_made": [],
            "issues_solved": [],
            "metadata": {"extraction_method": "claude_sdk"},
        }

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = mock_response

            result = await extractor.extract_from_messages(messages)

            assert len(result["memories"]) == 0
            assert "metadata" in result
