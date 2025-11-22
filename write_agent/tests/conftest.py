"""
Pytest configuration and fixtures for write agent tests.
"""

import pytest
import os
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Base URL for the write agent server
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:5010")


@pytest.fixture
def base_url():
    """Fixture providing the base URL for the write agent server."""
    return BASE_URL


@pytest.fixture
def sample_topics():
    """Fixture providing sample topics for testing."""
    return {
        "academic": "The impact of climate change on agricultural productivity",
        "technical": "How to configure a REST API with authentication",
        "analytical": "Analyzing the correlation between education and economic growth",
        "comparative": "Comparing Python and JavaScript for web development",
        "descriptive": "The architecture of a modern web application",
        "argumentative": "Why renewable energy should replace fossil fuels"
    }


@pytest.fixture
def invalid_topics():
    """Fixture providing invalid test data."""
    return {
        "empty": "",
        "missing": None
    }


@pytest.fixture
def sample_text():
    """Fixture providing sample text for operations testing."""
    return "Machine learning is really cool. It helps computers learn stuff. AI is also interesting. They work together sometimes."

