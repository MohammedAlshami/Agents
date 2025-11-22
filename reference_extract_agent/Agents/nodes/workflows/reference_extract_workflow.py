"""
Simplified Reference Extract Workflow
Simple workflow that uses the reference extract agent for extracting references from text.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Import the reference extract agent node
from ..interface.reference_extract_agent_node import ReferenceExtractAgentNode

logger = logging.getLogger(__name__)


class SimpleReferenceExtractWorkflow:
    """
    Simplified workflow that uses the reference extract agent for extracting references from text.
    
    This workflow:
    1. Takes text content
    2. Uses reference extract agent to extract and structure references
    3. Returns the extracted references with metadata
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Simple Reference Extract workflow.
        
        Args:
            api_key: OpenAI API key
        """
        # Load environment variables
        load_dotenv()
        
        # Initialize only the reference extract agent
        self.reference_extract_agent = ReferenceExtractAgentNode(
            api_key=api_key
        )
    
    def process_text(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process text using the reference extract agent to extract references.
        
        Args:
            text: The text content to extract references from
            context: Optional additional context
            
        Returns:
            Dict containing the extracted references and metadata
        """
        logger.info(f"Processing text for reference extraction: {text[:100]}...")
        
        try:
            start_time = datetime.now()
            
            # Use reference extract agent to process text
            result = self.reference_extract_agent.execute({
                "text": text,
                "context": context.get("context", "") if context else ""
            })
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            if result.status.value == "completed":
                output = result.output
                references = output.get("references", [])
                metadata = output.get("extraction_metadata", {})
                
                logger.info(f"References extracted successfully (took {execution_time:.2f}s)")
                
                return {
                    "success": True,
                    "text": text,
                    "references": references,
                    "extraction_metadata": metadata,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat(),
                    "workflow_id": f"simple_reference_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "model": "gpt-4o-mini",
                    "agent": "reference_extract"
                }
            else:
                logger.error(f"Reference extraction failed: {result.error}")
                return {
                    "success": False,
                    "error": result.error,
                    "text": text,
                    "references": [],
                    "extraction_metadata": {},
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error processing text for reference extraction: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "text": text,
                "references": [],
                "extraction_metadata": {},
                "timestamp": datetime.now().isoformat()
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the system status of the reference extract workflow.
        
        Returns:
            Dict with system status information
        """
        return {
            "reference_extract_agent_status": self.reference_extract_agent.get_system_status(),
            "supported_features": self.reference_extract_agent.get_supported_features(),
            "supported_formats": self.reference_extract_agent.get_supported_formats(),
            "example_texts": self.reference_extract_agent.get_example_texts()
        }
