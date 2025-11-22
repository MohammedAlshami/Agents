"""
Simple Humanize routes for API v1 - Text humanization only.
"""

from flask import Blueprint, request, jsonify
import sys
import os
import logging
from datetime import datetime

# Add the parent directory to the path to import Agents modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from Agents.nodes.workflows.humanize_workflow import SimpleHumanizeWorkflow

# Create blueprint
humanize_bp = Blueprint('humanize', __name__)

# Configure logging
logger = logging.getLogger(__name__)

# Global humanize workflow instances (one per session)
humanize_workflows = {}

def get_humanize_workflow(session_id: str = None, api_key: str = None):
    """Get or create humanize workflow instance for session."""
    global humanize_workflows
    
    if session_id is None:
        session_id = "default"
    
    if session_id not in humanize_workflows:
        try:
            humanize_workflows[session_id] = SimpleHumanizeWorkflow(
                api_key=api_key
            )
            logger.info(f"Simple Humanize Workflow initialized for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Simple Humanize Workflow for session {session_id}: {e}")
            return None
    
    return humanize_workflows[session_id]

@humanize_bp.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint for the humanize service.
    
    Response:
    {
        "status": "healthy",
        "service": "humanize",
        "timestamp": "string"
    }
    """
    return jsonify({
        "status": "healthy",
        "service": "humanize",
        "timestamp": datetime.now().isoformat()
    })

@humanize_bp.route('/', methods=['POST'])
def humanize_text():
    """
    Humanize text to make it sound more natural and human-like.
    
    Request body:
    {
        "text": "string",
        "session_id": "string (optional)",
        "api_key": "string (optional)",
        "context": "string (optional)"
    }
    
    Response:
    {
        "success": true,
        "original_text": "string",
        "humanized_text": "string",
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
        context = data.get('context', '')
        
        # Get humanize workflow
        workflow = get_humanize_workflow(session_id, api_key)
        if not workflow:
            return jsonify({"error": "Failed to initialize humanize workflow"}), 500
        
        # Process the text
        result = workflow.process_text(text, {"context": context})
        
        logger.info(f"Text processed successfully for session {session_id}: success={result.get('success')}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        return jsonify({"error": f"Error processing text: {str(e)}"}), 500
