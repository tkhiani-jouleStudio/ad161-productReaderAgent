"""MCP tools indirection layer.

This module re-exports get_mcp_tools from the MCP provider so that:
1. Application code imports from here (never directly from the provider)
2. Tests can monkey-patch this single import point
"""
from mcp_providers.agw import get_mcp_tools

__all__ = ["get_mcp_tools"]
