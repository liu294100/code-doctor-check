# -*- coding: utf-8 -*-
"""Tests for Apifox CLI MCP Server."""
import pytest


class TestCliMcp:
    """Test suite for CLI MCP server."""

    def test_project_flag_empty(self):
        """Test _project_flag with empty string."""
        from apifox_cli_mcp.server import _project_flag
        assert _project_flag("") == ""

    def test_project_flag_with_id(self):
        """Test _project_flag with project ID."""
        from apifox_cli_mcp.server import _project_flag
        assert _project_flag("12345") == "--project 12345"

    def test_json_result(self):
        """Test _json_result formatting."""
        from apifox_cli_mcp.server import _json_result
        result = _json_result({"ok": True, "data": "test"})
        assert '"ok": true' in result
        assert '"data": "test"' in result
