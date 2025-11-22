"""
Pytest tests for write workflow functionality.
"""

import pytest
import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Agents.nodes.workflows.write_workflow import SimpleWriteWorkflow


class TestWriteWorkflow:
    """Tests for SimpleWriteWorkflow class."""
    
    @pytest.fixture
    def workflow(self):
        """Fixture providing a SimpleWriteWorkflow instance."""
        return SimpleWriteWorkflow(api_key=os.getenv("OPENAI_API_KEY"))
    
    def test_workflow_initialization(self, workflow):
        """Test that SimpleWriteWorkflow initializes correctly."""
        assert workflow is not None
        assert workflow.write_agent is not None
    
    def test_process_topic_academic(self, workflow):
        """Test processing topic with academic style."""
        result = workflow.process_topic(
            topic="The impact of climate change on agriculture",
            writing_style="academic",
            word_count=200
        )
        assert result["success"] is True
        assert result["writing_style"] == "academic"
        assert len(result["generated_text"]) > 0
        assert "execution_time" in result
        assert "timestamp" in result
    
    def test_process_topic_technical(self, workflow):
        """Test processing topic with technical style."""
        result = workflow.process_topic(
            topic="How to configure a REST API",
            writing_style="technical",
            word_count=200
        )
        assert result["success"] is True
        assert result["writing_style"] == "technical"
    
    def test_process_topic_default_style(self, workflow):
        """Test processing topic with default (academic) style."""
        result = workflow.process_topic(
            topic="The importance of renewable energy"
        )
        assert result["success"] is True
        assert result["writing_style"] == "academic"
    
    def test_process_topic_with_context(self, workflow):
        """Test processing topic with context."""
        result = workflow.process_topic(
            topic="Machine learning in healthcare",
            writing_style="academic",
            context={"context": "Focus on diagnostic applications"},
            word_count=200
        )
        assert result["success"] is True
        assert len(result["generated_text"]) > 0
    
    def test_get_system_status(self, workflow):
        """Test getting system status."""
        status = workflow.get_system_status()
        assert "write_agent_status" in status
        assert "supported_features" in status
        assert "writing_style_examples" in status
    
    def test_all_writing_styles_workflow(self, workflow):
        """Test all writing styles through workflow."""
        styles = ["academic", "technical", "analytical", "comparative", "descriptive", "argumentative"]
        topic = "Artificial intelligence applications"
        
        for style in styles:
            result = workflow.process_topic(
                topic=topic,
                writing_style=style,
                word_count=150
            )
            assert result["success"] is True
            assert result["writing_style"] == style

