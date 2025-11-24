"""
Sentry MCP Optimized - Optimized Sentry integration using MCP Optimizer Framework
"""

__version__ = "1.0.0"

from .adaptors.sentry import SentryAdaptor

__all__ = [
    "SentryAdaptor",
]
