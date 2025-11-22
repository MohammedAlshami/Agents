"""
Fix Grammar and Spelling Agent Node
Fixes grammar, spelling, and punctuation errors.
"""

from typing import Dict, Any
from .base_node import BaseNode, NodeResult, NodeStatus
from ..nodes.ai.fix_grammar_spelling_agent import FixGrammarSpellingAgent


class FixGrammarSpellingAgentNode(BaseNode):
    """
    Node for fixing grammar, spelling, and punctuation errors.
    """
    
    def __init__(self, api_key: str = None):
        super().__init__(
            node_id="fix_grammar_spelling_agent",
            name="Fix Grammar and Spelling Agent",
            description="Fixes grammar, spelling, and punctuation errors"
        )
        self.agent = FixGrammarSpellingAgent(api_key=api_key)
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to fix"},
                "context": {"type": "string", "description": "Additional context", "default": ""}
            },
            "required": ["text"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "original_text": {"type": "string"},
                "corrected_text": {"type": "string"},
                "success": {"type": "boolean"},
                "operation": {"type": "string"},
                "error": {"type": "string"}
            },
            "required": ["original_text", "corrected_text", "success", "operation"]
        }
    
    def execute(self, inputs: Dict[str, Any]) -> NodeResult:
        try:
            if not self.validate_inputs(inputs):
                return NodeResult(status=NodeStatus.FAILED, output={}, error="Invalid input schema")
            
            self.status = NodeStatus.RUNNING
            result = self.agent.fix_grammar_spelling(
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

