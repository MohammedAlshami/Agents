"""
Paraphrase routes for API v1 - Text paraphrasing with references.
"""

from flask import Blueprint, request, jsonify
import sys
import os
import logging
from datetime import datetime

# Add the parent directory to the path to import Agents modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from Agents.nodes.workflows.paraphrase_workflow import SimpleParaphraseWorkflow
except ImportError as e:
    # Try alternative import paths
    try:
        # Add current directory's parent to path
        agents_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))), 'Agents')
        if agents_path not in sys.path:
            sys.path.insert(0, agents_path)
        from nodes.workflows.paraphrase_workflow import SimpleParaphraseWorkflow
    except ImportError:
        logger.error(f"Failed to import SimpleParaphraseWorkflow: {e}")
        raise

# Create blueprint
paraphrase_bp = Blueprint('paraphrase', __name__)

# Configure logging
logger = logging.getLogger(__name__)

# Global paraphrase workflow instances (one per session)
paraphrase_workflows = {}

def get_paraphrase_workflow(session_id: str = None, api_key: str = None):
    """Get or create paraphrase workflow instance for session."""
    global paraphrase_workflows
    
    if session_id is None:
        session_id = "default"
    
    if session_id not in paraphrase_workflows:
        try:
            paraphrase_workflows[session_id] = SimpleParaphraseWorkflow(
                api_key=api_key
            )
            logger.info(f"Simple Paraphrase Workflow initialized for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Simple Paraphrase Workflow for session {session_id}: {e}")
            return None
    
    return paraphrase_workflows[session_id]

@paraphrase_bp.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint for the paraphrase service.
    
    Response:
    {
        "status": "healthy",
        "service": "paraphrase",
        "timestamp": "string"
    }
    """
    return jsonify({
        "status": "healthy",
        "service": "paraphrase",
        "timestamp": datetime.now().isoformat()
    })

@paraphrase_bp.route('/', methods=['POST'])
def paraphrase_text():
    """
    Paraphrase text with academic sources using Perplexity.
    
    Request body:
    {
        "text": "string (required)",
        "session_id": "string (optional)",
        "api_key": "string (optional)"
    }
    
    Response:
    {
        "success": true,
        "original_text": "string",
        "paraphrased_text": "string",
        "sources": "array",
        "execution_time": "number",
        "timestamp": "string",
        "workflow_id": "string",
        "model": "string",
        "agent": "string"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
    except Exception as json_error:
        logger.error(f"JSON parsing error: {str(json_error)}")
        return jsonify({"error": "Invalid JSON format"}), 400
        
    try:
        text = data.get('text')
        if not text:
            return jsonify({"error": "text is required"}), 400
        
        session_id = data.get('session_id', 'default')
        api_key = data.get('api_key')
        
        # Get paraphrase workflow
        workflow = get_paraphrase_workflow(session_id, api_key)
        if not workflow:
            return jsonify({"error": "Failed to initialize paraphrase workflow"}), 500
        
        # Process the paraphrase
        result = workflow.paraphrase(text)
        
        logger.info(f"Paraphrase completed successfully for session {session_id}: success={result.get('success')}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error paraphrasing text: {str(e)}")
        return jsonify({"error": f"Error paraphrasing text: {str(e)}"}), 500

