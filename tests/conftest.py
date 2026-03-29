"""
Shared test fixtures and configuration for the test suite.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Provide a TestClient connected to the FastAPI app for making requests.
    
    This fixture is used by all tests to make HTTP requests to the API endpoints.
    """
    return TestClient(app)
