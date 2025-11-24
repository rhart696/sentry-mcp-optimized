# Troubleshooting Guide

Common issues and solutions for Sentry MCP Optimized.

## Table of Contents

- [Authentication Issues](#authentication-issues)
- [Connection Problems](#connection-problems)
- [Performance Issues](#performance-issues)
- [API Errors](#api-errors)
- [Configuration Problems](#configuration-problems)
- [Installation Issues](#installation-issues)
- [Framework Integration](#framework-integration)
- [Getting Help](#getting-help)

## Authentication Issues

### Issue: "AuthenticationError: Invalid token"

**Symptoms**:
```python
sentry_mcp.errors.AuthenticationError: Invalid or expired authentication token
```

**Common Causes**:
1. Token is incorrect or missing
2. Token has been revoked
3. Environment variable not set
4. Wrong token format

**Solutions**:

**1. Verify environment variable**:
```bash
echo $SENTRY_AUTH_TOKEN
# Should output: sntrys_abc123...
```

**2. Test token directly**:
```bash
curl -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  https://sentry.io/api/0/organizations/
```

Expected: JSON array of organizations

**3. Re-create token**:
1. Go to sentry.io → User Settings → Auth Tokens
2. Create new token with required scopes
3. Update environment variable:
```bash
export SENTRY_AUTH_TOKEN="sntrys_NEW_TOKEN_HERE"
```

**4. Check token format**:
- Should start with `sntrys_`
- Length: ~70 characters
- No spaces or newlines

**5. Verify in code**:
```python
import os

token = os.getenv("SENTRY_AUTH_TOKEN")
if not token:
    print("❌ Token not set")
elif not token.startswith("sntrys_"):
    print(f"❌ Invalid token format: {token[:10]}...")
else:
    print(f"✓ Token looks valid: sntrys_...{token[-4:]}")
```

---

### Issue: "AuthorizationError: Insufficient permissions"

**Symptoms**:
```python
sentry_mcp.errors.AuthorizationError: Token lacks required permissions
```

**Common Causes**:
1. Token missing required scopes
2. User lacks organization/project access
3. Project doesn't exist

**Solutions**:

**1. Check token scopes**:
Go to sentry.io → User Settings → Auth Tokens → Your Token

Required minimum scopes:
- `org:read`
- `project:read`
- `event:read`
- `issue:read`
- `issue:write` (for updates)

**2. Test permissions**:
```python
from sentry_mcp import SentryMCPOptimized

sentry = SentryMCPOptimized()

try:
    # Test read access
    projects = await sentry.list_projects()
    print(f"✓ Read access: {len(projects)} projects")
except Exception as e:
    print(f"✗ Read access failed: {e}")

try:
    # Test write access
    issues = await sentry.list_issues("PYTHON-1", limit=1)
    if issues:
        await sentry.update_issue(issues[0]["id"], is_bookmarked=True)
        print("✓ Write access works")
except Exception as e:
    print(f"✗ Write access failed: {e}")
```

**3. Create new token with full permissions**:
```
Required Scopes:
☑ org:read
☑ org:write
☑ project:read
☑ project:write
☑ event:read
☑ issue:read
☑ issue:write
☑ team:read
☑ member:read
```

---

## Connection Problems

### Issue: "NetworkError: Connection timeout"

**Symptoms**:
```python
sentry_mcp.errors.NetworkError: Connection to Sentry API timed out
```

**Common Causes**:
1. Network connectivity issues
2. Firewall blocking requests
3. Sentry API downtime
4. Timeout too short

**Solutions**:

**1. Check network connectivity**:
```bash
# Test basic connectivity
ping sentry.io

# Test HTTPS access
curl -I https://sentry.io/api/0/
```

**2. Check firewall rules**:
```bash
# Ensure port 443 (HTTPS) is open
telnet sentry.io 443
```

**3. Check Sentry status**:
Visit: https://status.sentry.io/

**4. Increase timeout**:
```python
from sentry_mcp import SentryConfig

config = SentryConfig(
    auth_token="your_token",
    organization="your_org",
    request_timeout=60  # Increase from 30 to 60 seconds
)

sentry = SentryMCPOptimized(config=config)
```

**5. Use proxy if needed**:
```python
import os
os.environ["HTTPS_PROXY"] = "http://proxy.company.com:8080"
```

---

### Issue: "NetworkError: SSL verification failed"

**Symptoms**:
```python
aiohttp.client_exceptions.ClientConnectorCertificateError: Certificate verify failed
```

**Common Causes**:
1. Corporate SSL interception
2. Self-signed certificates
3. Outdated CA certificates

**Solutions**:

**1. Update CA certificates**:
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install ca-certificates

# macOS
brew install ca-certificates

# Python certifi
pip install --upgrade certifi
```

**2. For self-hosted Sentry with self-signed cert** (development only):
```python
import ssl
import aiohttp

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Note: This disables SSL verification - NOT recommended for production
```

**3. Add corporate CA certificate**:
```bash
export REQUESTS_CA_BUNDLE=/path/to/corporate-ca-bundle.crt
```

---

## Performance Issues

### Issue: Operations are slow (>500ms)

**Symptoms**:
- Responses taking longer than expected
- Timeouts in high-load scenarios

**Common Causes**:
1. Network latency
2. Large result sets
3. Sentry API rate limiting
4. Missing optimization flags

**Solutions**:

**1. Reduce result set size**:
```python
# Bad: Requesting too many items
issues = await sentry.list_issues("PYTHON-1", limit=1000)  # Slow

# Good: Request only what you need
issues = await sentry.list_issues("PYTHON-1", limit=10)  # Fast
```

**2. Enable caching** (v0.2.0+):
```python
config = SentryConfig(
    auth_token="your_token",
    organization="your_org",
    enable_caching=True,
    cache_ttl=300  # 5 minutes
)
```

**3. Use batch operations**:
```python
import asyncio

# Bad: Sequential operations
for issue_id in issue_ids:
    issue = await sentry.get_issue_details(issue_id)  # Slow

# Good: Parallel operations
tasks = [sentry.get_issue_details(id) for id in issue_ids]
issues = await asyncio.gather(*tasks)  # Fast
```

**4. Profile your code**:
```python
import time

start = time.time()
result = await sentry.list_issues("PYTHON-1", limit=10)
elapsed = time.time() - start

print(f"Operation took {elapsed*1000:.1f}ms")

if elapsed > 0.5:
    print("⚠️  Operation slower than expected")
    print("Check network, Sentry API status, and query complexity")
```

---

### Issue: High token usage

**Symptoms**:
- Tokens higher than expected (~500 per operation)
- Unexpectedly high LLM costs

**Common Causes**:
1. Not using optimized methods
2. Returning too much data
3. Inefficient workflow

**Solutions**:

**1. Verify you're using Sentry MCP Optimized**:
```python
from sentry_mcp import SentryMCPOptimized

# Verify instance type
print(type(sentry))
# Should output: <class 'sentry_mcp.SentryMCPOptimized'>
```

**2. Use composite operations**:
```python
# Bad: Multiple separate calls (more tokens)
issue = await sentry.get_issue_details(issue_id)
event = await sentry.get_latest_event(issue_id)

# Good: Single composite call (fewer tokens)
analysis = await sentry.analyze_error(issue_id)
```

**3. Monitor token usage**:
```python
config = SentryConfig(
    auth_token="your_token",
    organization="your_org",
    enable_metrics=True
)

sentry = SentryMCPOptimized(config=config)

# Check metrics after operations
# See logs for token counts
```

---

## API Errors

### Issue: "NotFoundError: Project not found"

**Symptoms**:
```python
sentry_mcp.errors.NotFoundError: Project 'PYTHON-1' not found
```

**Solutions**:

**1. Verify project exists**:
```python
projects = await sentry.list_projects()
project_slugs = [p["slug"] for p in projects]
print(f"Available projects: {project_slugs}")
```

**2. Check project slug format**:
```bash
# Correct format examples:
PYTHON-1
javascript-2
my-app

# Incorrect (will fail):
python-1  # lowercase (depends on Sentry setup)
PYTHON_1  # underscore instead of dash
```

**3. Verify organization**:
```python
# Ensure organization is set correctly
config = SentryConfig(
    auth_token="your_token",
    organization="correct-org-slug"  # Not the display name!
)
```

---

### Issue: "RateLimitError: Rate limit exceeded"

**Symptoms**:
```python
sentry_mcp.errors.RateLimitError: Sentry API rate limit exceeded. Retry after 60 seconds.
```

**Common Causes**:
1. Too many requests in short time
2. Shared token across services
3. Burst traffic

**Solutions**:

**1. Implement retry logic**:
```python
from sentry_mcp import RateLimitError
import asyncio

async def with_retry(func, *args, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await func(*args)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            print(f"Rate limited. Waiting {e.retry_after}s...")
            await asyncio.sleep(e.retry_after)

# Usage
issues = await with_retry(sentry.list_issues, "PYTHON-1")
```

**2. Use exponential backoff**:
```python
async def exponential_backoff_retry(func, *args, max_retries=5):
    for attempt in range(max_retries):
        try:
            return await func(*args)
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # 1, 2, 4, 8, 16 seconds
            print(f"Retry {attempt+1}/{max_retries} after {wait_time}s")
            await asyncio.sleep(wait_time)
```

**3. Enable caching**:
```python
config = SentryConfig(
    enable_caching=True,
    cache_ttl=300
)
# Reduces API calls significantly
```

**4. Use separate tokens per service**:
- Create dedicated token for each application
- Avoids shared rate limit pool

---

### Issue: "BadRequestError: Invalid parameters"

**Symptoms**:
```python
sentry_mcp.errors.BadRequestError: Invalid query syntax
```

**Solutions**:

**1. Validate query syntax**:
```python
# Bad: Invalid syntax
query = "error.type=TypeError"  # Wrong operator

# Good: Correct syntax
query = "error.type:TypeError"  # Use colon

# Bad: Unescaped special characters
query = 'filename:"app/views.py"'  # Missing escapes

# Good: Properly quoted
query = 'error.filename:"app/views.py"'
```

**2. Check parameter types**:
```python
# Bad: Wrong type
limit = "10"  # String

# Good: Correct type
limit = 10  # Integer
```

**3. Validate date formats**:
```python
# Bad: Wrong format
period = "last 24 hours"

# Good: Correct format
period = "24h"  # Valid options: 1h, 24h, 7d, 14d, 30d
```

---

## Configuration Problems

### Issue: Environment variables not loading

**Symptoms**:
- `SENTRY_AUTH_TOKEN` not found
- Default values being used

**Solutions**:

**1. Check environment**:
```python
import os

print("SENTRY_AUTH_TOKEN:", os.getenv("SENTRY_AUTH_TOKEN", "NOT SET"))
print("SENTRY_ORG_SLUG:", os.getenv("SENTRY_ORG_SLUG", "NOT SET"))
```

**2. Load .env file explicitly**:
```python
from dotenv import load_dotenv
load_dotenv()  # Load from .env file

from sentry_mcp import SentryMCPOptimized
sentry = SentryMCPOptimized()
```

**3. Check .env file location**:
```bash
# .env should be in project root or explicitly specified
ls -la .env

# Or specify path
load_dotenv("/path/to/.env")
```

**4. Check .env file syntax**:
```bash
# Correct
SENTRY_AUTH_TOKEN=sntrys_abc123
SENTRY_ORG_SLUG=my-org

# Incorrect
SENTRY_AUTH_TOKEN = sntrys_abc123  # Extra spaces
SENTRY_AUTH_TOKEN="sntrys_abc123"  # Unnecessary quotes
```

---

## Installation Issues

### Issue: "ModuleNotFoundError: No module named 'sentry_mcp'"

**Solutions**:

**1. Install package**:
```bash
pip install sentry-mcp-optimized

# Or from source
git clone https://github.com/rhart696/sentry-mcp-optimized.git
cd sentry-mcp-optimized
pip install -e .
```

**2. Check Python environment**:
```bash
# Verify correct Python
which python
python --version  # Should be 3.8+

# Verify in correct virtualenv
which pip
```

**3. Reinstall if needed**:
```bash
pip uninstall sentry-mcp-optimized
pip install sentry-mcp-optimized
```

---

### Issue: "ImportError: MCP Optimizer Framework not found"

**Solutions**:

**1. Install framework**:
```bash
# Install from parent directory
pip install -e ../mcp-optimizer-framework

# Or specify full path
pip install -e /path/to/mcp-optimizer-framework
```

**2. Verify installation**:
```bash
pip list | grep mcp
# Should show:
# mcp-optimizer-framework  1.0.0
# sentry-mcp-optimized     0.1.0
```

---

## Framework Integration

### Issue: Sandbox errors

**Symptoms**:
```python
mcp_optimizer_framework.errors.SandboxError: Docker container failed to start
```

**Solutions**:

**1. Check Docker installation**:
```bash
docker --version
docker ps  # Should show running containers
```

**2. Use different sandbox mode**:
```python
config = SentryConfig(
    auth_token="your_token",
    organization="your_org",
    sandbox_mode="permissive"  # Less strict, no Docker required
)
```

**3. Disable sandboxing** (development only):
```python
config = SentryConfig(
    sandbox_mode="none"  # Not recommended for production
)
```

---

## Debugging Tips

### Enable Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Or use structlog
import structlog
structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG))
```

### Print Request/Response

```python
from sentry_mcp import SentryMCPOptimized

# Enable verbose mode
config = SentryConfig(
    auth_token="your_token",
    organization="your_org",
    verbose=True  # Log all requests/responses
)
```

### Check Version

```python
import sentry_mcp
print(f"Version: {sentry_mcp.__version__}")

import mcp_optimizer_framework
print(f"Framework: {mcp_optimizer_framework.__version__}")
```

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Search existing issues**: https://github.com/rhart696/sentry-mcp-optimized/issues
3. **Review documentation**:
   - [README](../README.md)
   - [API Reference](API.md)
   - [Architecture](ARCHITECTURE.md)

### How to Ask for Help

**GitHub Issues**: https://github.com/rhart696/sentry-mcp-optimized/issues/new

Include:
1. **Description**: What you're trying to do
2. **Error message**: Full stack trace
3. **Environment**:
```python
import platform
import sys
import sentry_mcp

print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"sentry-mcp: {sentry_mcp.__version__}")
```
4. **Minimal reproduction**: Smallest code that reproduces issue
5. **Expected vs actual behavior**

### Support Channels

- **Bug Reports**: [GitHub Issues](https://github.com/rhart696/sentry-mcp-optimized/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/rhart696/sentry-mcp-optimized/issues)
- **Questions**: [GitHub Discussions](https://github.com/rhart696/sentry-mcp-optimized/discussions)
- **Security**: rhart696@users.noreply.github.com (private)

---

**Last Updated**: 2024-11-24
**Version**: 0.1.0
