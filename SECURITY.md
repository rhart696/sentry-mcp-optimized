# Security Policy

## Supported Versions

We release patches for security vulnerabilities. The following versions are currently being supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Security Features

Sentry MCP Optimized inherits robust security features from the MCP Optimizer Framework:

### Multi-Layer Sandboxing

- **Docker Isolation**: Containerized execution environment
- **gVisor Support**: Additional kernel-level isolation
- **WASM Runtime**: WebAssembly sandbox for untrusted code
- **Network Isolation**: Controlled external access

### Credential Management

- **Environment Variables**: No hardcoded credentials
- **Secret Rotation**: Support for credential updates without restart
- **Token Validation**: Authentication token verification
- **Minimal Permissions**: Principle of least privilege

### API Security

- **Rate Limiting**: Built-in protection against API abuse
- **Input Validation**: All inputs sanitized and validated
- **Error Sanitization**: No sensitive data in error messages
- **Audit Logging**: Complete operation audit trail

### Resource Protection

- **CPU Limits**: Configurable CPU usage caps
- **Memory Limits**: Configurable memory constraints
- **Execution Timeout**: Automatic termination of long-running operations
- **Request Size Limits**: Protection against oversized payloads

## Security Best Practices

### For Users

1. **Protect Your Sentry Auth Token**
   ```bash
   # Use environment variables, never hardcode
   export SENTRY_AUTH_TOKEN="your-token-here"

   # Set restrictive file permissions
   chmod 600 .env

   # Never commit .env files
   echo ".env" >> .gitignore
   ```

2. **Use Scoped Tokens**
   - Create Sentry tokens with minimal required permissions
   - Use project-specific tokens when possible
   - Rotate tokens regularly (recommended: every 90 days)

3. **Monitor API Usage**
   ```python
   # Enable audit logging
   config = SentryConfig(
       auth_token=os.getenv("SENTRY_AUTH_TOKEN"),
       enable_audit_log=True,
       audit_log_path="/var/log/sentry-mcp/audit.log"
   )
   ```

4. **Network Security**
   - Use HTTPS for all Sentry API calls (enforced by default)
   - Configure firewall rules for outbound connections
   - Use VPN or private networks for sensitive environments

5. **Sandbox Configuration**
   ```python
   # Production: Use strict sandboxing
   config = SentryConfig(
       sandbox_mode="strict",  # Docker + gVisor
       allow_network=False,    # Disable unless needed
       enable_metrics=True     # Monitor for anomalies
   )
   ```

### For Developers

1. **Code Security**
   - Run security linters: `bandit -r sentry_mcp/`
   - Check dependencies: `safety check`
   - Review code before merging
   - Use type hints to prevent type-related bugs

2. **Dependency Management**
   ```bash
   # Check for known vulnerabilities
   pip install safety
   safety check

   # Keep dependencies updated
   pip list --outdated
   pip install --upgrade <package>
   ```

3. **Testing**
   - Include security tests in test suite
   - Test authentication failures
   - Verify input validation
   - Check error message sanitization

4. **Secret Management**
   ```python
   # Good: Use environment variables
   auth_token = os.getenv("SENTRY_AUTH_TOKEN")

   # Bad: Never hardcode
   auth_token = "abc123..."  # DON'T DO THIS
   ```

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do NOT Open a Public Issue

Security vulnerabilities should not be disclosed publicly until a fix is available.

### 2. Report Privately

**Email**: rhart696@users.noreply.github.com

**Subject**: `[SECURITY] Brief description of vulnerability`

**Include**:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)
- Your contact information (optional, for follow-up)

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 7-14 days
  - Medium: 14-30 days
  - Low: 30-90 days

### 4. Disclosure Process

1. **Acknowledgment**: We'll confirm receipt and begin investigation
2. **Assessment**: Determine severity and impact
3. **Fix Development**: Create patch (in private repository if needed)
4. **Testing**: Verify fix and run security tests
5. **Release**: Deploy patched version
6. **Public Disclosure**: Announce vulnerability and fix (with your permission)

### 5. Security Advisory

We will publish a security advisory including:
- Vulnerability description
- Affected versions
- Fix version
- Workarounds (if available)
- Credits (if you wish to be acknowledged)

## Vulnerability Severity Levels

### Critical
- Remote code execution
- Complete authentication bypass
- Data exposure of all users
- **Response**: Immediate fix, emergency release

### High
- Privilege escalation
- SQL injection
- Authentication bypass for specific endpoints
- **Response**: Fix within 7 days, expedited release

### Medium
- Cross-site scripting (XSS)
- Information disclosure (limited)
- Denial of service
- **Response**: Fix in next regular release (2-4 weeks)

### Low
- Minor information disclosure
- Non-exploitable bugs with security implications
- **Response**: Fix in future release

## Security Checklist for Deployments

### Production Deployment

- [ ] Use environment variables for all credentials
- [ ] Enable strict sandboxing mode
- [ ] Configure resource limits (CPU, memory, timeout)
- [ ] Enable audit logging
- [ ] Set up monitoring and alerts
- [ ] Use minimal Sentry token permissions
- [ ] Disable unnecessary network access
- [ ] Keep all dependencies updated
- [ ] Regular security scans (weekly)
- [ ] Incident response plan documented

### Development Environment

- [ ] Use test Sentry organization
- [ ] Separate credentials from production
- [ ] Enable debug logging
- [ ] Run security linters in pre-commit hooks
- [ ] Regular dependency updates
- [ ] Code review for security issues

## Known Security Considerations

### API Token Exposure

**Risk**: Sentry auth tokens grant access to organization data

**Mitigation**:
- Use environment variables
- Rotate tokens regularly
- Monitor token usage
- Use project-scoped tokens

### Rate Limiting

**Risk**: API abuse could exhaust Sentry rate limits

**Mitigation**:
- Built-in rate limiting protection
- Configurable retry logic
- Circuit breaker pattern
- Request throttling

### Data Privacy

**Risk**: Issue data may contain sensitive information

**Mitigation**:
- Data minimization (return only necessary fields)
- Sanitize logs and errors
- Comply with data protection regulations
- Encryption in transit (HTTPS)

### Dependency Vulnerabilities

**Risk**: Third-party packages may have security issues

**Mitigation**:
- Regular dependency updates
- Automated vulnerability scanning
- Pin dependency versions
- Review dependency changes

## Compliance

### Standards

- **OWASP Top 10**: Mitigations for common web vulnerabilities
- **CWE/SANS Top 25**: Coverage of dangerous software errors
- **ISO 27001**: Security management best practices

### Privacy

- **GDPR**: Data minimization and privacy by design
- **CCPA**: User data protection
- **SOC 2**: Security controls and monitoring

## Security Updates

Subscribe to security updates:
- Watch this repository on GitHub
- Star the repository for notifications
- Follow release notes in CHANGELOG.md

## Contact

For security concerns:
- **Email**: rhart696@users.noreply.github.com
- **Response Time**: Within 48 hours
- **PGP Key**: Available upon request

For general questions:
- **GitHub Issues**: Non-security bugs and features
- **GitHub Discussions**: Questions and support

## Acknowledgments

We thank the security researchers and contributors who help keep Sentry MCP Optimized secure:

- Security researchers who responsibly disclose vulnerabilities
- Contributors who improve security through code review
- Users who report potential security issues

## Additional Resources

- [MCP Optimizer Framework Security](https://github.com/rhart696/mcp-optimizer-framework/blob/main/SECURITY.md)
- [Sentry Security Documentation](https://docs.sentry.io/security/)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)

---

**Last Updated**: 2024-11-24

This security policy is subject to change. Check back regularly for updates.
