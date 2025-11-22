"""
Write Agent Node
Generates text content from topics/prompts with multiple writing style options.
"""

from typing import Dict, Any, List, Optional
from .base_node import BaseNode, NodeResult, NodeStatus
from ..nodes.ai.write_agent import WriteAgent


class WriteAgentNode(BaseNode):
    """
    Node for generating text content from topics/prompts with multiple writing style options.
    
    Input: Topic/prompt, writing_style, word_count, context
    Output: Generated text with metadata
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Write Agent Node.
        
        Args:
            api_key: OpenAI API key
        """
        super().__init__(
            node_id="write_agent",
            name="Write Agent",
            description="Generates text content from topics/prompts with multiple writing style options"
        )
        
        # Initialize the underlying WriteAgent
        self.write_agent = WriteAgent(
            api_key=api_key
        )
    
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Define the input schema for Write Agent Node.
        
        Returns:
            Dict describing the expected input structure
        """
        return {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic or prompt to write about"
                },
                "writing_style": {
                    "type": "string",
                    "description": "Writing style to use (academic, technical, analytical, comparative, descriptive, argumentative)",
                    "default": "academic",
                    "enum": ["academic", "technical", "analytical", "comparative", "descriptive", "argumentative"]
                },
                "word_count": {
                    "type": "integer",
                    "description": "Target word count (optional)",
                    "default": None
                },
                "context": {
                    "type": "string",
                    "description": "Optional context for the writing",
                    "default": ""
                },
                "stream": {
                    "type": "boolean",
                    "description": "Whether to stream the response",
                    "default": False
                }
            },
            "required": ["topic"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Define the output schema for Write Agent Node.
        
        Returns:
            Dict describing the output structure
        """
        return {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The original topic or prompt"
                },
                "generated_text": {
                    "type": "string",
                    "description": "The generated text content"
                },
                "success": {
                    "type": "boolean",
                    "description": "Whether the generation was successful"
                },
                "error": {
                    "type": "string",
                    "description": "Error message if generation failed"
                },
                "writing_style": {
                    "type": "string",
                    "description": "The writing style used"
                },
                "word_count": {
                    "type": "integer",
                    "description": "Target word count (if specified)"
                },
                "timestamp": {
                    "type": "string",
                    "description": "Timestamp of the response"
                },
                "model": {
                    "type": "string",
                    "description": "The AI model used"
                },
                "agent": {
                    "type": "string",
                    "description": "The agent type used"
                }
            },
            "required": ["topic", "generated_text", "success", "timestamp", "model", "agent"]
        }
    
    def execute(self, inputs: Dict[str, Any]) -> NodeResult:
        """
        Execute the Write Agent Node.
        
        Args:
            inputs: Input data matching the input schema
            
        Returns:
            NodeResult with status, output, and any errors
        """
        try:
            # Validate inputs
            if not self.validate_inputs(inputs):
                return NodeResult(
                    status=NodeStatus.FAILED,
                    output={},
                    error="Invalid input schema"
                )
            
            # Extract inputs
            topic = inputs["topic"]
            writing_style = inputs.get("writing_style", "academic")
            word_count = inputs.get("word_count")
            context = inputs.get("context", "")
            stream = inputs.get("stream", False)
            
            # Update status
            self.status = NodeStatus.RUNNING
            
            # Process the topic
            if stream:
                # Handle streaming response (simplified for now)
                result = self.write_agent.generate_text(
                    topic=topic,
                    writing_style=writing_style,
                    word_count=word_count,
                    context=context
                )
            else:
                # Handle regular response
                result = self.write_agent.generate_text(
                    topic=topic,
                    writing_style=writing_style,
                    word_count=word_count,
                    context=context
                )
            
            # Update status
            self.status = NodeStatus.COMPLETED
            
            return NodeResult(
                status=NodeStatus.COMPLETED,
                output=result,
                metadata={
                    "node_id": self.node_id,
                    "execution_time": "N/A",  # TODO: Add timing
                    "topic_length": len(topic),
                    "generated_length": len(result.get("generated_text", "")),
                    "success": result.get("success", False),
                    "writing_style": writing_style
                }
            )
            
        except Exception as e:
            self.status = NodeStatus.FAILED
            return NodeResult(
                status=NodeStatus.FAILED,
                output={},
                error=f"Write Agent execution failed: {str(e)}"
            )
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the system status of the Write Agent.
        
        Returns:
            Dict with system status information
        """
        return {
            "write_agent_enabled": True,
            "model": "gpt-4o-mini",
            "temperature": 0.3,
            "max_tokens": 4000,
            "supported_styles": ["academic", "technical", "analytical", "comparative", "descriptive", "argumentative"],
            "default_style": "academic"
        }
    
    def get_supported_features(self) -> List[str]:
        """
        Get the list of supported features.
        
        Returns:
            List of supported feature names
        """
        return [
            "text_generation",
            "multiple_writing_styles",
            "topic_based_writing",
            "word_count_targeting",
            "context_aware_generation"
        ]
    
    def get_writing_style_examples(self) -> Dict[str, List[str]]:
        """
        Get example topics for each writing style.
        
        Returns:
            Dict mapping writing styles to example topics
        """
        return {
            "academic": [
                "The impact of climate change on agricultural productivity",
                "Machine learning applications in healthcare diagnostics",
                "Social media's influence on political discourse"
            ],
            "technical": [
                "How to configure a REST API with authentication",
                "Database indexing strategies for performance optimization",
                "Implementing microservices architecture best practices"
            ],
            "analytical": [
                "Analyzing the correlation between education and economic growth",
                "Breaking down the causes of inflation in modern economies",
                "Evaluating the effectiveness of remote work policies"
            ],
            "comparative": [
                "Comparing Python and JavaScript for web development",
                "Cloud computing providers: AWS vs Azure vs GCP",
                "Traditional marketing vs digital marketing strategies"
            ],
            "descriptive": [
                "Describing the architecture of a modern web application",
                "The process of photosynthesis in plants",
                "The cultural significance of ancient Roman architecture"
            ],
            "argumentative": [
                "Why renewable energy should replace fossil fuels",
                "The benefits of implementing universal basic income",
                "The case for stronger data privacy regulations"
            ]
        }

