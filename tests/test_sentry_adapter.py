"""
Unit tests for SentryAdaptor
"""

import pytest
from unittest.mock import AsyncMock, patch, Mock
from sentry_mcp.adaptors.sentry import SentryAdaptor
from sentry_mcp import AuthenticationError, NotFoundError


class TestSentryAdaptorInit:
    """Test SentryAdaptor initialization"""

    def test_init_with_params(self):
        """Test initialization with explicit parameters"""
        adaptor = SentryAdaptor(
            auth_token="test_token",
            org_slug="test-org"
        )

        assert adaptor.auth_token == "test_token"
        assert adaptor.org_slug == "test-org"
        assert adaptor.base_url == "https://sentry.io/api/0"

    def test_init_from_env(self, monkeypatch):
        """Test initialization from environment variables"""
        monkeypatch.setenv("SENTRY_AUTH_TOKEN", "env_token")
        monkeypatch.setenv("SENTRY_ORG_SLUG", "env-org")

        adaptor = SentryAdaptor()

        assert adaptor.auth_token == "env_token"
        assert adaptor.org_slug == "env-org"

    def test_init_without_token_raises_error(self, monkeypatch):
        """Test that missing token raises ValueError"""
        monkeypatch.delenv("SENTRY_AUTH_TOKEN", raising=False)

        with pytest.raises(ValueError, match="SENTRY_AUTH_TOKEN required"):
            SentryAdaptor()

    def test_headers_property(self, sentry_adaptor):
        """Test headers property includes auth token"""
        headers = sentry_adaptor.headers

        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")


class TestListIssues:
    """Test list_issues method"""

    @pytest.mark.asyncio
    async def test_list_issues_success(self, sentry_adaptor, mock_issue, mocker):
        """Test successful issue listing"""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=[mock_issue])
        mock_response.raise_for_status = Mock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        mock_session.get = Mock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            issues = await sentry_adaptor.list_issues(
                project="python-1",
                limit=5
            )

        assert len(issues) == 1
        assert issues[0]["id"] == mock_issue["id"]
        assert issues[0]["title"] == mock_issue["title"]
        assert "id" in issues[0]
        assert "title" in issues[0]
        assert "level" in issues[0]
        assert "count" in issues[0]

    @pytest.mark.asyncio
    async def test_list_issues_minimizes_data(self, sentry_adaptor, mock_issue, mocker):
        """Test that list_issues returns minimized data"""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=[mock_issue])
        mock_response.raise_for_status = Mock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        mock_session.get = Mock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            issues = await sentry_adaptor.list_issues(
                project="python-1",
                limit=1
            )

        # Ensure only minimal fields are returned
        issue = issues[0]
        expected_fields = {"id", "title", "level", "count", "first_seen", "last_seen"}
        assert set(issue.keys()) == expected_fields


class TestGetIssueDetails:
    """Test get_issue_details method"""

    @pytest.mark.asyncio
    async def test_get_issue_details_success(self, sentry_adaptor, mock_issue, mocker):
        """Test successful issue details retrieval"""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=mock_issue)
        mock_response.raise_for_status = Mock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        mock_session.get = Mock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            issue = await sentry_adaptor.get_issue_details("4740575428")

        assert issue["id"] == mock_issue["id"]
        assert issue["title"] == mock_issue["title"]
        assert issue["culprit"] == mock_issue["culprit"]
        assert "metadata" in issue
        assert "tags" in issue


class TestGetLatestEvent:
    """Test get_latest_event method"""

    @pytest.mark.asyncio
    async def test_get_latest_event_success(self, sentry_adaptor, mock_event, mocker):
        """Test successful latest event retrieval"""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=mock_event)
        mock_response.raise_for_status = Mock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        mock_session.get = Mock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            event = await sentry_adaptor.get_latest_event("4740575428")

        assert event["event_id"] == mock_event["id"]
        assert event["platform"] == mock_event["platform"]
        assert "stack_trace" in event
        assert len(event["stack_trace"]) > 0

    @pytest.mark.asyncio
    async def test_get_latest_event_extracts_stack_trace(self, sentry_adaptor, mock_event, mocker):
        """Test that stack trace is properly extracted"""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=mock_event)
        mock_response.raise_for_status = Mock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        mock_session.get = Mock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            event = await sentry_adaptor.get_latest_event("4740575428")

        frame = event["stack_trace"][0]
        assert frame["filename"] == "app/views.py"
        assert frame["function"] == "user_profile"
        assert frame["lineno"] == 45
        assert "contextLine" in frame or "context_line" in frame


class TestAnalyzeError:
    """Test analyze_error method"""

    @pytest.mark.asyncio
    async def test_analyze_error_combines_data(self, sentry_adaptor, mock_issue, mock_event, mocker):
        """Test that analyze_error combines issue and event data"""
        # Mock both get_issue_details and get_latest_event
        with patch.object(sentry_adaptor, 'get_issue_details', return_value=mock_issue):
            with patch.object(sentry_adaptor, 'get_latest_event', return_value={
                "event_id": "abc123",
                "stack_trace": [{"filename": "app/views.py"}],
                **mock_event
            }):
                analysis = await sentry_adaptor.analyze_error("4740575428")

        assert "issue" in analysis
        assert "event" in analysis
        assert "analysis" in analysis

        # Check analysis contains expected fields
        assert "primary_file" in analysis["analysis"]
        assert "error_type" in analysis["analysis"]
        assert "suggested_fix" in analysis["analysis"]

    @pytest.mark.asyncio
    async def test_analyze_error_suggests_fix(self, sentry_adaptor, mocker):
        """Test that analyze_error provides fix suggestions"""
        mock_issue = {
            "id": "123",
            "title": "Test",
            "metadata": {"type": "AttributeError"}
        }
        mock_event = {
            "event_id": "abc",
            "stack_trace": [{"filename": "test.py"}]
        }

        with patch.object(sentry_adaptor, 'get_issue_details', return_value=mock_issue):
            with patch.object(sentry_adaptor, 'get_latest_event', return_value=mock_event):
                analysis = await sentry_adaptor.analyze_error("123")

        suggested_fix = analysis["analysis"]["suggested_fix"]
        assert isinstance(suggested_fix, str)
        assert len(suggested_fix) > 0


class TestSuggestFix:
    """Test _suggest_fix helper method"""

    def test_suggest_fix_attribute_error(self, sentry_adaptor):
        """Test fix suggestion for AttributeError"""
        issue = {"metadata": {"type": "AttributeError"}}
        event = {}

        fix = sentry_adaptor._suggest_fix(issue, event)

        assert "None" in fix or "attribute" in fix

    def test_suggest_fix_key_error(self, sentry_adaptor):
        """Test fix suggestion for KeyError"""
        issue = {"metadata": {"type": "KeyError"}}
        event = {}

        fix = sentry_adaptor._suggest_fix(issue, event)

        assert "dict.get()" in fix or "default" in fix

    def test_suggest_fix_type_error(self, sentry_adaptor):
        """Test fix suggestion for TypeError"""
        issue = {"metadata": {"type": "TypeError"}}
        event = {}

        fix = sentry_adaptor._suggest_fix(issue, event)

        assert "type" in fix.lower() or "argument" in fix.lower()

    def test_suggest_fix_generic(self, sentry_adaptor):
        """Test generic fix suggestion for unknown error"""
        issue = {"metadata": {"type": "UnknownError"}}
        event = {}

        fix = sentry_adaptor._suggest_fix(issue, event)

        assert "stack trace" in fix.lower() or "review" in fix.lower()
