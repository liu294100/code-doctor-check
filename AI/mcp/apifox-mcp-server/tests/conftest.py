# -*- coding: utf-8 -*-
"""Pytest configuration and fixtures."""
import pytest


@pytest.fixture
def mock_env(monkeypatch):
    """Fixture to set up mock environment variables."""
    monkeypatch.setenv("APIFOX_PROJECT_ID", "test-project-123")
    monkeypatch.setenv("APIFOX_ACCESS_TOKEN", "test-token-abc")
    monkeypatch.setenv("APIFOX_API_BASE_URL", "https://api.test.apifox.com")
