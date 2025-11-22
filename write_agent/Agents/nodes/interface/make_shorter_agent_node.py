"""
Make Shorter Agent Node
Condenses text while maintaining key information.
"""

from typing import Dict, Any
from .base_node import BaseNode, NodeResult, NodeStatus
from ..nodes.ai.make_shorter_agent import MakeShorterAgent


class MakeShorterAgentNode(BaseNode):
    """
    Node for condensing text.
    """
    
    def __init__(self, api_key: str = None):
        super().__init__(
            node_id="make_shorter_agent",
            name="Make Shorter Agent",
            description="Condenses text while maintaining key information"
        )
        self.agent = MakeShorterAgent(api_key=api_key)
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to condense"},
                "target_length": {"type": "integer", "description": "Target word count or percentage", "default": None},
                "context": {"type": "string", "description": "Additional context", "default": ""}
            },
            "required": ["text"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "original_text": {"type": "string"},
                "condensed_text": {"type": "string"},
                "success": {"type": "boolean"},
                "operation": {"type": "string"},
                "error": {"type": "string"}
            },
            "required": ["original_text", "condensed_text", "success", "operation"]
        }
    
    def execute(self, inputs: Dict[str, Any]) -> NodeResult:
        try:
            if not self.validate_inputs(inputs):
                return NodeResult(status=NodeStatus.FAILED, output={}, error="Invalid input schema")
            
            self.status = NodeStatus.RUNNING
            result = self.agent.make_shorter(
                text=inputs["text"],
                target_length=inputs.get("target_length"),
                context=inputs.get("context")
            )
            self.status = NodeStatus.COMPLETED
            
            return NodeResult(
                status=NodeStatus.COMPLETED,
                output=result,
                metadata={"node_id": self.node_id}
            )
        except Exception as e:
            self.status = NodeStatus.FAILED
            return NodeResult(status=NodeStatus.FAILED, output={}, error=str(e))

