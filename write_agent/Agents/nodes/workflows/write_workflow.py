"""
Simplified Write Workflow
Simple workflow that uses the write agent for text generation.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Import the write agent node
from ..interface.write_agent_node import WriteAgentNode

logger = logging.getLogger(__name__)


class SimpleWriteWorkflow:
    """
    Simplified workflow that uses the write agent for text generation.
    
    This workflow:
    1. Takes user topic/prompt input
    2. Uses write agent to generate text content
    3. Returns the generated text
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Simple Write workflow.
        
        Args:
            api_key: OpenAI API key
        """
        # Load environment variables
        load_dotenv()
        
        # Initialize only the write agent
        self.write_agent = WriteAgentNode(
            api_key=api_key
        )
    
    def process_topic(
        self,
        topic: str,
        writing_style: str = "academic",
        word_count: Optional[int] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process topic using the write agent to generate text content.
        
        Args:
            topic: The topic or prompt to write about
            writing_style: Writing style to use (default: "academic")
            word_count: Optional target word count
            context: Optional additional context
            
        Returns:
            Dict containing the generated text and metadata
        """
        logger.info(f"Processing topic: {topic[:100]}...")
        
        try:
            start_time = datetime.now()
            
            # Extract context string if provided
            context_str = ""
            if context:
                context_str = context.get("context", "") if isinstance(context, dict) else str(context)
            
            # Use write agent to process topic
            result = self.write_agent.execute({
                "topic": topic,
                "writing_style": writing_style,
                "word_count": word_count,
                "context": context_str,
                "stream": False
            })
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            if result.status.value == "completed":
                output = result.output
                
                logger.info(f"Text generated successfully (took {execution_time:.2f}s)")
                
                return {
                    "success": True,
                    "topic": topic,
                    "generated_text": output.get("generated_text", ""),
                    "writing_style": writing_style,
                    "word_count": word_count,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat(),
                    "workflow_id": f"simple_write_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "model": output.get("model", "gpt-4o-mini"),
                    "agent": output.get("agent", "write")
                }
            else:
                logger.error(f"Text generation failed: {result.error}")
                return {
                    "success": False,
                    "error": result.error,
                    "topic": topic,
                    "generated_text": "",
                    "writing_style": writing_style,
                    "word_count": word_count,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error processing topic: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic,
                "generated_text": "",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the system status of the write workflow.
        
        Returns:
            Dict with system status information
        """
        return {
            "write_agent_status": self.write_agent.get_system_status(),
            "supported_features": self.write_agent.get_supported_features(),
            "writing_style_examples": self.write_agent.get_writing_style_examples()
        }

