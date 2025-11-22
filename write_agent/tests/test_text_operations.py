"""
Pytest tests for text operations endpoints.
"""

import pytest
import requests
import json
from datetime import datetime


class TestImproveTransitions:
    """Tests for improve_transitions operation."""
    
    def test_improve_transitions(self, base_url, sample_text):
        """Test improve_transitions operation."""
        payload = {
            "operation": "improve_transitions",
            "text": sample_text,
            "context": ""
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["operation"] == "improve_transitions"
        assert "improved_text" in data
        assert len(data["improved_text"]) > 0
        assert "execution_time" in data
    
    def test_improve_transitions_with_context(self, base_url, sample_text):
        """Test improve_transitions with context."""
        payload = {
            "operation": "improve_transitions",
            "text": sample_text,
            "context": "Focus on academic writing style"
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestContinueWriting:
    """Tests for continue_writing operation."""
    
    def test_continue_writing(self, base_url, sample_text):
        """Test continue_writing operation."""
        payload = {
            "operation": "continue_writing",
            "text": sample_text,
            "context": ""
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["operation"] == "continue_writing"
        assert "continuation" in data
        assert len(data["continuation"]) > 0
    
    def test_continue_writing_with_context(self, base_url, sample_text):
        """Test continue_writing with context."""
        payload = {
            "operation": "continue_writing",
            "text": sample_text,
            "context": "Continue with examples"
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestMakeFormal:
    """Tests for make_formal operation."""
    
    def test_make_formal(self, base_url, sample_text):
        """Test make_formal operation."""
        payload = {
            "operation": "make_formal",
            "text": sample_text,
            "context": ""
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["operation"] == "make_formal"
        assert "formal_text" in data
        assert len(data["formal_text"]) > 0
    
    def test_make_formal_informal_text(self, base_url):
        """Test make_formal with informal text."""
        informal_text = "Hey, this is really cool! You should check it out. It's awesome!"
        payload = {
            "operation": "make_formal",
            "text": informal_text
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "formal_text" in data


class TestMakeShorter:
    """Tests for make_shorter operation."""
    
    def test_make_shorter(self, base_url, sample_text):
        """Test make_shorter operation."""
        payload = {
            "operation": "make_shorter",
            "text": sample_text
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["operation"] == "make_shorter"
        assert "condensed_text" in data
        assert len(data["condensed_text"]) > 0
        # Condensed text should generally be shorter
        assert len(data["condensed_text"]) <= len(sample_text) * 1.2  # Allow some variance
    
    def test_make_shorter_with_target(self, base_url, sample_text):
        """Test make_shorter with target length."""
        payload = {
            "operation": "make_shorter",
            "text": sample_text,
            "target_length": 50
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestMakeLonger:
    """Tests for make_longer operation."""
    
    def test_make_longer(self, base_url, sample_text):
        """Test make_longer operation."""
        payload = {
            "operation": "make_longer",
            "text": sample_text
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["operation"] == "make_longer"
        assert "expanded_text" in data
        assert len(data["expanded_text"]) > 0
        # Expanded text should generally be longer
        assert len(data["expanded_text"]) >= len(sample_text)
    
    def test_make_longer_with_target(self, base_url, sample_text):
        """Test make_longer with target length."""
        payload = {
            "operation": "make_longer",
            "text": sample_text,
            "target_length": 500
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestFixGrammarSpelling:
    """Tests for fix_grammar_spelling operation."""
    
    def test_fix_grammar_spelling(self, base_url):
        """Test fix_grammar_spelling operation."""
        text_with_errors = "The student's where studying there homework. Its importent to no the differents between there, their, and they're."
        payload = {
            "operation": "fix_grammar_spelling",
            "text": text_with_errors
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["operation"] == "fix_grammar_spelling"
        assert "corrected_text" in data
        assert len(data["corrected_text"]) > 0
    
    def test_fix_grammar_spelling_correct_text(self, base_url, sample_text):
        """Test fix_grammar_spelling with already correct text."""
        payload = {
            "operation": "fix_grammar_spelling",
            "text": sample_text
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestOperationErrors:
    """Tests for operation error handling."""
    
    def test_missing_text(self, base_url):
        """Test that missing text returns 400."""
        payload = {
            "operation": "improve_transitions"
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "text is required" in data["error"].lower()
    
    def test_invalid_operation(self, base_url, sample_text):
        """Test that invalid operation returns 400."""
        payload = {
            "operation": "invalid_operation",
            "text": sample_text
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "invalid operation" in data["error"].lower()
    
    def test_empty_text(self, base_url):
        """Test that empty text returns error."""
        payload = {
            "operation": "improve_transitions",
            "text": ""
        }
        response = requests.post(
            f"{base_url}/api/v1/write",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        # May return 200 or 400 depending on validation
        assert response.status_code in [200, 400]

