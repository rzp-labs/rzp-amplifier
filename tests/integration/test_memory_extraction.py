"""End-to-end integration tests for memory extraction"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from amplifier.extraction.config import reset_config
from amplifier.extraction.core import MemoryExtractor
from amplifier.memory.core import MemoryStore
from amplifier.memory.models import Memory


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directory"""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def extractor():
    """Create MemoryExtractor instance"""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        return MemoryExtractor()


@pytest.mark.integration
class TestEndToEndExtraction:
    """Complete flow: transcript → extraction → storage"""

    @pytest.mark.asyncio
    async def test_end_to_end_extraction(self, extractor, temp_data_dir):
        """Complete flow: transcript → extraction → storage"""
        transcript_path = Path(__file__).parent.parent / "fixtures/transcripts/valid_session.jsonl"

        messages = []
        with open(transcript_path) as f:
            for line in f:
                if line.strip():
                    messages.append(json.loads(line))

        mock_extraction_result = {
            "memories": [
                {"type": "learning", "content": "Use asyncio.timeout()", "importance": 0.8, "tags": ["python"]},
                {"type": "decision", "content": "120s timeout for extraction", "importance": 0.7, "tags": ["config"]},
            ],
            "key_learnings": ["asyncio.timeout() for async operations"],
            "decisions_made": ["Use 120 second timeout"],
            "issues_solved": [],
            "metadata": {"extraction_method": "claude_sdk", "timestamp": datetime.now().isoformat()},
        }

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = mock_extraction_result

            result = await extractor.extract_from_messages(messages)

            assert result is not None
            assert len(result["memories"]) == 2

            store = MemoryStore(data_dir=temp_data_dir)
            store.add_memories_batch(result)

            memories = store.get_all()
            assert len(memories) == 2

            memory_types = {m.category for m in memories}
            assert "learning" in memory_types
            assert "decision" in memory_types

            assert (temp_data_dir / "memory.json").exists()

    @pytest.mark.asyncio
    async def test_extraction_failure_preserves_transcript(self, extractor, tmp_path):
        """Failed extraction doesn't lose transcript"""
        transcript_path = tmp_path / "session.jsonl"
        messages = [{"role": "user", "content": "Test message"}]

        with open(transcript_path, "w") as f:
            for msg in messages:
                f.write(json.dumps(msg) + "\n")

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.side_effect = TimeoutError("Extraction timed out")

            with pytest.raises(TimeoutError):
                with open(transcript_path) as f:
                    loaded_messages = [json.loads(line) for line in f if line.strip()]
                await extractor.extract_from_messages(loaded_messages)

            assert transcript_path.exists()
            with open(transcript_path) as f:
                preserved_messages = [json.loads(line) for line in f if line.strip()]
            assert len(preserved_messages) == len(messages)

    @pytest.mark.asyncio
    async def test_multiple_sessions_dont_interfere(self, extractor, temp_data_dir):
        """Multiple sessions extract independently"""
        session1_messages = [{"role": "user", "content": "Session 1 message"}]
        session2_messages = [{"role": "user", "content": "Session 2 message"}]

        mock_result_1 = {
            "memories": [{"type": "learning", "content": "Learning 1", "importance": 0.5, "tags": []}],
            "key_learnings": ["Session 1"],
            "decisions_made": [],
            "issues_solved": [],
            "metadata": {"extraction_method": "claude_sdk"},
        }

        mock_result_2 = {
            "memories": [{"type": "decision", "content": "Decision 2", "importance": 0.6, "tags": []}],
            "key_learnings": [],
            "decisions_made": ["Session 2"],
            "issues_solved": [],
            "metadata": {"extraction_method": "claude_sdk"},
        }

        store = MemoryStore(data_dir=temp_data_dir)

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = mock_result_1
            result1 = await extractor.extract_from_messages(session1_messages)
            store.add_memories_batch(result1)

            mock_extract.return_value = mock_result_2
            result2 = await extractor.extract_from_messages(session2_messages)
            store.add_memories_batch(result2)

        all_memories = store.get_all()
        assert len(all_memories) == 2

        contents = {m.content for m in all_memories}
        assert "Learning 1" in contents
        assert "Decision 2" in contents


@pytest.mark.integration
class TestExtractionWithStorage:
    """Integration tests between extraction and storage"""

    def teardown_method(self):
        """Reset config after each test"""
        reset_config()

    @pytest.mark.asyncio
    async def test_extracted_memories_stored_correctly(self, extractor, temp_data_dir):
        """Extracted memories should store with correct structure"""
        messages = [{"role": "user", "content": "I decided to use pytest for testing"}]

        mock_result = {
            "memories": [
                {"type": "decision", "content": "Use pytest for testing", "importance": 0.9, "tags": ["testing"]}
            ],
            "key_learnings": [],
            "decisions_made": ["Use pytest"],
            "issues_solved": [],
            "metadata": {"extraction_method": "claude_sdk"},
        }

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = mock_result

            result = await extractor.extract_from_messages(messages)

            store = MemoryStore(data_dir=temp_data_dir)
            store.add_memories_batch(result)

            stored_memories = store.get_all()
            assert len(stored_memories) == 1

            memory = stored_memories[0]
            assert memory.content == "Use pytest for testing"
            assert memory.category == "decision"
            assert memory.metadata["importance"] == 0.9
            assert "testing" in memory.metadata["tags"]

    @pytest.mark.asyncio
    async def test_storage_persists_across_instances(self, extractor, temp_data_dir):
        """Stored memories should persist across MemoryStore instances"""
        messages = [{"role": "user", "content": "Persistent memory test"}]

        mock_result = {
            "memories": [{"type": "pattern", "content": "Test persistence", "importance": 0.7, "tags": []}],
            "key_learnings": [],
            "decisions_made": [],
            "issues_solved": [],
            "metadata": {"extraction_method": "claude_sdk"},
        }

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = mock_result
            result = await extractor.extract_from_messages(messages)

            store1 = MemoryStore(data_dir=temp_data_dir)
            store1.add_memories_batch(result)

            store2 = MemoryStore(data_dir=temp_data_dir)
            memories = store2.get_all()

            assert len(memories) == 1
            assert memories[0].content == "Test persistence"

    @pytest.mark.asyncio
    async def test_batch_add_preserves_structured_data(self, extractor, temp_data_dir):
        """add_memories_batch should preserve key_learnings, decisions, issues"""
        messages = [{"role": "user", "content": "Test structured data"}]

        mock_result = {
            "memories": [{"type": "learning", "content": "Test memory", "importance": 0.5, "tags": []}],
            "key_learnings": ["Important learning 1", "Important learning 2"],
            "decisions_made": ["Critical decision"],
            "issues_solved": ["Fixed bug X"],
            "metadata": {"extraction_method": "claude_sdk"},
        }

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.return_value = mock_result
            result = await extractor.extract_from_messages(messages)

            store = MemoryStore(data_dir=temp_data_dir)
            store.add_memories_batch(result)

            with open(temp_data_dir / "memory.json") as f:
                data = json.load(f)

            assert "key_learnings" in data
            assert len(data["key_learnings"]) == 2
            assert "decisions_made" in data
            assert len(data["decisions_made"]) == 1
            assert "issues_solved" in data
            assert len(data["issues_solved"]) == 1


@pytest.mark.integration
class TestErrorRecovery:
    """Tests for error handling and recovery"""

    @pytest.mark.asyncio
    async def test_timeout_doesnt_corrupt_storage(self, extractor, temp_data_dir):
        """Extraction timeout shouldn't corrupt existing storage"""
        store = MemoryStore(data_dir=temp_data_dir)
        existing_memory = Memory(content="Existing memory", category="learning", metadata={})
        store.add_memory(existing_memory)

        messages = [{"role": "user", "content": "This will timeout"}]

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.side_effect = TimeoutError("Timeout")

            with pytest.raises(TimeoutError):
                await extractor.extract_from_messages(messages)

        store2 = MemoryStore(data_dir=temp_data_dir)
        memories = store2.get_all()
        assert len(memories) == 1
        assert memories[0].content == "Existing memory"

    @pytest.mark.asyncio
    async def test_json_error_doesnt_corrupt_storage(self, extractor, temp_data_dir):
        """JSON parse error shouldn't corrupt existing storage"""
        store = MemoryStore(data_dir=temp_data_dir)
        existing_memory = Memory(content="Existing memory", category="decision", metadata={})
        store.add_memory(existing_memory)

        messages = [{"role": "user", "content": "This will fail JSON parse"}]

        with patch.object(extractor, "_extract_with_claude_full") as mock_extract:
            mock_extract.side_effect = json.JSONDecodeError("Invalid", "", 0)

            with pytest.raises(json.JSONDecodeError):
                await extractor.extract_from_messages(messages)

        store2 = MemoryStore(data_dir=temp_data_dir)
        memories = store2.get_all()
        assert len(memories) == 1
        assert memories[0].content == "Existing memory"
