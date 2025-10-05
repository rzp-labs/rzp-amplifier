"""
Tests for Amplifier core session functionality.
"""
import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch

from amplifier_core import AmplifierSession
from amplifier_core.testing import (
    create_test_coordinator,
    MockProvider,
    MockTool,
    EventRecorder
)


@pytest.mark.asyncio
async def test_session_initialization():
    """Test session can be initialized."""
    session = AmplifierSession()
    
    assert session.session_id is not None
    assert session.coordinator is not None
    assert session.loader is not None
    assert not session._initialized


@pytest.mark.asyncio
async def test_session_with_config():
    """Test session accepts configuration."""
    config = {
        'session': {
            'orchestrator': 'test-orchestrator',
            'context': 'test-context'
        }
    }
    
    session = AmplifierSession(config)
    assert session.config['session']['orchestrator'] == 'test-orchestrator'


@pytest.mark.asyncio
async def test_session_context_manager():
    """Test session works as async context manager."""
    async with AmplifierSession() as session:
        assert session is not None
        # Would be initialized here if modules were available
    # Cleanup should be called after exit


@pytest.mark.asyncio
async def test_session_execute_requires_modules():
    """Test session execution requires modules to be mounted."""
    session = AmplifierSession()
    
    # Without initialization, should fail
    with pytest.raises(RuntimeError, match="No orchestrator"):
        await session.execute("Test prompt")


@pytest.mark.asyncio
async def test_session_with_mock_modules():
    """Test session with mock modules."""
    # This would require setting up mock module loading
    # For now, directly mount mock modules
    session = AmplifierSession()
    
    # Create mock orchestrator
    mock_orchestrator = AsyncMock()
    mock_orchestrator.execute = AsyncMock(return_value="Test response")
    
    # Create mock context
    mock_context = Mock()
    mock_context.add_message = AsyncMock()
    mock_context.get_messages = AsyncMock(return_value=[])
    
    # Mount mocks directly (bypassing loader for testing)
    session.coordinator.mount_points['orchestrator'] = mock_orchestrator
    session.coordinator.mount_points['context'] = mock_context
    session.coordinator.mount_points['providers'] = {'mock': MockProvider()}
    
    session._initialized = True
    
    # Now execution should work
    result = await session.execute("Test prompt")
    assert result == "Test response"
    
    # Verify orchestrator was called
    mock_orchestrator.execute.assert_called_once()
