"""
Improve Transitions Agent Node
Improves transitions between sentences and paragraphs.
"""

from typing import Dict, Any
from .base_node import BaseNode, NodeResult, NodeStatus
from ..nodes.ai.improve_transitions_agent import ImproveTransitionsAgent


class ImproveTransitionsAgentNode(BaseNode):
    """
    Node for improving transitions in text.
    """
    
    def __init__(self, api_key: str = None):
        super().__init__(
            node_id="improve_transitions_agent",
            name="Improve Transitions Agent",
            description="Improves transitions between sentences and paragraphs"
        )
        self.agent = ImproveTransitionsAgent(api_key=api_key)
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to improve transitions for"},
                "context": {"type": "string", "description": "Additional context", "default": ""}
            },
            "required": ["text"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "original_text": {"type": "string"},
                "improved_text": {"type": "string"},
                "success": {"type": "boolean"},
                "operation": {"type": "string"},
                "error": {"type": "string"}
            },
            "required": ["original_text", "improved_text", "success", "operation"]
        }
    
    def execute(self, inputs: Dict[str, Any]) -> NodeResult:
        try:
            if not self.validate_inputs(inputs):
                return NodeResult(status=NodeStatus.FAILED, output={}, error="Invalid input schema")
            
            self.status = NodeStatus.RUNNING
            result = self.agent.improve_transitions(
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

