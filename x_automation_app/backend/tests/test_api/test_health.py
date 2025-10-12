"""Tests for health check endpoint."""
import pytest


def test_health_check_returns_200(client):
    """Test that health check endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_returns_correct_status(client):
    """Test that health check returns correct status message."""
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "oki doki"

