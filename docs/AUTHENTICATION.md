# Authentication Guide

Complete guide to authentication and token management for Sentry MCP Optimized.

## Table of Contents

- [Overview](#overview)
- [Creating Sentry Auth Tokens](#creating-sentry-auth-tokens)
- [Configuration Methods](#configuration-methods)
- [Token Permissions](#token-permissions)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

Sentry MCP Optimized requires a Sentry authentication token to access the Sentry API. This guide covers how to create, configure, and secure your authentication credentials.

## Creating Sentry Auth Tokens

### Step 1: Access Sentry Settings

1. Log in to [sentry.io](https://sentry.io)
2. Click your profile icon (bottom left)
3. Select **User Settings**
4. Navigate to **Auth Tokens** tab

### Step 2: Create New Token

1. Click **Create New Token**
2. Fill in token details:
   - **Name**: `sentry-mcp-optimized` (or your preferred name)
   - **Scopes**: Select required permissions (see [Token Permissions](#token-permissions))
3. Click **Create Token**
4. **Important**: Copy the token immediately (it won't be shown again)

### Step 3: Verify Token

Test your token using curl:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://sentry.io/api/0/organizations/
```

Expected response: JSON array of organizations you have access to.

## Configuration Methods

### Method 1: Environment Variables (Recommended)

Set environment variables in your shell:

```bash
export SENTRY_AUTH_TOKEN="sntrys_abc123..."
export SENTRY_ORG_SLUG="your-org-slug"
```

Make permanent by adding to `~/.bashrc` or `~/.zshrc`:

```bash
echo 'export SENTRY_AUTH_TOKEN="sntrys_abc123..."' >> ~/.bashrc
echo 'export SENTRY_ORG_SLUG="your-org-slug"' >> ~/.bashrc
source ~/.bashrc
```

**Advantage**: Secure, no credentials in code, works across all scripts.

---

### Method 2: .env File

Create a `.env` file in your project root:

```bash
# .env
SENTRY_AUTH_TOKEN=sntrys_abc123...
SENTRY_ORG_SLUG=your-org-slug
SENTRY_BASE_URL=https://sentry.io

# Optional settings
MCP_SANDBOX_MODE=hybrid
MCP_ENABLE_METRICS=true
```

**Important**: Add `.env` to `.gitignore`:

```bash
echo ".env" >> .gitignore
```

Load in Python:

```python
from dotenv import load_dotenv
load_dotenv()

from sentry_mcp import SentryMCPOptimized

sentry = SentryMCPOptimized()  # Reads from environment
```

**Advantage**: Easy to manage, environment-specific configuration.

---

### Method 3: Direct Instantiation

Pass credentials directly when creating instance:

```python
from sentry_mcp import SentryMCPOptimized

sentry = SentryMCPOptimized(
    auth_token="sntrys_abc123...",
    organization="your-org-slug"
)
```

**Disadvantage**: Credentials in code (not recommended for production).

---

### Method 4: Configuration Object

Use a configuration object for advanced settings:

```python
from sentry_mcp import SentryMCPOptimized, SentryConfig
from pydantic import SecretStr

config = SentryConfig(
    auth_token=SecretStr("sntrys_abc123..."),
    organization="your-org-slug",
    base_url="https://sentry.io",
    request_timeout=30,
    max_retries=3
)

sentry = SentryMCPOptimized(config=config)
```

**Advantage**: Type-safe, validated configuration with advanced options.

---

### Method 5: Configuration File

Create `~/.sentry-mcp/config.yaml`:

```yaml
# config.yaml
auth_token: ${SENTRY_AUTH_TOKEN}  # Reference environment variable
organization: your-org-slug
base_url: https://sentry.io

performance:
  request_timeout: 30
  max_retries: 3
  cache_ttl: 300

security:
  sandbox_mode: hybrid
  enable_audit_log: true

observability:
  enable_metrics: true
  metrics_backend: prometheus
```

Load in Python:

```python
import yaml
from sentry_mcp import SentryConfig, SentryMCPOptimized

with open("~/.sentry-mcp/config.yaml") as f:
    config_dict = yaml.safe_load(f)

config = SentryConfig(**config_dict)
sentry = SentryMCPOptimized(config=config)
```

**Advantage**: Centralized configuration, supports multiple profiles.

## Token Permissions

### Required Scopes

Minimum required permissions for Sentry MCP Optimized:

| Scope | Permission | Purpose |
|-------|------------|---------|
| `org:read` | Read | List organizations |
| `project:read` | Read | List projects |
| `event:read` | Read | Query events |
| `issue:read` | Read | List issues |
| `issue:write` | Write | Update/delete issues |

### Recommended Scopes

For full functionality:

```
org:read
org:write
project:read
project:write
event:read
event:write
issue:read
issue:write
team:read
member:read
```

### Create Minimum Permission Token

For read-only access (monitoring):

```
org:read
project:read
event:read
issue:read
```

### Create Full Access Token

For complete management:

```
org:admin
project:admin
event:admin
issue:admin
team:admin
member:admin
```

### Project-Scoped Tokens (v0.2.0+)

Limit token to specific projects:

1. In Sentry, go to **Project Settings**
2. Navigate to **Auth Tokens**
3. Create project-specific token
4. Use in configuration:

```python
config = SentryConfig(
    auth_token="project_token...",
    organization="your-org",
    default_project="PYTHON-1"  # Token only works for this project
)
```

## Security Best Practices

### 1. Never Commit Credentials

**Bad**:
```python
# ❌ DON'T DO THIS
sentry = SentryMCPOptimized(
    auth_token="sntrys_abc123...",  # Exposed in version control
    organization="my-org"
)
```

**Good**:
```python
# ✅ USE ENVIRONMENT VARIABLES
import os
sentry = SentryMCPOptimized(
    auth_token=os.getenv("SENTRY_AUTH_TOKEN"),
    organization=os.getenv("SENTRY_ORG_SLUG")
)
```

### 2. Use .gitignore

Always ignore credential files:

```bash
# .gitignore
.env
.env.local
.env.production
config.yaml
secrets/
*.pem
*.key
```

### 3. Rotate Tokens Regularly

Best practice: Rotate every 90 days

1. Create new token in Sentry
2. Update environment variable
3. Verify functionality
4. Revoke old token

```bash
# Script to rotate token
export SENTRY_AUTH_TOKEN_OLD=$SENTRY_AUTH_TOKEN
export SENTRY_AUTH_TOKEN="new_token_here"

# Test new token
python -c "from sentry_mcp import SentryMCPOptimized; s = SentryMCPOptimized(); print('Success')"

# If successful, revoke old token in Sentry UI
```

### 4. Use Minimal Permissions

Create role-specific tokens:

**Monitoring Bot** (read-only):
```yaml
permissions:
  - org:read
  - project:read
  - event:read
  - issue:read
```

**Triage Bot** (read + update):
```yaml
permissions:
  - org:read
  - project:read
  - event:read
  - issue:read
  - issue:write
```

**Admin Bot** (full access):
```yaml
permissions:
  - org:admin
  - project:admin
  - event:admin
  - issue:admin
```

### 5. Secure Token Storage

**Development**:
```bash
# Store in environment file with restricted permissions
chmod 600 .env
```

**Production**:
```bash
# Use secret management service
# AWS Secrets Manager, HashiCorp Vault, etc.

# Example with AWS Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id sentry/mcp/auth-token \
  --query SecretString \
  --output text
```

**Docker**:
```dockerfile
# Use Docker secrets
docker secret create sentry_token ./sentry_token.txt

docker service create \
  --name sentry-mcp \
  --secret sentry_token \
  myapp
```

**Kubernetes**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: sentry-credentials
type: Opaque
stringData:
  auth-token: sntrys_abc123...
  org-slug: your-org
---
apiVersion: v1
kind: Pod
metadata:
  name: sentry-mcp
spec:
  containers:
  - name: app
    image: sentry-mcp-optimized
    env:
    - name: SENTRY_AUTH_TOKEN
      valueFrom:
        secretKeyRef:
          name: sentry-credentials
          key: auth-token
```

### 6. Monitor Token Usage

Enable audit logging:

```python
config = SentryConfig(
    auth_token=token,
    organization=org,
    enable_audit_log=True,
    audit_log_path="/var/log/sentry-mcp/audit.log"
)
```

Audit log format:
```json
{
  "timestamp": "2024-11-24T10:30:00Z",
  "operation": "list_issues",
  "user": "bot@company.com",
  "project": "PYTHON-1",
  "result": "success",
  "token_last_4": "a1b2"
}
```

### 7. Handle Credentials in CI/CD

**GitHub Actions**:
```yaml
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        env:
          SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
          SENTRY_ORG_SLUG: ${{ secrets.SENTRY_ORG_SLUG }}
        run: pytest tests/
```

**GitLab CI**:
```yaml
test:
  script:
    - pytest tests/
  variables:
    SENTRY_AUTH_TOKEN: $SENTRY_AUTH_TOKEN
    SENTRY_ORG_SLUG: $SENTRY_ORG_SLUG
```

## Troubleshooting

### Issue: "AuthenticationError: Invalid token"

**Possible Causes**:
1. Token is incorrect or expired
2. Token has been revoked
3. Environment variable not set

**Solutions**:
```bash
# Verify environment variable
echo $SENTRY_AUTH_TOKEN

# Test token directly
curl -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  https://sentry.io/api/0/organizations/

# Re-create token in Sentry UI
```

---

### Issue: "AuthorizationError: Insufficient permissions"

**Possible Causes**:
1. Token missing required scopes
2. User lacks organization/project access

**Solutions**:
1. Check token scopes in Sentry UI
2. Create new token with required permissions
3. Verify organization membership

```python
# Test with read-only operations first
try:
    projects = await sentry.list_projects()
    print(f"✓ Read access works: {len(projects)} projects")
except Exception as e:
    print(f"✗ Read access failed: {e}")

try:
    await sentry.update_issue(issue_id="123", status="resolved")
    print("✓ Write access works")
except Exception as e:
    print(f"✗ Write access failed: {e}")
```

---

### Issue: "RateLimitError: Rate limit exceeded"

**Possible Causes**:
1. Too many API requests
2. Shared token across multiple services

**Solutions**:
1. Implement rate limiting
2. Use separate tokens per service
3. Enable caching

```python
from sentry_mcp import RateLimitError
import asyncio

async def with_rate_limiting():
    try:
        return await sentry.list_issues("PYTHON-1")
    except RateLimitError as e:
        print(f"Rate limited. Retrying after {e.retry_after}s")
        await asyncio.sleep(e.retry_after)
        return await sentry.list_issues("PYTHON-1")
```

---

### Issue: Token not found in environment

**Debug**:
```python
import os

# Check if variables are set
auth_token = os.getenv("SENTRY_AUTH_TOKEN")
org_slug = os.getenv("SENTRY_ORG_SLUG")

if not auth_token:
    print("❌ SENTRY_AUTH_TOKEN not set")
    print("Set with: export SENTRY_AUTH_TOKEN='your_token'")
else:
    print(f"✓ SENTRY_AUTH_TOKEN set (ends with {auth_token[-4:]})")

if not org_slug:
    print("❌ SENTRY_ORG_SLUG not set")
    print("Set with: export SENTRY_ORG_SLUG='your_org'")
else:
    print(f"✓ SENTRY_ORG_SLUG set: {org_slug}")
```

---

### Issue: Self-hosted Sentry

For self-hosted Sentry installations:

```python
from sentry_mcp import SentryConfig, SentryMCPOptimized

config = SentryConfig(
    auth_token="your_token",
    organization="your_org",
    base_url="https://sentry.your-company.com"  # Your Sentry URL
)

sentry = SentryMCPOptimized(config=config)
```

Verify connectivity:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://sentry.your-company.com/api/0/
```

## Token Management Checklist

### Development Setup
- [ ] Create Sentry auth token with required permissions
- [ ] Set environment variables
- [ ] Add .env to .gitignore
- [ ] Test token with curl
- [ ] Verify token in Python

### Production Deployment
- [ ] Use secret management service
- [ ] Create separate tokens per environment
- [ ] Use minimal required permissions
- [ ] Enable audit logging
- [ ] Set up token rotation schedule
- [ ] Configure monitoring/alerts
- [ ] Document token purpose and owner

### Security Audit
- [ ] All tokens use minimum required permissions
- [ ] No credentials in version control
- [ ] Tokens rotated in last 90 days
- [ ] Unused tokens revoked
- [ ] Audit logs reviewed regularly
- [ ] Token usage monitored
- [ ] Incident response plan documented

## Additional Resources

- [Sentry API Authentication Docs](https://docs.sentry.io/api/auth/)
- [Sentry Auth Tokens](https://docs.sentry.io/api/auth/#auth-tokens)
- [Security Policy](../SECURITY.md)
- [MCP Optimizer Framework Security](https://github.com/rhart696/mcp-optimizer-framework/blob/main/docs/SECURITY.md)

---

**Last Updated**: 2024-11-24
**Version**: 0.1.0
