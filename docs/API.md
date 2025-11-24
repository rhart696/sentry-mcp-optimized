# API Reference

Complete API reference for Sentry MCP Optimized v0.1.0.

## Table of Contents

- [Quick Start](#quick-start)
- [SentryMCPOptimized](#sentrymcpoptimized)
- [SentryAdaptor](#sentryadaptor)
- [Issue Operations](#issue-operations)
- [Event Operations](#event-operations)
- [Project Operations](#project-operations)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Type Definitions](#type-definitions)

## Quick Start

```python
from sentry_mcp import SentryMCPOptimized

# Initialize with environment variables
sentry = SentryMCPOptimized(
    auth_token="YOUR_SENTRY_AUTH_TOKEN",
    organization="your-org-slug"
)

# List issues
issues = await sentry.list_issues(project="PYTHON-1", limit=10)

# Get issue details
issue = await sentry.get_issue_details(issue_id="12345")

# Analyze error
analysis = await sentry.analyze_error(issue_id="12345")
```

## SentryMCPOptimized

Main entry point for the optimized Sentry integration.

### Constructor

```python
SentryMCPOptimized(
    auth_token: Optional[str] = None,
    organization: Optional[str] = None,
    config: Optional[SentryConfig] = None
)
```

**Parameters**:
- `auth_token` (str, optional): Sentry authentication token. If not provided, reads from `SENTRY_AUTH_TOKEN` environment variable.
- `organization` (str, optional): Sentry organization slug. If not provided, reads from `SENTRY_ORG_SLUG` environment variable.
- `config` (SentryConfig, optional): Complete configuration object. If provided, overrides other parameters.

**Example**:
```python
# Simple initialization
sentry = SentryMCPOptimized(
    auth_token="sntrys_abc123...",
    organization="my-company"
)

# Advanced initialization with config
from sentry_mcp import SentryConfig, SandboxMode

config = SentryConfig(
    auth_token="sntrys_abc123...",
    organization="my-company",
    base_url="https://sentry.io",
    sandbox_mode=SandboxMode.STRICT,
    enable_metrics=True,
    enable_caching=True,
    cache_ttl=300
)

sentry = SentryMCPOptimized(config=config)
```

## SentryAdaptor

Low-level API adapter. Most users should use `SentryMCPOptimized` instead.

### Constructor

```python
SentryAdaptor(
    auth_token: Optional[str] = None,
    org_slug: Optional[str] = None
)
```

## Issue Operations

### list_issues()

List issues for a project with filtering options.

```python
async def list_issues(
    project: str,
    limit: int = 5,
    status: str = "unresolved",
    query: Optional[str] = None,
    sort: str = "date",
    period: str = "24h"
) -> List[Dict[str, Any]]
```

**Parameters**:
- `project` (str, required): Project slug (e.g., "PYTHON-1")
- `limit` (int, default=5): Maximum number of issues to return (1-100)
- `status` (str, default="unresolved"): Filter by status
  - `"unresolved"`: Active issues
  - `"resolved"`: Fixed issues
  - `"ignored"`: Ignored issues
  - `""`: All issues
- `query` (str, optional): Sentry search query (e.g., "error.type:TypeError")
- `sort` (str, default="date"): Sort order
  - `"date"`: Most recent first
  - `"freq"`: Most frequent first
  - `"priority"`: Highest priority first
  - `"new"`: Newest first
- `period` (str, default="24h"): Time period for stats
  - `"1h"`, `"24h"`, `"7d"`, `"14d"`, `"30d"`

**Returns**: List of issue dictionaries with minimized fields.

**Return Type**:
```python
[
    {
        "id": str,           # Issue ID
        "title": str,        # Issue title
        "level": str,        # error, warning, info
        "count": int,        # Number of occurrences
        "first_seen": str,   # ISO timestamp
        "last_seen": str,    # ISO timestamp
        "status": str,       # resolved, unresolved, ignored
        "assignee": str,     # Assigned user email
        "tags": List[dict]   # Issue tags
    },
    ...
]
```

**Token Usage**: ~207 tokens per call (10 issues)

**Example**:
```python
# List unresolved errors
issues = await sentry.list_issues(
    project="PYTHON-1",
    limit=10,
    status="unresolved"
)

# List TypeError issues sorted by frequency
issues = await sentry.list_issues(
    project="PYTHON-1",
    query="error.type:TypeError",
    sort="freq",
    limit=20
)

# List all issues from last 7 days
issues = await sentry.list_issues(
    project="PYTHON-1",
    status="",
    period="7d",
    limit=50
)
```

**Raises**:
- `ValueError`: If project is empty or limit is invalid
- `AuthenticationError`: If auth token is invalid
- `NotFoundError`: If project doesn't exist
- `APIError`: If Sentry API request fails

---

### get_issue_details()

Get detailed information about a specific issue.

```python
async def get_issue_details(
    issue_id: str
) -> Dict[str, Any]
```

**Parameters**:
- `issue_id` (str, required): Issue ID (e.g., "4740575428")

**Returns**: Detailed issue information.

**Return Type**:
```python
{
    "id": str,
    "title": str,
    "culprit": str,          # Function/module causing issue
    "metadata": {
        "type": str,         # Error type (e.g., "TypeError")
        "value": str,        # Error message
        "filename": str      # File where error occurred
    },
    "tags": [
        {"key": str, "value": str},
        ...
    ],
    "status": str,
    "level": str,
    "count": int,
    "user_count": int,
    "first_seen": str,
    "last_seen": str
}
```

**Token Usage**: ~185 tokens per call

**Example**:
```python
issue = await sentry.get_issue_details(issue_id="4740575428")

print(f"Error: {issue['metadata']['type']}")
print(f"Location: {issue['culprit']}")
print(f"Occurrences: {issue['count']}")
```

**Raises**:
- `ValueError`: If issue_id is empty
- `NotFoundError`: If issue doesn't exist
- `APIError`: If Sentry API request fails

---

### get_latest_event()

Get the most recent event (with stack trace) for an issue.

```python
async def get_latest_event(
    issue_id: str
) -> Dict[str, Any]
```

**Parameters**:
- `issue_id` (str, required): Issue ID

**Returns**: Latest event with stack trace.

**Return Type**:
```python
{
    "event_id": str,
    "message": str,
    "platform": str,         # python, javascript, etc.
    "timestamp": str,        # ISO timestamp
    "stack_trace": [
        {
            "filename": str,
            "function": str,
            "lineno": int,
            "context_line": str,
            "pre_context": List[str],
            "post_context": List[str]
        },
        ...
    ],
    "exception": {
        "type": str,
        "value": str,
        "module": str
    },
    "user": dict,
    "tags": dict,
    "context": dict
}
```

**Token Usage**: ~195 tokens per call

**Example**:
```python
event = await sentry.get_latest_event(issue_id="4740575428")

# Print stack trace
for frame in event["stack_trace"]:
    print(f"{frame['filename']}:{frame['lineno']} in {frame['function']}")
    print(f"  {frame['context_line']}")
```

**Raises**:
- `ValueError`: If issue_id is empty
- `NotFoundError`: If issue has no events
- `APIError`: If Sentry API request fails

---

### analyze_error()

Comprehensive error analysis combining issue details and latest event.

```python
async def analyze_error(
    issue_id: str
) -> Dict[str, Any]
```

**Parameters**:
- `issue_id` (str, required): Issue ID

**Returns**: Complete error analysis.

**Return Type**:
```python
{
    "issue": {
        # Issue details (see get_issue_details)
    },
    "event": {
        # Latest event (see get_latest_event)
    },
    "analysis": {
        "primary_file": str,      # Main file causing error
        "error_type": str,        # Type of error
        "suggested_fix": str,     # AI-generated fix suggestion
        "root_cause": str,        # Likely root cause
        "impact": str            # User impact assessment
    }
}
```

**Token Usage**: ~380 tokens per call

**Example**:
```python
analysis = await sentry.analyze_error(issue_id="4740575428")

print(f"Error Type: {analysis['analysis']['error_type']}")
print(f"Primary File: {analysis['analysis']['primary_file']}")
print(f"Suggested Fix: {analysis['analysis']['suggested_fix']}")

# Access full details
issue = analysis['issue']
event = analysis['event']
```

**Raises**:
- `ValueError`: If issue_id is empty
- `NotFoundError`: If issue doesn't exist
- `APIError`: If Sentry API request fails

---

### update_issue()

Update issue properties.

```python
async def update_issue(
    issue_id: str,
    status: Optional[str] = None,
    assignee: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    is_bookmarked: Optional[bool] = None
) -> Dict[str, Any]
```

**Parameters**:
- `issue_id` (str, required): Issue ID
- `status` (str, optional): New status ("resolved", "unresolved", "ignored")
- `assignee` (str, optional): User email or username to assign
- `tags` (dict, optional): Tags to add/update (e.g., {"priority": "high"})
- `is_bookmarked` (bool, optional): Bookmark status

**Returns**: Updated issue details.

**Token Usage**: ~195 tokens per call

**Example**:
```python
# Resolve issue
await sentry.update_issue(
    issue_id="4740575428",
    status="resolved"
)

# Assign and tag issue
await sentry.update_issue(
    issue_id="4740575428",
    assignee="developer@company.com",
    tags={"priority": "high", "component": "auth"}
)

# Bookmark issue
await sentry.update_issue(
    issue_id="4740575428",
    is_bookmarked=True
)
```

**Raises**:
- `ValueError`: If issue_id is empty or parameters are invalid
- `NotFoundError`: If issue doesn't exist
- `AuthorizationError`: If user lacks permissions
- `APIError`: If Sentry API request fails

---

### delete_issue()

Delete or permanently ignore an issue.

```python
async def delete_issue(
    issue_id: str,
    permanent: bool = False
) -> bool
```

**Parameters**:
- `issue_id` (str, required): Issue ID
- `permanent` (bool, default=False): If True, permanently delete. If False, ignore.

**Returns**: True if successful.

**Token Usage**: ~180 tokens per call

**Example**:
```python
# Ignore issue
await sentry.delete_issue(issue_id="4740575428", permanent=False)

# Permanently delete issue
await sentry.delete_issue(issue_id="4740575428", permanent=True)
```

**Raises**:
- `ValueError`: If issue_id is empty
- `NotFoundError`: If issue doesn't exist
- `AuthorizationError`: If user lacks permissions
- `APIError`: If Sentry API request fails

---

## Event Operations

### query_events()

Search and filter events across a project.

```python
async def query_events(
    project: str,
    query: Optional[str] = None,
    period: str = "24h",
    limit: int = 10,
    sort: str = "-timestamp"
) -> List[Dict[str, Any]]
```

**Parameters**:
- `project` (str, required): Project slug
- `query` (str, optional): Search query (e.g., "error.type:TypeError user.email:*@example.com")
- `period` (str, default="24h"): Time period ("1h", "24h", "7d", "14d", "30d")
- `limit` (int, default=10): Maximum events to return (1-100)
- `sort` (str, default="-timestamp"): Sort field (prefix with "-" for descending)

**Returns**: List of events.

**Return Type**:
```python
[
    {
        "event_id": str,
        "timestamp": str,
        "message": str,
        "level": str,
        "platform": str,
        "user": dict,
        "tags": dict
    },
    ...
]
```

**Token Usage**: ~200 tokens per call (10 events)

**Example**:
```python
# Query TypeError events
events = await sentry.query_events(
    project="PYTHON-1",
    query="error.type:TypeError",
    period="7d",
    limit=50
)

# Query events for specific user
events = await sentry.query_events(
    project="PYTHON-1",
    query="user.email:user@example.com",
    period="24h"
)

# Query all error-level events
events = await sentry.query_events(
    project="PYTHON-1",
    query="level:error",
    sort="-timestamp",
    limit=100
)
```

---

## Project Operations

### list_projects()

List all accessible projects in the organization.

```python
async def list_projects() -> List[Dict[str, Any]]
```

**Returns**: List of projects.

**Return Type**:
```python
[
    {
        "id": str,
        "slug": str,           # Project slug (e.g., "PYTHON-1")
        "name": str,           # Display name
        "platform": str,       # python, javascript, etc.
        "status": str,         # active, disabled
        "date_created": str    # ISO timestamp
    },
    ...
]
```

**Token Usage**: ~180 tokens per call

**Example**:
```python
projects = await sentry.list_projects()

for project in projects:
    print(f"{project['name']} ({project['slug']})")
```

---

### get_project()

Get detailed information about a specific project.

```python
async def get_project(
    project: str
) -> Dict[str, Any]
```

**Parameters**:
- `project` (str, required): Project slug

**Returns**: Project details.

**Return Type**:
```python
{
    "id": str,
    "slug": str,
    "name": str,
    "platform": str,
    "status": str,
    "date_created": str,
    "features": List[str],
    "teams": List[dict],
    "options": dict
}
```

**Token Usage**: ~190 tokens per call

**Example**:
```python
project = await sentry.get_project("PYTHON-1")
print(f"Platform: {project['platform']}")
print(f"Features: {', '.join(project['features'])}")
```

---

## Configuration

### SentryConfig

Configuration model for Sentry MCP Optimized.

```python
from sentry_mcp import SentryConfig, SandboxMode
from pydantic import SecretStr

config = SentryConfig(
    # Authentication (required)
    auth_token: SecretStr,           # Sentry auth token
    organization: str,                # Organization slug

    # API Configuration
    base_url: str = "https://sentry.io",
    request_timeout: int = 30,        # Request timeout in seconds
    max_retries: int = 3,             # Max retry attempts

    # Performance
    enable_caching: bool = False,     # Enable result caching
    cache_ttl: int = 300,            # Cache TTL in seconds

    # Security
    sandbox_mode: SandboxMode = "hybrid",  # strict, hybrid, permissive
    enable_audit_log: bool = True,    # Enable audit logging

    # Observability
    enable_metrics: bool = True,      # Enable metrics collection
    metrics_backend: str = "prometheus"  # Metrics backend
)
```

**Environment Variables**:
```bash
SENTRY_AUTH_TOKEN=sntrys_abc123...
SENTRY_ORG_SLUG=my-company
SENTRY_BASE_URL=https://sentry.io
MCP_SANDBOX_MODE=hybrid
MCP_ENABLE_METRICS=true
```

---

## Error Handling

### Exception Hierarchy

```python
SentryMCPError                    # Base exception
├── AuthenticationError           # Invalid credentials
├── AuthorizationError            # Insufficient permissions
├── RateLimitError               # API rate limit exceeded
├── ValidationError              # Invalid input
├── APIError                     # Sentry API error
│   ├── NotFoundError           # Resource not found (404)
│   ├── BadRequestError         # Invalid request (400)
│   └── ServerError             # Sentry server error (500)
└── NetworkError                 # Connection issues
```

### Example Error Handling

```python
from sentry_mcp import (
    SentryMCPOptimized,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    APIError
)

async def safe_get_issue(issue_id: str):
    try:
        return await sentry.get_issue_details(issue_id)
    except AuthenticationError:
        print("Invalid auth token")
    except NotFoundError:
        print(f"Issue {issue_id} not found")
    except RateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after} seconds")
    except APIError as e:
        print(f"API error: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

---

## Type Definitions

### Issue

```python
from typing import TypedDict

class Issue(TypedDict):
    id: str
    title: str
    level: str
    count: int
    first_seen: str
    last_seen: str
    status: str
    assignee: Optional[str]
    tags: List[dict]
```

### Event

```python
class Event(TypedDict):
    event_id: str
    timestamp: str
    message: str
    level: str
    platform: str
    stack_trace: List[StackFrame]
    exception: dict
    user: dict
    tags: dict
```

### StackFrame

```python
class StackFrame(TypedDict):
    filename: str
    function: str
    lineno: int
    context_line: str
    pre_context: List[str]
    post_context: List[str]
```

---

## Performance Metrics

### Token Usage by Operation

| Operation | Tokens | Reduction |
|-----------|--------|-----------|
| list_issues (10 items) | 207 | 99.6% |
| get_issue_details | 185 | 99.6% |
| get_latest_event | 195 | 99.6% |
| analyze_error | 380 | 99.2% |
| update_issue | 195 | 99.6% |
| query_events (10 items) | 200 | 99.7% |
| list_projects | 180 | 99.6% |

### Latency by Operation

| Operation | Latency | Baseline |
|-----------|---------|----------|
| list_issues | 45ms | 2000ms |
| get_issue_details | 40ms | 1800ms |
| analyze_error | 85ms | 3500ms |

---

## Complete Example

```python
import asyncio
from sentry_mcp import SentryMCPOptimized

async def main():
    # Initialize
    sentry = SentryMCPOptimized(
        auth_token="sntrys_abc123...",
        organization="my-company"
    )

    # List projects
    projects = await sentry.list_projects()
    print(f"Found {len(projects)} projects")

    # Get issues for first project
    project_slug = projects[0]["slug"]
    issues = await sentry.list_issues(
        project=project_slug,
        limit=5,
        status="unresolved"
    )

    # Analyze first issue
    if issues:
        issue_id = issues[0]["id"]
        analysis = await sentry.analyze_error(issue_id)

        print(f"Issue: {analysis['issue']['title']}")
        print(f"Error Type: {analysis['analysis']['error_type']}")
        print(f"Suggested Fix: {analysis['analysis']['suggested_fix']}")

        # Resolve if fix is simple
        if "check for None" in analysis['analysis']['suggested_fix'].lower():
            await sentry.update_issue(
                issue_id=issue_id,
                status="resolved",
                tags={"auto_resolved": "true"}
            )

if __name__ == "__main__":
    asyncio.run(main())
```

---

**Last Updated**: 2024-11-24
**Version**: 0.1.0

For more information, see:
- [Architecture Documentation](ARCHITECTURE.md)
- [Sentry Operations Guide](SENTRY_OPERATIONS.md)
- [GitHub Repository](https://github.com/rhart696/sentry-mcp-optimized)
