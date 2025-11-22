"""
Simplified Humanize Workflow
Simple workflow that uses the humanize agent for text humanization.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Import the humanize agent node
from ..interface.humanize_agent_node import HumanizeAgentNode

logger = logging.getLogger(__name__)


class SimpleHumanizeWorkflow:
    """
    Simplified workflow that uses the humanize agent for text humanization.
    
    This workflow:
    1. Takes user text input
    2. Uses humanize agent to make text more human-like
    3. Returns the humanized text
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Simple Humanize workflow.
        
        Args:
            api_key: OpenAI API key
        """
        # Load environment variables
        load_dotenv()
        
        # Initialize only the humanize agent
        self.humanize_agent = HumanizeAgentNode(
            api_key=api_key
        )
    
    def process_text(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process text using the humanize agent to make it more human-like.
        
        Args:
            text: The text to humanize
            context: Optional additional context
            
        Returns:
            Dict containing the humanized text and metadata
        """
        logger.info(f"Processing text: {text[:100]}...")
        
        try:
            start_time = datetime.now()
            
            # Use humanize agent to process text
            result = self.humanize_agent.execute({
                "text": text,
                "context": context.get("context", "") if context else "",
                "stream": False
            })
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            if result.status.value == "completed":
                output = result.output
                
                logger.info(f"Text humanized successfully (took {execution_time:.2f}s)")
                
                return {
                    "success": True,
                    "original_text": text,
                    "humanized_text": output.get("humanized_text", ""),
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat(),
                    "workflow_id": f"simple_humanize_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "model": output.get("model", "gpt-4o-mini"),
                    "agent": output.get("agent", "humanize")
                }
            else:
                logger.error(f"Text humanization failed: {result.error}")
                return {
                    "success": False,
                    "error": result.error,
                    "original_text": text,
                    "humanized_text": "",
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "original_text": text,
                "humanized_text": "",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the system status of the humanize workflow.
        
        Returns:
            Dict with system status information
        """
        return {
            "humanize_agent_status": self.humanize_agent.get_system_status(),
            "supported_features": self.humanize_agent.get_supported_features(),
            "humanization_examples": self.humanize_agent.get_humanization_examples()
        }
