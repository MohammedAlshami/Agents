"""
Make Formal Agent Node
Converts text to formal writing style.
"""

from typing import Dict, Any
from .base_node import BaseNode, NodeResult, NodeStatus
from ..nodes.ai.make_formal_agent import MakeFormalAgent


class MakeFormalAgentNode(BaseNode):
    """
    Node for converting text to formal writing style.
    """
    
    def __init__(self, api_key: str = None):
        super().__init__(
            node_id="make_formal_agent",
            name="Make Formal Agent",
            description="Converts text to formal writing style"
        )
        self.agent = MakeFormalAgent(api_key=api_key)
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to formalize"},
                "context": {"type": "string", "description": "Additional context", "default": ""}
            },
            "required": ["text"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "original_text": {"type": "string"},
                "formal_text": {"type": "string"},
                "success": {"type": "boolean"},
                "operation": {"type": "string"},
                "error": {"type": "string"}
            },
            "required": ["original_text", "formal_text", "success", "operation"]
        }
    
    def execute(self, inputs: Dict[str, Any]) -> NodeResult:
        try:
            if not self.validate_inputs(inputs):
                return NodeResult(status=NodeStatus.FAILED, output={}, error="Invalid input schema")
            
            self.status = NodeStatus.RUNNING
            result = self.agent.make_formal(
                text=inputs["text"],
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

