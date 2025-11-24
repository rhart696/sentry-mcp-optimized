"""
Sentry integration adaptor
Efficient error tracking without loading massive tool definitions
"""

import os
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
import structlog

logger = structlog.get_logger()

class SentryAdaptor:
    """Sentry API integration with minimal overhead"""

    def __init__(self, auth_token: Optional[str] = None, org_slug: Optional[str] = None):
        self.auth_token = auth_token or os.getenv("SENTRY_AUTH_TOKEN")
        self.org_slug = org_slug or os.getenv("SENTRY_ORG_SLUG", "my-org")
        self.base_url = "https://sentry.io/api/0"

        if not self.auth_token:
            raise ValueError("SENTRY_AUTH_TOKEN required")

    @property
    def headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.auth_token}"}

    async def list_issues(self, project: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        List recent issues - replaces traditional MCP tool loading
        Returns structured data directly
        """
        url = f"{self.base_url}/projects/{self.org_slug}/{project}/issues/"
        params = {"limit": limit, "statsPeriod": "24h"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as resp:
                resp.raise_for_status()
                issues = await resp.json()

                # Return minimal structured data (saves tokens)
                return [
                    {
                        "id": issue["id"],
                        "title": issue["title"],
                        "level": issue.get("level", "error"),
                        "count": issue.get("count", 0),
                        "first_seen": issue.get("firstSeen"),
                        "last_seen": issue.get("lastSeen")
                    }
                    for issue in issues
                ]

    async def get_issue_details(self, issue_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific issue"""
        url = f"{self.base_url}/issues/{issue_id}/"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                resp.raise_for_status()
                issue = await resp.json()

                # Extract relevant fields only
                return {
                    "id": issue["id"],
                    "title": issue["title"],
                    "culprit": issue.get("culprit"),
                    "metadata": issue.get("metadata", {}),
                    "tags": issue.get("tags", [])
                }

    async def get_latest_event(self, issue_id: str) -> Dict[str, Any]:
        """Get the latest event (with stack trace) for an issue"""
        url = f"{self.base_url}/issues/{issue_id}/events/latest/"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                resp.raise_for_status()
                event = await resp.json()

                # Extract stack trace
                stack_trace = []
                if "exception" in event:
                    for exc in event["exception"].get("values", []):
                        if "stacktrace" in exc:
                            for frame in exc["stacktrace"].get("frames", []):
                                stack_trace.append({
                                    "filename": frame.get("filename"),
                                    "function": frame.get("function"),
                                    "lineno": frame.get("lineno"),
                                    "context_line": frame.get("contextLine")
                                })

                return {
                    "event_id": event["id"],
                    "message": event.get("message"),
                    "platform": event.get("platform"),
                    "stack_trace": stack_trace
                }

    async def analyze_error(self, issue_id: str) -> Dict[str, Any]:
        """
        Complete error analysis in one efficient call
        This is what replaces the multi-tool MCP approach
        """
        # Get both issue details and latest event in parallel
        issue_task = self.get_issue_details(issue_id)
        event_task = self.get_latest_event(issue_id)

        issue, event = await asyncio.gather(issue_task, event_task)

        # Combine into analysis
        return {
            "issue": issue,
            "event": event,
            "analysis": {
                "primary_file": event["stack_trace"][0]["filename"] if event["stack_trace"] else None,
                "error_type": issue["metadata"].get("type"),
                "suggested_fix": self._suggest_fix(issue, event)
            }
        }

    def _suggest_fix(self, issue: Dict, event: Dict) -> str:
        """Simple heuristic-based fix suggestion"""
        error_type = issue["metadata"].get("type", "")

        if "AttributeError" in error_type:
            return "Check for None values before accessing attributes"
        elif "KeyError" in error_type:
            return "Use dict.get() with default values"
        elif "TypeError" in error_type:
            return "Verify function arguments match expected types"
        else:
            return "Review stack trace for root cause"
