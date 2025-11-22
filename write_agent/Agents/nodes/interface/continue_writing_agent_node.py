"""
Continue Writing Agent Node
Continues writing from existing text.
"""

from typing import Dict, Any
from .base_node import BaseNode, NodeResult, NodeStatus
from ..nodes.ai.continue_writing_agent import ContinueWritingAgent


class ContinueWritingAgentNode(BaseNode):
    """
    Node for continuing writing from existing text.
    """
    
    def __init__(self, api_key: str = None):
        super().__init__(
            node_id="continue_writing_agent",
            name="Continue Writing Agent",
            description="Continues writing from existing text"
        )
        self.agent = ContinueWritingAgent(api_key=api_key)
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to continue from"},
                "context": {"type": "string", "description": "Additional context", "default": ""}
            },
            "required": ["text"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "original_text": {"type": "string"},
                "continuation": {"type": "string"},
                "success": {"type": "boolean"},
                "operation": {"type": "string"},
                "error": {"type": "string"}
            },
            "required": ["original_text", "continuation", "success", "operation"]
        }
    
    def execute(self, inputs: Dict[str, Any]) -> NodeResult:
        try:
            if not self.validate_inputs(inputs):
                return NodeResult(status=NodeStatus.FAILED, output={}, error="Invalid input schema")
            
            self.status = NodeStatus.RUNNING
            result = self.agent.continue_writing(
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

