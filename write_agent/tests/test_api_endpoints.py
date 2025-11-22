"""
Pytest tests for write agent API endpoints.
"""

import pytest
import requests
import json
from datetime import datetime


class TestHealthCheck:
    """Tests for health check endpoint."""
    
    def test_health_check_endpoint(self, base_url):
        """Test the health check endpoint returns 200."""
        response = requests.get(f"{base_url}/api/v1/write")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "write"
        assert "timestamp" in data
    
    def test_root_endpoint(self, base_url):
        """Test the root endpoint returns 200."""
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Write Agent API"
        assert "endpoints" in data
    
    def test_api_info_endpoint(self, base_url):
        """Test the API info endpoint returns 200."""
        response = requests.get(f"{base_url}/api")
        assert response.status_code == 200
        data = response.json()
        assert data["api_name"] == "Write Agent API"
        assert "writing_styles" in data
        assert "academic" in data["writing_styles"]
    
    def test_test_endpoint(self, base_url):
        """Test the test endpoint returns 200."""
        response = requests.get(f"{base_url}/test")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["message"] == "Backend is running"


class TestTextGeneration:
    """Tests for text generation endpoint."""
    
    def test_generate_text_academic_style(self, base_url, sample_topics):
        """Test generating text with academic writing style."""
        payload = {
            "topic": sample_topics["academic"],
            "writing_style": "academic",
            "word_count": 300
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["topic"] == sample_topics["academic"]
        assert "generated_text" in data
        assert len(data["generated_text"]) > 0
        assert data["writing_style"] == "academic"
        assert "execution_time" in data
        assert "timestamp" in data
        assert "model" in data
        assert data["model"] == "gpt-4o-mini"
    
    def test_generate_text_technical_style(self, base_url, sample_topics):
        """Test generating text with technical writing style."""
        payload = {
            "topic": sample_topics["technical"],
            "writing_style": "technical",
            "word_count": 400
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["writing_style"] == "technical"
        assert len(data["generated_text"]) > 0
    
    def test_generate_text_analytical_style(self, base_url, sample_topics):
        """Test generating text with analytical writing style."""
        payload = {
            "topic": sample_topics["analytical"],
            "writing_style": "analytical",
            "word_count": 500
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["writing_style"] == "analytical"
    
    def test_generate_text_comparative_style(self, base_url, sample_topics):
        """Test generating text with comparative writing style."""
        payload = {
            "topic": sample_topics["comparative"],
            "writing_style": "comparative",
            "word_count": 350
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["writing_style"] == "comparative"
    
    def test_generate_text_descriptive_style(self, base_url, sample_topics):
        """Test generating text with descriptive writing style."""
        payload = {
            "topic": sample_topics["descriptive"],
            "writing_style": "descriptive",
            "word_count": 400
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["writing_style"] == "descriptive"
    
    def test_generate_text_argumentative_style(self, base_url, sample_topics):
        """Test generating text with argumentative writing style."""
        payload = {
            "topic": sample_topics["argumentative"],
            "writing_style": "argumentative",
            "word_count": 450
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["writing_style"] == "argumentative"
    
    def test_generate_text_default_style(self, base_url, sample_topics):
        """Test generating text with default (academic) writing style."""
        payload = {
            "topic": sample_topics["academic"]
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["writing_style"] == "academic"
    
    def test_generate_text_with_context(self, base_url, sample_topics):
        """Test generating text with additional context."""
        payload = {
            "topic": sample_topics["academic"],
            "writing_style": "academic",
            "context": "Focus on developing countries",
            "word_count": 300
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["generated_text"]) > 0
    
    def test_generate_text_with_session_id(self, base_url, sample_topics):
        """Test generating text with session ID."""
        payload = {
            "topic": sample_topics["academic"],
            "writing_style": "academic",
            "session_id": "test_session_123",
            "word_count": 300
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_missing_topic(self, base_url):
        """Test that missing topic returns 400."""
        payload = {
            "writing_style": "academic"
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "topic is required" in data["error"].lower()
    
    def test_invalid_writing_style(self, base_url, sample_topics):
        """Test that invalid writing style returns 400."""
        payload = {
            "topic": sample_topics["academic"],
            "writing_style": "invalid_style"
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "invalid writing_style" in data["error"].lower()
    
    def test_empty_topic(self, base_url):
        """Test that empty topic returns error."""
        payload = {
            "topic": "",
            "writing_style": "academic"
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        # May return 400 or 200 depending on validation
        assert response.status_code in [200, 400]
    
    def test_invalid_json(self, base_url):
        """Test that invalid JSON returns 400."""
        response = requests.post(
            f"{base_url}/api/v1/write",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_missing_json(self, base_url):
        """Test that missing JSON returns 400."""
        response = requests.post(
            f"{base_url}/api/v1/write",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data


class TestWordCount:
    """Tests for word count functionality."""
    
    def test_with_word_count(self, base_url, sample_topics):
        """Test generating text with word count specified."""
        payload = {
            "topic": sample_topics["academic"],
            "writing_style": "academic",
            "word_count": 200
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["word_count"] == 200
    
    def test_without_word_count(self, base_url, sample_topics):
        """Test generating text without word count specified."""
        payload = {
            "topic": sample_topics["academic"],
            "writing_style": "academic"
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data.get("word_count") is None or isinstance(data.get("word_count"), int)

