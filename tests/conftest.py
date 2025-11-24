"""
Pytest configuration and shared fixtures
"""

import pytest
import os
from unittest.mock import AsyncMock, Mock
from sentry_mcp import SentryAdaptor, SentryMCPOptimized, SentryConfig


@pytest.fixture
def mock_auth_token():
    """Mock Sentry authentication token"""
    return "sntrys_test_token_abc123xyz"


@pytest.fixture
def mock_org_slug():
    """Mock organization slug"""
    return "test-org"


@pytest.fixture
def sentry_config(mock_auth_token, mock_org_slug):
    """Create test Sentry configuration"""
    return SentryConfig(
        auth_token=mock_auth_token,
        organization=mock_org_slug,
        base_url="https://sentry.io",
        request_timeout=30,
        max_retries=3
    )


@pytest.fixture
def sentry_adaptor(mock_auth_token, mock_org_slug):
    """Create SentryAdaptor instance for testing"""
    return SentryAdaptor(
        auth_token=mock_auth_token,
        org_slug=mock_org_slug
    )


@pytest.fixture
def sentry_client(sentry_config):
    """Create SentryMCPOptimized instance for testing"""
    return SentryMCPOptimized(config=sentry_config)


@pytest.fixture
def mock_issue():
    """Mock Sentry issue data"""
    return {
        "id": "4740575428",
        "title": "TypeError: 'NoneType' object is not subscriptable",
        "shortId": "PYTHON-1",
        "level": "error",
        "status": "unresolved",
        "count": "156",
        "userCount": 23,
        "firstSeen": "2024-11-20T10:30:00Z",
        "lastSeen": "2024-11-24T09:15:00Z",
        "culprit": "app.views.user_profile",
        "metadata": {
            "type": "TypeError",
            "value": "'NoneType' object is not subscriptable",
            "filename": "app/views.py"
        },
        "tags": [
            {"key": "environment", "value": "production"},
            {"key": "python_version", "value": "3.11.4"}
        ]
    }


@pytest.fixture
def mock_event():
    """Mock Sentry event data"""
    return {
        "id": "abc123def456",
        "eventID": "abc123def456",
        "message": "TypeError: 'NoneType' object is not subscriptable",
        "platform": "python",
        "timestamp": "2024-11-24T09:15:00Z",
        "exception": {
            "values": [
                {
                    "type": "TypeError",
                    "value": "'NoneType' object is not subscriptable",
                    "module": "builtins",
                    "stacktrace": {
                        "frames": [
                            {
                                "filename": "app/views.py",
                                "function": "user_profile",
                                "lineno": 45,
                                "contextLine": "    return user['profile']['avatar']",
                                "preContext": [
                                    "def user_profile(request, user_id):",
                                    "    user = get_user(user_id)"
                                ],
                                "postContext": [
                                    "",
                                    "def get_user(user_id):"
                                ]
                            }
                        ]
                    }
                }
            ]
        },
        "user": {
            "id": "12345",
            "email": "user@example.com"
        },
        "tags": {
            "environment": "production",
            "server_name": "web-1"
        }
    }


@pytest.fixture
def mock_project():
    """Mock Sentry project data"""
    return {
        "id": "123456",
        "slug": "python-1",
        "name": "Python Backend",
        "platform": "python",
        "status": "active",
        "dateCreated": "2024-01-15T10:00:00Z",
        "features": ["error-tracking", "performance-monitoring"],
        "teams": []
    }


@pytest.fixture
def mock_aiohttp_response(mocker):
    """Mock aiohttp ClientSession response"""
    def _create_response(data, status=200):
        mock_resp = AsyncMock()
        mock_resp.status = status
        mock_resp.json = AsyncMock(return_value=data)
        mock_resp.raise_for_status = Mock()
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=None)
        return mock_resp

    return _create_response


@pytest.fixture(autouse=True)
def set_test_env_vars(monkeypatch, mock_auth_token, mock_org_slug):
    """Set test environment variables for all tests"""
    monkeypatch.setenv("SENTRY_AUTH_TOKEN", mock_auth_token)
    monkeypatch.setenv("SENTRY_ORG_SLUG", mock_org_slug)


@pytest.fixture
def mock_logger(mocker):
    """Mock structlog logger"""
    return mocker.patch("sentry_mcp.adaptors.sentry.logger")


# Markers
def pytest_configure(config):
    """Register custom pytest markers"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires Sentry credentials)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )
