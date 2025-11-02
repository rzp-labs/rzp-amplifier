"""Tests for defensive file I/O utilities with cloud sync retry logic"""

import errno
import json
from unittest.mock import mock_open
from unittest.mock import patch

import pytest

from amplifier.ccsdk_toolkit.defensive.file_io import read_json_with_retry
from amplifier.ccsdk_toolkit.defensive.file_io import write_json_with_retry


class TestWriteJsonWithRetry:
    """Tests for write_json_with_retry function"""

    def test_write_succeeds_first_try(self, tmp_path):
        """Normal write succeeds without retry"""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "nested": {"items": [1, 2, 3]}}

        write_json_with_retry(test_data, test_file)

        # Verify file was written correctly
        assert test_file.exists()
        with open(test_file) as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data

    @patch("time.sleep")  # Don't actually sleep during tests
    @patch(
        "builtins.open",
        side_effect=[
            OSError(errno.EIO, "I/O error"),  # First attempt fails with errno 5
            mock_open()(),  # Second attempt succeeds
        ],
    )
    def test_write_retries_on_errno_5(self, mock_open_func, mock_sleep, tmp_path):
        """OSError errno 5 triggers retry (cloud sync scenario)"""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value"}

        # Create parent directory (won't be mocked)
        test_file.parent.mkdir(parents=True, exist_ok=True)

        # Mock the open function to fail once, then succeed
        with patch(
            "builtins.open", side_effect=[OSError(errno.EIO, "I/O error"), mock_open()(test_file, "w")]
        ) as mock_file:
            # Should succeed after retry
            write_json_with_retry(test_data, test_file, max_retries=3, initial_delay=0.1)

            # Verify retry occurred
            assert mock_file.call_count == 2
            # Verify sleep was called (exponential backoff)
            mock_sleep.assert_called_once_with(0.1)

    @patch("time.sleep")
    def test_write_retry_backoff_timing(self, mock_sleep, tmp_path):
        """Exponential backoff timing is correct"""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value"}

        # Mock open to fail multiple times
        error_count = 0

        def mock_open_with_retries(*args, **kwargs):
            nonlocal error_count
            error_count += 1
            if error_count < 3:  # Fail first 2 attempts
                raise OSError(errno.EIO, "I/O error")
            # Third attempt succeeds
            return mock_open()(*args, **kwargs)

        with patch("builtins.open", side_effect=mock_open_with_retries):
            write_json_with_retry(test_data, test_file, max_retries=4, initial_delay=0.5)

            # Verify exponential backoff: 0.5s, 1.0s
            assert mock_sleep.call_count == 2
            calls = [call[0][0] for call in mock_sleep.call_args_list]
            assert calls == [0.5, 1.0]  # Exponential doubling

    def test_write_max_retries_exhausted(self, tmp_path):
        """Max retries raises original error"""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value"}

        # Mock open to always fail with errno 5
        with patch("builtins.open", side_effect=OSError(errno.EIO, "I/O error")):
            with pytest.raises(OSError) as exc_info:
                write_json_with_retry(test_data, test_file, max_retries=2)

            # Verify it's the original OSError
            assert exc_info.value.errno == errno.EIO

    @patch("amplifier.ccsdk_toolkit.defensive.file_io.logger")
    @patch("time.sleep")
    def test_write_logs_cloud_sync_warning(self, mock_sleep, mock_logger, tmp_path):
        """Cloud sync warning logged on first retry"""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value"}

        # Fail once then succeed
        with patch("builtins.open", side_effect=[OSError(errno.EIO, "I/O error"), mock_open()(test_file, "w")]):
            write_json_with_retry(test_data, test_file)

            # Verify warning logged
            mock_logger.warning.assert_called_once()
            warning_msg = mock_logger.warning.call_args[0][0]
            assert "cloud-synced files" in warning_msg
            assert "OneDrive" in warning_msg or "Dropbox" in warning_msg


class TestReadJsonWithRetry:
    """Tests for read_json_with_retry function"""

    def test_read_returns_default_on_missing_file(self, tmp_path):
        """Missing file returns default value"""
        test_file = tmp_path / "nonexistent.json"
        default_value = {"default": "data"}

        result = read_json_with_retry(test_file, default=default_value)

        assert result == default_value

    def test_read_succeeds_first_try(self, tmp_path):
        """Normal read succeeds without retry"""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "list": [1, 2, 3]}

        # Write test data
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        result = read_json_with_retry(test_file)

        assert result == test_data

    @patch("time.sleep")
    def test_read_retries_on_errno_5(self, mock_sleep, tmp_path):
        """OSError errno 5 triggers retry"""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value"}

        # Create the file
        test_file.write_text(json.dumps(test_data))

        # Mock open to fail once then succeed
        original_open = open
        call_count = 0

        def mock_open_with_retry(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise OSError(errno.EIO, "I/O error")
            return original_open(*args, **kwargs)

        with patch("builtins.open", side_effect=mock_open_with_retry):
            result = read_json_with_retry(test_file)

            # Verify retry occurred
            assert result == test_data
            mock_sleep.assert_called_once()

    def test_read_returns_default_on_json_decode_error(self, tmp_path):
        """Invalid JSON returns default without raising exception"""
        test_file = tmp_path / "bad.json"
        default_value = {}

        # Write invalid JSON
        test_file.write_text("{invalid json}")

        result = read_json_with_retry(test_file, default=default_value)

        assert result == default_value

    @patch("amplifier.ccsdk_toolkit.defensive.file_io.logger")
    def test_read_logs_invalid_json_error(self, mock_logger, tmp_path):
        """Invalid JSON error is logged"""
        test_file = tmp_path / "bad.json"
        test_file.write_text("{malformed}")

        read_json_with_retry(test_file, default={})

        # Verify error logged
        mock_logger.error.assert_called_once()
        error_msg = mock_logger.error.call_args[0][0]
        assert "Invalid JSON" in error_msg
