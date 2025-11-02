"""Tests for memory extraction configuration"""

import os
from pathlib import Path
from unittest.mock import patch

from amplifier.extraction.config import MemoryExtractionConfig
from amplifier.extraction.config import get_config
from amplifier.extraction.config import reset_config


class TestMemoryExtractionConfig:
    """Unit tests for configuration"""

    def setup_method(self):
        """Reset singleton and clear environment before each test"""
        reset_config()
        # Clear all config-related environment variables to ensure test isolation
        env_vars = [
            "MEMORY_SYSTEM_ENABLED",
            "MEMORY_EXTRACTION_MODEL",
            "MEMORY_EXTRACTION_TIMEOUT",
            "MEMORY_EXTRACTION_MAX_MESSAGES",
            "MEMORY_EXTRACTION_MAX_CONTENT_LENGTH",
            "MEMORY_EXTRACTION_MAX_MEMORIES",
            "MEMORY_STORAGE_DIR",
            "ANTHROPIC_API_KEY",
        ]
        for var in env_vars:
            os.environ.pop(var, None)

    def teardown_method(self):
        """Reset config singleton after each test"""
        reset_config()

    def test_default_values(self):
        """Config should have sensible defaults"""
        # Create config without loading .env file
        reset_config()
        config = MemoryExtractionConfig(_env_file=None)  # type: ignore[call-arg]

        assert config.memory_system_enabled is False
        assert config.memory_extraction_model == "claude-3-5-haiku-20241022"
        assert config.memory_extraction_timeout == 120
        assert config.memory_extraction_max_messages == 20
        assert config.memory_extraction_max_content_length == 500
        assert config.memory_extraction_max_memories == 10
        assert config.memory_storage_dir == Path(".data/memories")

    def test_env_override_enabled_flag(self):
        """MEMORY_SYSTEM_ENABLED env var should enable system"""
        with patch.dict(os.environ, {"MEMORY_SYSTEM_ENABLED": "true"}):
            reset_config()
            config = get_config()
            assert config.memory_system_enabled is True

    def test_env_override_disabled_flag(self):
        """MEMORY_SYSTEM_ENABLED=false should disable system"""
        with patch.dict(os.environ, {"MEMORY_SYSTEM_ENABLED": "false"}):
            reset_config()
            config = get_config()
            assert config.memory_system_enabled is False

    def test_env_override_timeout(self):
        """MEMORY_EXTRACTION_TIMEOUT env var should set timeout"""
        with patch.dict(os.environ, {"MEMORY_EXTRACTION_TIMEOUT": "60"}):
            reset_config()
            config = get_config()
            assert config.memory_extraction_timeout == 60

    def test_env_override_model(self):
        """MEMORY_EXTRACTION_MODEL env var should set model"""
        with patch.dict(os.environ, {"MEMORY_EXTRACTION_MODEL": "claude-3-opus-20240229"}):
            reset_config()
            config = get_config()
            assert config.memory_extraction_model == "claude-3-opus-20240229"

    def test_env_override_max_messages(self):
        """MEMORY_EXTRACTION_MAX_MESSAGES env var should set limit"""
        with patch.dict(os.environ, {"MEMORY_EXTRACTION_MAX_MESSAGES": "50"}):
            reset_config()
            config = get_config()
            assert config.memory_extraction_max_messages == 50

    def test_env_override_max_content_length(self):
        """MEMORY_EXTRACTION_MAX_CONTENT_LENGTH env var should set limit"""
        with patch.dict(os.environ, {"MEMORY_EXTRACTION_MAX_CONTENT_LENGTH": "1000"}):
            reset_config()
            config = get_config()
            assert config.memory_extraction_max_content_length == 1000

    def test_env_override_storage_dir(self):
        """MEMORY_STORAGE_DIR env var should set directory"""
        with patch.dict(os.environ, {"MEMORY_STORAGE_DIR": "/custom/path"}):
            reset_config()
            config = get_config()
            assert config.memory_storage_dir == Path("/custom/path")

    def test_singleton_pattern(self):
        """get_config() should return same instance"""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_reset_config(self):
        """reset_config() should create new instance"""
        config1 = get_config()
        reset_config()
        config2 = get_config()
        assert config1 is not config2

    def test_ensure_storage_dir_creates_directory(self, tmp_path):
        """ensure_storage_dir() should create directory if missing"""
        test_dir = tmp_path / "test_memories"
        config = MemoryExtractionConfig(memory_storage_dir=test_dir)

        assert not test_dir.exists()
        result = config.ensure_storage_dir()
        assert test_dir.exists()
        assert result == test_dir

    def test_ensure_storage_dir_idempotent(self, tmp_path):
        """ensure_storage_dir() should work on existing directory"""
        test_dir = tmp_path / "existing_memories"
        test_dir.mkdir(parents=True)
        config = MemoryExtractionConfig(memory_storage_dir=test_dir)

        result = config.ensure_storage_dir()
        assert test_dir.exists()
        assert result == test_dir


class TestConfigurationIntegration:
    """Integration tests for configuration usage"""

    def setup_method(self):
        """Reset singleton and clear environment before each test"""
        reset_config()
        # Clear all config-related environment variables to ensure test isolation
        env_vars = [
            "MEMORY_SYSTEM_ENABLED",
            "MEMORY_EXTRACTION_MODEL",
            "MEMORY_EXTRACTION_TIMEOUT",
            "MEMORY_EXTRACTION_MAX_MESSAGES",
            "MEMORY_EXTRACTION_MAX_CONTENT_LENGTH",
            "MEMORY_EXTRACTION_MAX_MEMORIES",
            "MEMORY_STORAGE_DIR",
            "ANTHROPIC_API_KEY",
        ]
        for var in env_vars:
            os.environ.pop(var, None)

    def teardown_method(self):
        """Reset config singleton after each test"""
        reset_config()

    def test_extractor_uses_config_timeout(self):
        """MemoryExtractor should respect configured timeout"""
        from unittest.mock import MagicMock

        from amplifier.extraction.core import MemoryExtractor

        with patch.dict(os.environ, {"MEMORY_EXTRACTION_TIMEOUT": "90"}):
            reset_config()
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                extractor = MemoryExtractor()
                assert extractor.config.memory_extraction_timeout == 90

    def test_extractor_uses_config_model(self):
        """MemoryExtractor should respect configured model"""
        from unittest.mock import MagicMock

        from amplifier.extraction.core import MemoryExtractor

        with patch.dict(os.environ, {"MEMORY_EXTRACTION_MODEL": "claude-3-opus-20240229"}):
            reset_config()
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                extractor = MemoryExtractor()
                assert extractor.config.memory_extraction_model == "claude-3-opus-20240229"

    def test_memory_store_uses_config_storage_dir(self, tmp_path):
        """MemoryStore should respect configured storage directory"""
        from amplifier.memory.core import MemoryStore

        test_dir = tmp_path / "custom_storage"
        with patch.dict(os.environ, {"MEMORY_STORAGE_DIR": str(test_dir)}):
            reset_config()
            store = MemoryStore()
            assert store.data_dir == test_dir
            assert test_dir.exists()
