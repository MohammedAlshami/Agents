"""
Simple Paraphrase Workflow
A simplified workflow for paraphrasing text using the Paraphrase Agent.
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, Any

# Add the parent directory to the path to import Agents modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from Agents.nodes.ai.paraphrase_agent import ParaphraseAgent
except ImportError:
    # Try alternative import path
    try:
        agents_path = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        if agents_path not in sys.path:
            sys.path.insert(0, agents_path)
        from nodes.ai.paraphrase_agent import ParaphraseAgent
    except ImportError as e:
        import traceback
        traceback.print_exc()
        raise ImportError(f"Failed to import ParaphraseAgent: {e}")


class SimpleParaphraseWorkflow:
    """
    Simple workflow for text paraphrasing.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Simple Paraphrase Workflow.
        
        Args:
            api_key (str): Perplexity API key. If None, will use environment variable.
        """
        self.api_key = api_key
        self.agent = ParaphraseAgent(api_key=api_key)
        self.workflow_id = f"simple_paraphrase_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def paraphrase(self, text: str) -> Dict[str, Any]:
        """
        Paraphrase text using the paraphrase agent.
        
        Args:
            text: Text to paraphrase
            
        Returns:
            Dict containing the paraphrased text and metadata
        """
        try:
            start_time = time.time()
            
            # Paraphrase the text using the agent
            result = self.agent.paraphrase(text)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Add workflow metadata
            result.update({
                "workflow_id": self.workflow_id,
                "model": "sonar",
                "agent": "paraphrase",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time if 'start_time' in locals() else 0
            return {
                "success": False,
                "error": f"Error in paraphrase workflow: {str(e)}",
                "original_text": text,
                "paraphrased_text": "",
                "sources": [],
                "metadata": {
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                },
                "workflow_id": self.workflow_id,
                "model": "sonar",
                "agent": "paraphrase",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get workflow status and capabilities."""
        return {
            "workflow_id": self.workflow_id,
            "status": "active",
            "capabilities": [
                "Academic text paraphrasing",
                "Perplexity integration",
                "Academic source references",
                "Structure preservation"
            ],
            "agent_status": {
                "agent_enabled": True,
                "perplexity_service": self.agent.perplexity_service is not None,
                "capabilities": [
                    "Text paraphrasing",
                    "Academic style conversion",
                    "Source extraction"
                ]
            }
        }

