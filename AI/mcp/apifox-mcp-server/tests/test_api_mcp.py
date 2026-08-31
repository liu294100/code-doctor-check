# -*- coding: utf-8 -*-
"""Tests for Apifox API MCP Server."""
import pytest


class TestApiMcp:
    """Test suite for API MCP server."""

    def test_is_internal_url_localhost(self):
        """Test _is_internal_url with localhost."""
        from apifox_api_mcp.server import _is_internal_url
        assert _is_internal_url("http://localhost:8080/api") is True
        assert _is_internal_url("http://127.0.0.1:8080/api") is True

    def test_is_internal_url_private(self):
        """Test _is_internal_url with private IPs."""
        from apifox_api_mcp.server import _is_internal_url
        assert _is_internal_url("http://10.0.0.1/api") is True
        assert _is_internal_url("http://192.168.1.1/api") is True
        assert _is_internal_url("http://172.16.0.1/api") is True

    def test_is_internal_url_public(self):
        """Test _is_internal_url with public URLs."""
        from apifox_api_mcp.server import _is_internal_url
        assert _is_internal_url("https://api.apifox.com/v1") is False
        assert _is_internal_url("https://example.com/api") is False

    def test_parse_spec_json(self):
        """Test _parse_spec with JSON."""
        from apifox_api_mcp.server import _parse_spec
        spec = '{"openapi": "3.0.0", "info": {"title": "Test"}}'
        data, err = _parse_spec(spec)
        assert err is None
        assert data["openapi"] == "3.0.0"

    def test_parse_spec_invalid_json(self):
        """Test _parse_spec with invalid JSON."""
        from apifox_api_mcp.server import _parse_spec
        spec = '{invalid json'
        data, err = _parse_spec(spec)
        assert data is None
        assert "JSON parse error" in err

    def test_resolve_project_with_mapping(self):
        """Test _resolve_project with project mapping."""
        import os
        from apifox_api_mcp.server import _resolve_project

        # Without mapping
        assert _resolve_project("12345") == "12345"

    def test_err_format(self):
        """Test _err output format."""
        from apifox_api_mcp.server import _err
        result = _err("Test error", extra="data")
        assert '"ok": false' in result
        assert '"error": "Test error"' in result

    def test_ok_format(self):
        """Test _ok output format."""
        from apifox_api_mcp.server import _ok
        result = _ok({"data": "test"})
        assert '"ok": true' in result
        assert '"data": "test"' in result
