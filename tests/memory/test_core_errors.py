"""Tests for memory/core.py error handling paths"""

import errno
import json
from unittest.mock import patch

from amplifier.memory.core import MemoryStore
from amplifier.memory.models import Memory


class TestMemoryStoreErrors:
    """Tests for error handling in MemoryStore"""

    def test_save_data_handles_disk_full(self, tmp_path, caplog):
        """Disk full during save logs error (doesn't raise due to error handling)"""
        import logging

        caplog.set_level(logging.ERROR)

        store = MemoryStore(data_dir=tmp_path, max_memories=10)

        # Add a memory
        memory = Memory(content="Test content", category="learning", metadata={})
        store.add_memory(memory)

        # Mock file write to raise "No space left on device" error
        with patch("builtins.open", side_effect=OSError(errno.ENOSPC, "No space left on device")):
            store._save_data()

        # Verify error was logged (MemoryStore catches and logs OSError)
        assert "Failed to save data" in caplog.text

    def test_load_data_handles_corrupted_json(self, tmp_path):
        """Corrupted JSON file handled gracefully"""
        data_file = tmp_path / "memory.json"

        # Write corrupted JSON
        data_file.write_text("{invalid json content}")

        # Initialize store - should handle corrupted file gracefully
        store = MemoryStore(data_dir=tmp_path)

        # Should return default structure, not crash
        assert isinstance(store._data, dict)
        assert "memories" in store._data
        assert len(store._memories) == 0

    def test_rotate_memories_preserves_recent(self, tmp_path):
        """Rotation keeps most recently accessed memories"""
        store = MemoryStore(data_dir=tmp_path, max_memories=5)

        # Add memories one at a time and trigger rotation
        memory_ids = []
        for i in range(10):
            memory = Memory(content=f"Content {i}", category="learning", metadata={})
            stored = store.add_memory(memory)
            memory_ids.append((stored.id, i))

            # Access some memories more frequently
            if i % 2 == 0:
                # Access even-numbered memories multiple times
                for _ in range(5):
                    store.get_by_id(stored.id)

        # Manually trigger rotation
        store._rotate_memories()

        # Should have rotated to max_memories
        assert len(store._memories) == 5

        # Frequently accessed memories should be preserved
        remaining_contents = [m.content for m in store.get_all()]

        # Even-numbered memories (0, 2, 4, 6, 8) should be more likely to remain
        # because they have higher access counts
        frequently_accessed = sum(1 for content in remaining_contents if int(content.split()[-1]) % 2 == 0)

        # At least some frequently accessed should remain
        assert frequently_accessed >= 2

    @patch("amplifier.memory.core.logger")
    def test_load_data_logs_json_error(self, mock_logger, tmp_path):
        """JSON decode error is logged"""
        data_file = tmp_path / "memory.json"
        data_file.write_text("{bad: json}")

        MemoryStore(data_dir=tmp_path)

        # Verify error was logged
        mock_logger.error.assert_called_once()
        error_msg = mock_logger.error.call_args[0][0]
        assert "Failed to load memories" in error_msg

    def test_extract_memories_handles_missing_fields(self, tmp_path):
        """Missing fields in stored memories handled gracefully"""
        data_file = tmp_path / "memory.json"

        # Write memories with missing fields
        data = {
            "memories": [
                {"id": "mem-1", "content": "Test", "category": "test"},  # Missing timestamp
                {"content": "Test 2", "category": "test"},  # Missing id
            ]
        }

        with open(data_file, "w") as f:
            json.dump(data, f)

        # Should load without crashing
        store = MemoryStore(data_dir=tmp_path)

        # Should have skipped invalid entries
        assert len(store._memories) <= 1

    def test_save_data_creates_parent_directory(self, tmp_path):
        """Parent directory created if missing"""
        nested_dir = tmp_path / "nested" / "deep" / "path"
        store = MemoryStore(data_dir=nested_dir, max_memories=10)

        memory = Memory(content="Test", category="learning", metadata={})
        store.add_memory(memory)

        # Directory should be created
        assert nested_dir.exists()
        assert (nested_dir / "memory.json").exists()
