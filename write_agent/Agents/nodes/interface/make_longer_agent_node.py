"""
Make Longer Agent Node
Expands text while maintaining coherence and adding value.
"""

from typing import Dict, Any
from .base_node import BaseNode, NodeResult, NodeStatus
from ..nodes.ai.make_longer_agent import MakeLongerAgent


class MakeLongerAgentNode(BaseNode):
    """
    Node for expanding text.
    """
    
    def __init__(self, api_key: str = None):
        super().__init__(
            node_id="make_longer_agent",
            name="Make Longer Agent",
            description="Expands text while maintaining coherence and adding value"
        )
        self.agent = MakeLongerAgent(api_key=api_key)
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to expand"},
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
                "expanded_text": {"type": "string"},
                "success": {"type": "boolean"},
                "operation": {"type": "string"},
                "error": {"type": "string"}
            },
            "required": ["original_text", "expanded_text", "success", "operation"]
        }
    
    def execute(self, inputs: Dict[str, Any]) -> NodeResult:
        try:
            if not self.validate_inputs(inputs):
                return NodeResult(status=NodeStatus.FAILED, output={}, error="Invalid input schema")
            
            self.status = NodeStatus.RUNNING
            result = self.agent.make_longer(
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

