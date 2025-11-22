"""
Text Operations Workflow
Handles various text operations: improve_transitions, continue_writing, make_formal, make_shorter, make_longer, fix_grammar_spelling
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from ..interface.improve_transitions_agent_node import ImproveTransitionsAgentNode
from ..interface.continue_writing_agent_node import ContinueWritingAgentNode
from ..interface.make_formal_agent_node import MakeFormalAgentNode
from ..interface.make_shorter_agent_node import MakeShorterAgentNode
from ..interface.make_longer_agent_node import MakeLongerAgentNode
from ..interface.fix_grammar_spelling_agent_node import FixGrammarSpellingAgentNode

logger = logging.getLogger(__name__)


class TextOperationsWorkflow:
    """
    Workflow for handling various text operations.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the text operations workflow.
        
        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key
        
        # Initialize all agent nodes
        self.improve_transitions_node = ImproveTransitionsAgentNode(api_key=api_key)
        self.continue_writing_node = ContinueWritingAgentNode(api_key=api_key)
        self.make_formal_node = MakeFormalAgentNode(api_key=api_key)
        self.make_shorter_node = MakeShorterAgentNode(api_key=api_key)
        self.make_longer_node = MakeLongerAgentNode(api_key=api_key)
        self.fix_grammar_spelling_node = FixGrammarSpellingAgentNode(api_key=api_key)
        
        logger.info("Text Operations Workflow initialized")
    
    def process_operation(
        self,
        operation: str,
        text: str,
        target_length: Optional[int] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a text operation.
        
        Args:
            operation: The operation to perform (improve_transitions, continue_writing, make_formal, make_shorter, make_longer, fix_grammar_spelling)
            text: The text to process
            target_length: Optional target length (for make_shorter/make_longer)
            context: Optional additional context
            
        Returns:
            Dict containing the processed text and metadata
        """
        logger.info(f"Processing operation: {operation}")
        
        try:
            start_time = datetime.now()
            
            # Route to appropriate agent based on operation
            if operation == "improve_transitions":
                result = self.improve_transitions_node.execute({
                    "text": text,
                    "context": context
                })
            elif operation == "continue_writing":
                result = self.continue_writing_node.execute({
                    "text": text,
                    "context": context
                })
            elif operation == "make_formal":
                result = self.make_formal_node.execute({
                    "text": text,
                    "context": context
                })
            elif operation == "make_shorter":
                result = self.make_shorter_node.execute({
                    "text": text,
                    "target_length": target_length,
                    "context": context
                })
            elif operation == "make_longer":
                result = self.make_longer_node.execute({
                    "text": text,
                    "target_length": target_length,
                    "context": context
                })
            elif operation == "fix_grammar_spelling":
                result = self.fix_grammar_spelling_node.execute({
                    "text": text,
                    "context": context
                })
            else:
                return {
                    "success": False,
                    "error": f"Invalid operation: {operation}",
                    "operation": operation,
                    "timestamp": datetime.now().isoformat(),
                    "agent": "text_operations"
                }
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            if result.status.value == "completed":
                output = result.output
                
                # Extract the processed text based on operation
                if operation == "improve_transitions":
                    processed_text = output.get("improved_text", "")
                elif operation == "continue_writing":
                    processed_text = output.get("continuation", "")
                elif operation == "make_formal":
                    processed_text = output.get("formal_text", "")
                elif operation == "make_shorter":
                    processed_text = output.get("condensed_text", "")
                elif operation == "make_longer":
                    processed_text = output.get("expanded_text", "")
                elif operation == "fix_grammar_spelling":
                    processed_text = output.get("corrected_text", "")
                else:
                    processed_text = ""
                
                # Add a unified processed_text field for easier access
                return {
                    **output,
                    "processed_text": processed_text,  # Unified field for all operations
                    "execution_time": execution_time,
                    "workflow_id": f"text_ops_{start_time.timestamp()}"
                }
            else:
                return {
                    "success": False,
                    "error": result.error or "Operation failed",
                    "operation": operation,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": execution_time,
                    "agent": "text_operations"
                }
                
        except Exception as e:
            logger.error(f"Error processing operation {operation}: {str(e)}")
            return {
                "success": False,
                "error": f"Error processing operation: {str(e)}",
                "operation": operation,
                "timestamp": datetime.now().isoformat(),
                "agent": "text_operations"
            }

