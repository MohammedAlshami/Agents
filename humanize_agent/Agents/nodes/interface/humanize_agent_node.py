"""
Humanize Agent Node
Makes text sound more human and natural for academic writing.
"""

from typing import Dict, Any, List, Optional
from .base_node import BaseNode, NodeResult, NodeStatus
from ..nodes.ai.humanize_agent import HumanizeAgent


class HumanizeAgentNode(BaseNode):
    """
    Node for humanizing AI-generated text to make it sound more natural and human-like.
    
    Input: Text to humanize, optional context
    Output: Humanized text with metadata
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Humanize Agent Node.
        
        Args:
            api_key: OpenAI API key
        """
        super().__init__(
            node_id="humanize_agent",
            name="Humanize Agent",
            description="Makes AI-generated text sound more human and natural for academic writing"
        )
        
        # Initialize the underlying HumanizeAgent
        self.humanize_agent = HumanizeAgent(
            api_key=api_key
        )
    
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Define the input schema for Humanize Agent Node.
        
        Returns:
            Dict describing the expected input structure
        """
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to humanize"
                },
                "context": {
                    "type": "string",
                    "description": "Optional context for the humanization",
                    "default": ""
                },
                "stream": {
                    "type": "boolean",
                    "description": "Whether to stream the response",
                    "default": False
                }
            },
            "required": ["text"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Define the output schema for Humanize Agent Node.
        
        Returns:
            Dict describing the output structure
        """
        return {
            "type": "object",
            "properties": {
                "original_text": {
                    "type": "string",
                    "description": "The original input text"
                },
                "humanized_text": {
                    "type": "string",
                    "description": "The humanized version of the text"
                },
                "success": {
                    "type": "boolean",
                    "description": "Whether the humanization was successful"
                },
                "error": {
                    "type": "string",
                    "description": "Error message if humanization failed"
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
            "required": ["original_text", "humanized_text", "success", "timestamp", "model", "agent"]
        }
    
    def execute(self, inputs: Dict[str, Any]) -> NodeResult:
        """
        Execute the Humanize Agent Node.
        
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
            text = inputs["text"]
            context = inputs.get("context", "")
            stream = inputs.get("stream", False)
            
            # Update status
            self.status = NodeStatus.RUNNING
            
            # Process the text
            if stream:
                # Handle streaming response (simplified for now)
                result = self.humanize_agent.humanize_text(text)
            else:
                # Handle regular response
                result = self.humanize_agent.humanize_text(text)
            
            # Update status
            self.status = NodeStatus.COMPLETED
            
            return NodeResult(
                status=NodeStatus.COMPLETED,
                output=result,
                metadata={
                    "node_id": self.node_id,
                    "execution_time": "N/A",  # TODO: Add timing
                    "text_length": len(text),
                    "humanized_length": len(result.get("humanized_text", "")),
                    "success": result.get("success", False)
                }
            )
            
        except Exception as e:
            self.status = NodeStatus.FAILED
            return NodeResult(
                status=NodeStatus.FAILED,
                output={},
                error=f"Humanize Agent execution failed: {str(e)}"
            )
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the system status of the Humanize Agent.
        
        Returns:
            Dict with system status information
        """
        return {
            "humanize_agent_enabled": True,
            "model": "gpt-4o-mini",
            "temperature": 0.2,
            "max_tokens": 4000
        }
    
    def get_supported_features(self) -> List[str]:
        """
        Get the list of supported features.
        
        Returns:
            List of supported feature names
        """
        return [
            "text_humanization",
            "academic_writing_style",
            "ai_detection_avoidance",
            "natural_language_processing"
        ]
    
    def get_humanization_examples(self) -> Dict[str, List[str]]:
        """
        Get example inputs and outputs for humanization.
        
        Returns:
            Dict mapping feature names to example texts
        """
        return {
            "academic_writing": [
                "Furthermore, the results indicate that the hypothesis was supported by the data analysis.",
                "Moreover, it is important to note that the findings demonstrate significant correlation.",
                "In conclusion, the research provides evidence for the proposed theoretical framework."
            ],
            "technical_writing": [
                "The system processes the data through multiple algorithms to generate accurate results.",
                "The implementation utilizes advanced machine learning techniques for optimization.",
                "The methodology involves comprehensive analysis of the collected datasets."
            ],
            "research_articles": [
                "The study examined the relationship between variables using statistical analysis.",
                "The methodology section describes the experimental design and data collection procedures.",
                "The results section presents the findings from the quantitative analysis."
            ]
        }
