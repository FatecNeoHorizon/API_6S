"""
Pytest configuration and fixtures for backend tests.

Handles mocking of external dependencies (PostgreSQL, MongoDB) to allow
tests to run without external services.
"""

import sys
from unittest.mock import MagicMock, patch
import pytest


def pytest_configure(config):
    """
    Configure pytest to mock database connections before importing test modules.
    This runs before test discovery and collection.
    """
    # Mock psycopg2 SimpleConnectionPool to prevent connection attempts during imports
    try:
        import psycopg2.pool
        psycopg2.pool.SimpleConnectionPool = MagicMock(return_value=MagicMock())
    except ImportError:
        pass

    # src/config/__init__.py imports setup_middleware at package level, which
    # triggers pending_consent_middleware → user_repository circular import.
    # Pre-populate sys.modules so the package __init__ is a no-op during tests.
    sys.modules.setdefault("src.config.middleware", MagicMock())
    sys.modules.setdefault("src.config.pending_consent_middleware", MagicMock())


@pytest.fixture
def mock_mongo_client(monkeypatch):
    """Fixture to provide a mock MongoDB client"""
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    return mock_client
