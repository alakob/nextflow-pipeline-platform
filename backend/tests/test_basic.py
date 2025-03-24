"""
Basic test to verify the test environment is set up correctly
"""
import os
import sys
import pytest

# Ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_environment_setup():
    """Verify test environment is working"""
    assert True, "Basic test passed"


@pytest.mark.asyncio
async def test_async_function():
    """Verify async testing works"""
    # This is a simple async test
    result = await sample_async_function()
    assert result == "success"


async def sample_async_function():
    """Sample async function for testing"""
    return "success"
