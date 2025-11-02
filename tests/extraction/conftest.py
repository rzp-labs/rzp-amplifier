"""Shared fixtures for extraction tests"""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory"""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def transcripts_dir(fixtures_dir):
    """Path to transcript fixtures"""
    return fixtures_dir / "transcripts"


@pytest.fixture
def valid_transcript(transcripts_dir):
    """Path to valid session transcript"""
    return transcripts_dir / "valid_session.jsonl"


@pytest.fixture
def large_transcript(transcripts_dir):
    """Path to large session transcript"""
    return transcripts_dir / "large_session.jsonl"


@pytest.fixture
def empty_transcript(transcripts_dir):
    """Path to empty session transcript"""
    return transcripts_dir / "empty_session.jsonl"


@pytest.fixture
def corrupted_transcript(transcripts_dir):
    """Path to corrupted session transcript"""
    return transcripts_dir / "corrupted_session.jsonl"


@pytest.fixture
def system_messages_transcript(transcripts_dir):
    """Path to transcript with system messages"""
    return transcripts_dir / "system_messages_session.jsonl"
