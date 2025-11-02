"""Tests for knowledge synthesis event emitter"""

import errno
import json
import time
from unittest.mock import patch

from amplifier.knowledge_synthesis.events import EventEmitter


class TestEventEmitter:
    """Tests for EventEmitter class"""

    def test_emit_writes_event_to_file(self, tmp_path):
        """Event emitted and saved to JSONL"""
        events_file = tmp_path / "events.jsonl"
        emitter = EventEmitter(path=events_file)

        emitter.emit("test_event", source_id="src-123", stage="testing", data={"key": "value"})

        # Verify file exists and contains event
        assert events_file.exists()
        with open(events_file) as f:
            line = f.readline()
            event_data = json.loads(line)

        assert event_data["event"] == "test_event"
        assert event_data["source_id"] == "src-123"
        assert event_data["stage"] == "testing"
        assert event_data["data"] == {"key": "value"}
        assert "timestamp" in event_data

    @patch("time.sleep")
    def test_emit_retries_on_io_error(self, mock_sleep, tmp_path):
        """OSError errno 5 triggers retry"""
        events_file = tmp_path / "events.jsonl"
        emitter = EventEmitter(path=events_file)

        # Mock open to fail once then succeed
        original_open = open
        call_count = 0

        def mock_open_with_retry(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1 and args[0] == events_file:
                raise OSError(errno.EIO, "I/O error")
            return original_open(*args, **kwargs)

        with patch("builtins.open", side_effect=mock_open_with_retry):
            emitter.emit("test_event", source_id="src-456")

        # Verify retry occurred (sleep was called)
        mock_sleep.assert_called()

        # Verify event was eventually saved
        assert events_file.exists()

    def test_tail_returns_recent_events(self, tmp_path):
        """Tail returns last N events"""
        events_file = tmp_path / "events.jsonl"
        emitter = EventEmitter(path=events_file)

        # Emit 10 events
        for i in range(10):
            emitter.emit(f"event_{i}", source_id=f"src-{i}", data={"index": i})
            time.sleep(0.01)  # Small delay to ensure different timestamps

        # Tail last 5 events
        recent = emitter.tail(n=5)

        assert len(recent) == 5
        # Should be most recent events (5-9)
        assert recent[0].data["index"] == 5  # type: ignore[index]
        assert recent[-1].data["index"] == 9  # type: ignore[index]

    def test_tail_filters_by_event_type(self, tmp_path):
        """Filtering by event type works"""
        events_file = tmp_path / "events.jsonl"
        emitter = EventEmitter(path=events_file)

        # Emit events of different types
        emitter.emit("type_a", source_id="src-1", data={"value": 1})
        emitter.emit("type_b", source_id="src-2", data={"value": 2})
        emitter.emit("type_a", source_id="src-3", data={"value": 3})
        emitter.emit("type_b", source_id="src-4", data={"value": 4})
        emitter.emit("type_a", source_id="src-5", data={"value": 5})

        # Filter for type_a only
        type_a_events = emitter.tail(n=10, event_filter="type_a")

        assert len(type_a_events) == 3
        assert all(e.event == "type_a" for e in type_a_events)
        assert [e.data["value"] for e in type_a_events] == [1, 3, 5]  # type: ignore[index]

    def test_emit_handles_empty_log_file(self, tmp_path):
        """Empty file doesn't break tail"""
        events_file = tmp_path / "events.jsonl"
        emitter = EventEmitter(path=events_file)

        # Tail before any events emitted
        recent = emitter.tail()

        assert recent == []

    def test_tail_handles_malformed_json_lines(self, tmp_path):
        """Malformed JSON lines are skipped gracefully"""
        events_file = tmp_path / "events.jsonl"

        # Write some valid and invalid lines
        with open(events_file, "w") as f:
            f.write('{"timestamp": 1.0, "event": "valid1", "source_id": "src-1"}\n')
            f.write("{invalid json}\n")
            f.write('{"timestamp": 2.0, "event": "valid2", "source_id": "src-2"}\n')

        emitter = EventEmitter(path=events_file)
        events = emitter.tail()

        # Should only return valid events
        assert len(events) == 2
        assert events[0].event == "valid1"
        assert events[1].event == "valid2"

    @patch("amplifier.knowledge_synthesis.events.logger")
    @patch("time.sleep")
    def test_emit_logs_cloud_sync_warning(self, mock_sleep, mock_logger, tmp_path):
        """Cloud sync warning logged on first retry"""
        events_file = tmp_path / "events.jsonl"
        emitter = EventEmitter(path=events_file)

        # Mock open to fail once
        with patch("builtins.open", side_effect=[OSError(errno.EIO, "I/O error"), open(events_file, "a")]):
            emitter.emit("test", source_id="src-1")

        # Verify warning logged
        mock_logger.warning.assert_called_once()
        warning_msg = mock_logger.warning.call_args[0][0]
        assert "cloud-synced files" in warning_msg

    def test_tail_respects_n_limit(self, tmp_path):
        """Tail respects the n parameter limit"""
        events_file = tmp_path / "events.jsonl"
        emitter = EventEmitter(path=events_file)

        # Emit 100 events
        for i in range(100):
            emitter.emit(f"event_{i}", source_id=f"src-{i}")

        # Tail with different limits
        tail_10 = emitter.tail(n=10)
        tail_5 = emitter.tail(n=5)
        tail_all = emitter.tail(n=200)

        assert len(tail_10) == 10
        assert len(tail_5) == 5
        assert len(tail_all) == 100  # All events
