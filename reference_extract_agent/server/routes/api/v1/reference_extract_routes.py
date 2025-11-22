"""
Simple Reference Extract routes for API v1 - Reference extraction only.
"""

from flask import Blueprint, request, jsonify
import sys
import os
import logging
from datetime import datetime

# Add the parent directory to the path to import Agents modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from Agents.nodes.workflows.reference_extract_workflow import SimpleReferenceExtractWorkflow

# Create blueprint
reference_extract_bp = Blueprint('reference_extract', __name__)

# Configure logging
logger = logging.getLogger(__name__)

# Global reference extract workflow instances (one per session)
reference_extract_workflows = {}

def get_reference_extract_workflow(session_id: str = None, api_key: str = None):
    """Get or create reference extract workflow instance for session."""
    global reference_extract_workflows
    
    if session_id is None:
        session_id = "default"
    
    if session_id not in reference_extract_workflows:
        try:
            reference_extract_workflows[session_id] = SimpleReferenceExtractWorkflow(
                api_key=api_key
            )
            logger.info(f"Simple Reference Extract Workflow initialized for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Simple Reference Extract Workflow for session {session_id}: {e}")
            return None
    
    return reference_extract_workflows[session_id]

@reference_extract_bp.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint for the reference extract service.
    
    Response:
    {
        "status": "healthy",
        "service": "reference_extract",
        "timestamp": "string"
    }
    """
    return jsonify({
        "status": "healthy",
        "service": "reference_extract",
        "timestamp": datetime.now().isoformat()
    })

@reference_extract_bp.route('/', methods=['POST'])
def extract_references():
    """
    Extract references from the given text.
    
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
        "text": "string",
        "references": [
            {
                "id": "string",
                "full_citation": "string",
                "short_form": "string",
                "type": "string",
                "order": 1,
                "original_text": "string"
            }
        ],
        "extraction_metadata": {
            "total_references": 0,
            "extraction_confidence": 0.95,
            "detected_formats": ["APA", "MLA"],
            "processing_time": "string",
            "agent_version": "string"
        },
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
        
        # Get reference extract workflow
        workflow = get_reference_extract_workflow(session_id, api_key)
        if not workflow:
            return jsonify({"error": "Failed to initialize reference extract workflow"}), 500
        
        # Process the text
        result = workflow.process_text(text, {"context": context})
        
        logger.info(f"Text processed successfully for session {session_id}: success={result.get('success')}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        return jsonify({"error": f"Error processing text: {str(e)}"}), 500
