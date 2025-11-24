# Architecture Documentation

## Overview

Sentry MCP Optimized is built on the MCP Optimizer Framework to provide a high-performance, token-efficient integration with the Sentry error tracking platform. This document describes the system architecture, design decisions, and integration patterns.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                        │
│  (Claude Desktop, Roo Code, Cline, Custom Python Scripts)    │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│              Sentry MCP Optimized (This Project)             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            SentryAdaptor (sentry.py)                 │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  • list_issues()                                     │    │
│  │  • get_issue_details()                               │    │
│  │  • get_latest_event()                                │    │
│  │  • analyze_error()                                   │    │
│  │  • list_projects()                                   │    │
│  │  • query_events()                                    │    │
│  │  • update_issue()                                    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Configuration (config.py)                  │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  • SentryConfig (Pydantic model)                     │    │
│  │  • Environment validation                            │    │
│  │  • Token management                                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│           MCP Optimizer Framework (Dependency)               │
├─────────────────────────────────────────────────────────────┤
│  • Sandbox Execution (Docker, gVisor, WASM)                  │
│  • Token Metrics & Monitoring                                │
│  • Audit Logging                                             │
│  • Resource Management                                       │
│  • Security Controls                                         │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                 External Services                            │
├─────────────────────────────────────────────────────────────┤
│  • Sentry API (sentry.io)                                    │
│  • Redis (optional, for caching)                             │
│  • Metrics Backend (Prometheus, etc.)                        │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. SentryAdaptor Layer

**Purpose**: Direct API wrapper that replaces traditional MCP tool loading.

**Design Philosophy**:
- **Direct execution** instead of tool discovery
- **Minimal data transfer** - return only essential fields
- **Async-first** - all operations are async
- **Structured output** - typed responses using Pydantic

**Key Methods**:

```python
class SentryAdaptor:
    """Core adaptor for Sentry API operations"""

    # Issue Management
    async def list_issues(project, limit, status) -> List[Issue]
    async def get_issue_details(issue_id) -> IssueDetails
    async def update_issue(issue_id, **updates) -> Issue
    async def delete_issue(issue_id) -> bool

    # Event Querying
    async def get_latest_event(issue_id) -> Event
    async def query_events(project, filters) -> List[Event]

    # Analysis
    async def analyze_error(issue_id) -> Analysis

    # Project Operations
    async def list_projects() -> List[Project]
    async def get_project(project_slug) -> ProjectDetails
```

**Token Optimization**:
- Traditional MCP: Returns full tool schemas (~150K tokens)
- Optimized: Direct function calls (~500 tokens)
- Savings: 99.7% token reduction

### 2. Configuration Management

**SentryConfig** (Pydantic model):

```python
class SentryConfig(BaseModel):
    # Authentication
    auth_token: SecretStr
    organization: str
    base_url: str = "https://sentry.io"

    # Performance
    request_timeout: int = 30
    max_retries: int = 3
    cache_ttl: int = 300

    # Security (inherited from framework)
    sandbox_mode: SandboxMode = "hybrid"
    enable_audit_log: bool = True

    # Features
    enable_metrics: bool = True
    enable_caching: bool = False
```

**Configuration Sources** (priority order):
1. Direct instantiation
2. Environment variables
3. Configuration file (~/.sentry-mcp/config.yaml)
4. Defaults

### 3. Integration with MCP Optimizer Framework

**Framework Responsibilities**:
- Sandbox execution environments
- Resource limits enforcement
- Token counting and metrics
- Audit trail generation
- Security policy enforcement

**Integration Points**:

```python
from mcp_optimizer_framework import MCPOptimizer, ExecutionContext

class SentryMCPOptimized(MCPOptimizer):
    """Inherits framework capabilities"""

    def __init__(self, config: SentryConfig):
        super().__init__(
            adaptor=SentryAdaptor(config),
            sandbox_mode=config.sandbox_mode,
            enable_metrics=config.enable_metrics
        )
```

### 4. Execution Flow

**Traditional MCP Approach**:
```
1. Client requests operation
2. MCP server loads all tool schemas (~150K tokens)
3. LLM selects appropriate tool
4. Tool execution via JSON-RPC
5. Response serialization
Total: 150,000+ tokens, 2-3 seconds
```

**Optimized Approach**:
```
1. Client calls method directly
2. SentryAdaptor executes API call
3. Framework handles security/metrics
4. Structured response returned
Total: ~500 tokens, 50ms
```

**Sequence Diagram**:
```
Client          SentryMCPOptimized    SentryAdaptor    Sentry API
  |                    |                    |               |
  |-- list_issues() -->|                    |               |
  |                    |-- validate() ----->|               |
  |                    |                    |-- GET /api -->|
  |                    |                    |<-- 200 OK ----|
  |                    |<-- parse() --------|               |
  |                    |-- metrics() ------>|               |
  |<-- List[Issue] ----|                    |               |
```

## Data Flow

### Issue Listing Flow

```python
# 1. Client Request
issues = await sentry.list_issues(
    project="PYTHON-1",
    status="unresolved",
    limit=10
)

# 2. SentryAdaptor Processing
async def list_issues(self, project, status, limit):
    url = f"{self.base_url}/projects/{self.org}/{project}/issues/"
    params = {"limit": limit, "query": f"is:{status}"}

    # 3. API Request
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=self.headers, params=params) as resp:
            raw_issues = await resp.json()

    # 4. Data Minimization (Token Optimization)
    return [
        {
            "id": issue["id"],
            "title": issue["title"],
            "level": issue.get("level", "error"),
            "count": issue.get("count", 0),
            # Only essential fields returned
        }
        for issue in raw_issues
    ]
```

**Token Comparison**:
- Full issue object: ~2,000 tokens per issue
- Minimized object: ~20 tokens per issue
- 10 issues: 20,000 vs 200 tokens (99% reduction)

### Error Analysis Flow

**Composite Operation** (replaces multiple MCP calls):

```python
async def analyze_error(self, issue_id: str) -> Dict:
    # Parallel execution for efficiency
    issue_task = self.get_issue_details(issue_id)
    event_task = self.get_latest_event(issue_id)

    issue, event = await asyncio.gather(issue_task, event_task)

    return {
        "issue": issue,
        "event": event,
        "analysis": {
            "primary_file": self._extract_primary_file(event),
            "error_type": issue["metadata"].get("type"),
            "suggested_fix": self._suggest_fix(issue, event)
        }
    }
```

**Advantages**:
- Single client call instead of 3+ MCP tool invocations
- Parallel API requests reduce latency
- Integrated analysis reduces round trips
- Total tokens: ~500 vs ~45,000 (traditional)

## Security Architecture

### Multi-Layer Security

**Layer 1: Framework Sandboxing**
```
┌──────────────────────────────────┐
│    Docker Container              │
│  ┌────────────────────────────┐  │
│  │   gVisor Kernel            │  │
│  │  ┌──────────────────────┐  │  │
│  │  │  SentryAdaptor       │  │  │
│  │  │  (Isolated Process)  │  │  │
│  │  └──────────────────────┘  │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

**Layer 2: Network Isolation**
- Whitelisted endpoints only (sentry.io)
- HTTPS enforcement
- Certificate validation
- Rate limiting

**Layer 3: Credential Management**
- Tokens stored in environment variables
- Secrets never logged
- Token rotation support
- Scoped permissions

**Layer 4: Audit Trail**
```python
{
    "timestamp": "2024-11-24T10:30:00Z",
    "operation": "list_issues",
    "user": "user@example.com",
    "project": "PYTHON-1",
    "result": "success",
    "tokens_used": 207,
    "latency_ms": 45
}
```

## Performance Architecture

### Token Optimization Strategies

**1. Data Minimization**
```python
# Bad: Return everything (high tokens)
return raw_api_response

# Good: Return only necessary fields (low tokens)
return {
    "id": response["id"],
    "title": response["title"],
    "count": response["count"]
}
```

**2. Batching**
```python
# Process multiple operations in parallel
results = await asyncio.gather(
    sentry.get_issue(id1),
    sentry.get_issue(id2),
    sentry.get_issue(id3)
)
```

**3. Caching** (v0.2.0+)
```python
@cache(ttl=300)
async def list_projects():
    # Expensive API call cached for 5 minutes
    pass
```

### Latency Optimization

**Connection Pooling**:
```python
# Reuse HTTP connections
session = aiohttp.ClientSession(
    connector=aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
)
```

**Request Compression**:
```python
headers = {
    "Accept-Encoding": "gzip, deflate",
    "Accept": "application/json"
}
```

**Parallel Execution**:
```python
# Execute independent operations concurrently
async def get_dashboard_data(project):
    issues, events, stats = await asyncio.gather(
        sentry.list_issues(project),
        sentry.query_events(project, period="24h"),
        sentry.get_project_stats(project)
    )
```

## Scalability Considerations

### Horizontal Scaling

**Stateless Design**:
- No server-side state
- Session-less API calls
- Load balancer compatible

**Deployment Options**:
```yaml
# Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentry-mcp-optimized
spec:
  replicas: 3  # Scale horizontally
  selector:
    matchLabels:
      app: sentry-mcp
  template:
    spec:
      containers:
      - name: sentry-mcp
        image: sentry-mcp-optimized:0.1.0
        env:
        - name: SENTRY_AUTH_TOKEN
          valueFrom:
            secretKeyRef:
              name: sentry-credentials
              key: auth-token
```

### Rate Limiting

**Sentry API Limits**:
- Default: 10,000 requests/hour
- Configurable retry logic with exponential backoff

```python
class RateLimitHandler:
    async def execute_with_retry(self, func, *args):
        for attempt in range(self.max_retries):
            try:
                return await func(*args)
            except RateLimitError as e:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
        raise MaxRetriesExceeded()
```

### Caching Strategy (v0.2.0+)

**Cache Layers**:
```
┌──────────────────────┐
│   In-Memory Cache    │  ← Fastest (LRU, 100 entries)
├──────────────────────┤
│   Redis Cache        │  ← Shared (TTL 5 minutes)
├──────────────────────┤
│   Sentry API         │  ← Source of truth
└──────────────────────┘
```

**Cache Invalidation**:
- TTL-based expiration
- Explicit invalidation on updates
- Cache warming for common queries

## Monitoring & Observability

### Metrics Collection

**Prometheus Metrics**:
```python
# Operation counters
sentry_mcp_operations_total{operation="list_issues", status="success"} 1234

# Latency histograms
sentry_mcp_operation_duration_seconds{operation="list_issues"} 0.05

# Token usage
sentry_mcp_tokens_used_total{operation="list_issues"} 207000
```

### Structured Logging

```python
logger = structlog.get_logger()

logger.info(
    "sentry_operation_completed",
    operation="list_issues",
    project="PYTHON-1",
    issue_count=10,
    latency_ms=45,
    tokens_used=207
)
```

### Tracing (v1.0.0+)

**OpenTelemetry Integration**:
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("list_issues")
async def list_issues(project):
    span = trace.get_current_span()
    span.set_attribute("project", project)
    # Operation implementation
```

## Error Handling

### Error Hierarchy

```python
SentryMCPError (base)
├── AuthenticationError      # Invalid token
├── AuthorizationError       # Insufficient permissions
├── RateLimitError          # API rate limit exceeded
├── ValidationError         # Invalid input
├── APIError                # Sentry API error
│   ├── NotFoundError       # Resource not found
│   ├── BadRequestError     # Invalid request
│   └── ServerError         # Sentry server error
└── NetworkError            # Connection issues
```

### Error Recovery

```python
async def list_issues_with_retry(self, project, limit):
    try:
        return await self.list_issues(project, limit)
    except RateLimitError:
        await asyncio.sleep(60)  # Wait for rate limit reset
        return await self.list_issues(project, limit)
    except NetworkError:
        # Use cached data if available
        return await self.get_cached_issues(project)
    except APIError as e:
        logger.error("api_error", error=str(e), project=project)
        raise
```

## Testing Architecture

### Test Pyramid

```
        ┌─────────────┐
        │   E2E Tests │        (5% - Full integration)
        └─────────────┘
      ┌─────────────────┐
      │ Integration Tests│      (15% - API mocking)
      └─────────────────┘
    ┌───────────────────────┐
    │     Unit Tests        │  (80% - Component isolation)
    └───────────────────────┘
```

### Test Categories

**Unit Tests**:
```python
@pytest.mark.asyncio
async def test_minimize_issue_data():
    """Test data minimization reduces tokens"""
    full_issue = load_fixture("full_issue.json")
    minimized = adaptor._minimize_issue_data(full_issue)

    full_tokens = count_tokens(json.dumps(full_issue))
    minimized_tokens = count_tokens(json.dumps(minimized))

    assert minimized_tokens < full_tokens * 0.05  # 95% reduction
```

**Integration Tests**:
```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_issues_integration(mock_sentry_api):
    """Test list_issues with mocked API"""
    mock_sentry_api.get.return_value = mock_response([...])

    issues = await adaptor.list_issues("PYTHON-1", limit=5)

    assert len(issues) == 5
    mock_sentry_api.get.assert_called_once()
```

**E2E Tests**:
```python
@pytest.mark.e2e
@pytest.mark.skipif(not SENTRY_TOKEN, reason="Requires Sentry credentials")
async def test_full_workflow():
    """Test complete error analysis workflow"""
    sentry = SentryMCPOptimized(auth_token=SENTRY_TOKEN)

    # Real API calls
    issues = await sentry.list_issues("PYTHON-1", limit=1)
    analysis = await sentry.analyze_error(issues[0]["id"])

    assert "suggested_fix" in analysis["analysis"]
```

## Deployment Architecture

### Local Development

```bash
# Virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Environment configuration
export SENTRY_AUTH_TOKEN="..."
export SENTRY_ORG_SLUG="..."

# Run tests
pytest tests/
```

### Production Deployment (v1.0.0)

**Docker Container**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e .

# Security: Non-root user
RUN useradd -m -u 1000 sentry-mcp
USER sentry-mcp

CMD ["python", "-m", "sentry_mcp.server"]
```

**Kubernetes**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: sentry-mcp
spec:
  selector:
    app: sentry-mcp
  ports:
  - port: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentry-mcp
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: sentry-mcp
        image: sentry-mcp-optimized:0.1.0
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## Dependencies

### Core Dependencies

```
mcp-optimizer-framework >= 1.0.0  # Foundation
aiohttp >= 3.8.0                  # Async HTTP
pydantic >= 2.0.0                 # Data validation
structlog >= 23.0.0               # Structured logging
python-dotenv >= 1.0.0            # Environment config
```

### Optional Dependencies

```
redis >= 4.5.0                    # Caching (v0.2.0+)
prometheus-client >= 0.17.0       # Metrics export
opentelemetry-api >= 1.20.0       # Tracing (v1.0.0+)
```

## Design Patterns

### Adapter Pattern
```python
# Adapts Sentry API to optimized interface
class SentryAdaptor:
    """Adapter for Sentry API"""
    def __init__(self, config):
        self._client = SentryAPIClient(config)

    async def list_issues(self, ...):
        raw_data = await self._client.get("/issues")
        return self._minimize_data(raw_data)
```

### Factory Pattern
```python
def create_sentry_mcp(profile: str = "default") -> SentryMCPOptimized:
    """Factory for creating configured instances"""
    config = load_config(profile)
    return SentryMCPOptimized(config)
```

### Strategy Pattern
```python
class CachingStrategy(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]: pass

class RedisCache(CachingStrategy):
    async def get(self, key: str): ...

class InMemoryCache(CachingStrategy):
    async def get(self, key: str): ...
```

## Future Architecture (v2.0.0+)

### Plugin System
```python
class SentryMCPPlugin(ABC):
    @abstractmethod
    async def on_issue_created(self, issue): pass

class SlackNotifier(SentryMCPPlugin):
    async def on_issue_created(self, issue):
        await slack.send(f"New issue: {issue['title']}")
```

### GraphQL Support
```graphql
query GetIssues($project: String!, $limit: Int!) {
  issues(project: $project, limit: $limit) {
    id
    title
    count
    events {
      id
      message
    }
  }
}
```

### WebSocket Real-Time
```python
async with sentry.subscribe("issues", project="PYTHON-1") as stream:
    async for issue in stream:
        print(f"New issue: {issue}")
```

## References

- [MCP Optimizer Framework Architecture](https://github.com/rhart696/mcp-optimizer-framework/blob/main/docs/ARCHITECTURE.md)
- [Sentry API Documentation](https://docs.sentry.io/api/)
- [ADR Index](adr/README.md)

---

**Last Updated**: 2024-11-24
**Version**: 0.1.0
