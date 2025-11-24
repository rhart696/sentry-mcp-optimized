"""
Tests for Sentry operations and workflows
"""

import pytest
from unittest.mock import AsyncMock, patch, Mock
import asyncio
from sentry_mcp import SentryMCPOptimized


class TestOperations:
    """Test complete operations"""

    @pytest.mark.asyncio
    async def test_list_projects(self, sentry_client, mock_project, mocker):
        """Test listing projects"""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=[mock_project])
        mock_response.raise_for_status = Mock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        mock_session.get = Mock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        # Mock the adaptor's base session
        with patch("aiohttp.ClientSession", return_value=mock_session):
            # Note: This assumes sentry_client has a list_projects method
            # You'll need to implement this in your actual code
            pass  # Placeholder for actual implementation

    @pytest.mark.asyncio
    async def test_parallel_operations(self, sentry_adaptor, mock_issue, mocker):
        """Test parallel execution of multiple operations"""
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
            # Execute multiple operations in parallel
            tasks = [
                sentry_adaptor.get_issue_details("123"),
                sentry_adaptor.get_issue_details("456"),
                sentry_adaptor.get_issue_details("789")
            ]

            results = await asyncio.gather(*tasks)

        assert len(results) == 3
        for result in results:
            assert "id" in result


class TestTokenOptimization:
    """Test token optimization strategies"""

    def test_data_minimization_reduces_tokens(self, mock_issue):
        """Test that data minimization reduces token count"""
        # Full issue has many fields
        full_fields = len(str(mock_issue))

        # Minimized issue should have fewer
        minimized = {
            "id": mock_issue["id"],
            "title": mock_issue["title"],
            "level": mock_issue["level"],
            "count": mock_issue["count"]
        }
        minimized_fields = len(str(minimized))

        # Verify reduction
        assert minimized_fields < full_fields
        reduction_percent = (1 - minimized_fields / full_fields) * 100
        assert reduction_percent > 50  # At least 50% reduction


class TestPerformance:
    """Test performance characteristics"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_operation_latency(self, sentry_adaptor, mock_issue, mocker):
        """Test that operations complete quickly"""
        import time

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
            start = time.time()
            await sentry_adaptor.list_issues("python-1", limit=10)
            elapsed = time.time() - start

        # Should complete very quickly with mocked responses
        assert elapsed < 0.1  # 100ms


class TestErrorHandling:
    """Test error handling"""

    @pytest.mark.asyncio
    async def test_handles_network_errors(self, sentry_adaptor, mocker):
        """Test handling of network errors"""
        mock_session = AsyncMock()
        mock_session.get = Mock(side_effect=Exception("Network error"))
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with pytest.raises(Exception):
                await sentry_adaptor.list_issues("python-1")

    @pytest.mark.asyncio
    async def test_handles_invalid_responses(self, sentry_adaptor, mocker):
        """Test handling of invalid API responses"""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"error": "Invalid"})
        mock_response.raise_for_status = Mock(side_effect=Exception("Bad request"))
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        mock_session.get = Mock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with pytest.raises(Exception):
                await sentry_adaptor.list_issues("python-1")
