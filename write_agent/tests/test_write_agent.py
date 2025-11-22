"""
Pytest tests for write agent core functionality.
"""

import pytest
import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Agents.nodes.nodes.ai.write_agent import WriteAgent


class TestWriteAgent:
    """Tests for WriteAgent class."""
    
    @pytest.fixture
    def write_agent(self):
        """Fixture providing a WriteAgent instance."""
        return WriteAgent(api_key=os.getenv("OPENAI_API_KEY"))
    
    def test_write_agent_initialization(self, write_agent):
        """Test that WriteAgent initializes correctly."""
        assert write_agent is not None
        assert write_agent.llm is not None
        assert write_agent.llm.model_name == "gpt-4o-mini"
    
    def test_generate_text_academic(self, write_agent):
        """Test generating text with academic style."""
        result = write_agent.generate_text(
            topic="The impact of climate change on agriculture",
            writing_style="academic",
            word_count=200
        )
        assert result["success"] is True
        assert result["writing_style"] == "academic"
        assert len(result["generated_text"]) > 0
        assert "topic" in result
    
    def test_generate_text_technical(self, write_agent):
        """Test generating text with technical style."""
        result = write_agent.generate_text(
            topic="How to configure a REST API",
            writing_style="technical",
            word_count=200
        )
        assert result["success"] is True
        assert result["writing_style"] == "technical"
        assert len(result["generated_text"]) > 0
    
    def test_generate_text_default_style(self, write_agent):
        """Test generating text with default (academic) style."""
        result = write_agent.generate_text(
            topic="The importance of renewable energy"
        )
        assert result["success"] is True
        assert result["writing_style"] == "academic"
    
    def test_generate_text_with_context(self, write_agent):
        """Test generating text with context."""
        result = write_agent.generate_text(
            topic="Machine learning in healthcare",
            writing_style="academic",
            context="Focus on diagnostic applications",
            word_count=200
        )
        assert result["success"] is True
        assert len(result["generated_text"]) > 0
    
    def test_all_writing_styles(self, write_agent):
        """Test all writing styles work correctly."""
        styles = ["academic", "technical", "analytical", "comparative", "descriptive", "argumentative"]
        topic = "Artificial intelligence applications"
        
        for style in styles:
            result = write_agent.generate_text(
                topic=topic,
                writing_style=style,
                word_count=150
            )
            assert result["success"] is True
            assert result["writing_style"] == style
            assert len(result["generated_text"]) > 0
    
    def test_process_input_alias(self, write_agent):
        """Test that process_input is an alias for generate_text."""
        result1 = write_agent.generate_text(
            topic="Test topic",
            writing_style="academic"
        )
        result2 = write_agent.process_input(
            topic="Test topic",
            writing_style="academic"
        )
        assert result1["success"] == result2["success"]
        assert result1["writing_style"] == result2["writing_style"]

