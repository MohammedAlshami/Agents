"""
Reference Search routes for API v1 - Reference search and gathering only.
"""

from flask import Blueprint, request, jsonify
import sys
import os
import logging
from datetime import datetime

# Add the parent directory to the path to import Agents modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from Agents.nodes.workflows.reference_search_workflow import SimpleReferenceSearchWorkflow

# Create blueprint
reference_search_bp = Blueprint('reference_search', __name__)

# Configure logging
logger = logging.getLogger(__name__)

# Global reference search workflow instances (one per session)
reference_search_workflows = {}

def get_reference_search_workflow(session_id: str = None, api_key: str = None, openalex_email: str = None):
    """Get or create reference search workflow instance for session."""
    global reference_search_workflows
    
    if session_id is None:
        session_id = "default"
    
    if session_id not in reference_search_workflows:
        try:
            reference_search_workflows[session_id] = SimpleReferenceSearchWorkflow(
                api_key=api_key,
                openalex_email=openalex_email
            )
            logger.info(f"Simple Reference Search Workflow initialized for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Simple Reference Search Workflow for session {session_id}: {e}")
            return None
    
    return reference_search_workflows[session_id]

@reference_search_bp.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint for the reference search service.
    
    Response:
    {
        "status": "healthy",
        "service": "reference_search",
        "timestamp": "string"
    }
    """
    return jsonify({
        "status": "healthy",
        "service": "reference_search",
        "timestamp": datetime.now().isoformat()
    })

@reference_search_bp.route('/', methods=['POST'])
def search_references():
    """
    Search for academic references using OpenAlex.
    
    Request body:
    {
        "title": "string",
        "problem_statement": "string",
        "num_references": "number",
        "q_rating": "string (q1, q2, q3, q4)",
        "session_id": "string (optional)",
        "api_key": "string (optional)",
        "openalex_email": "string (optional)"
    }
    
    Response:
    {
        "success": true,
        "references": "array",
        "metadata": "object",
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
        title = data.get('title')
        problem_statement = data.get('problem_statement')
        if not title or not problem_statement:
            return jsonify({"error": "title and problem_statement are required"}), 400
        
        num_references = data.get('num_references', 20)
        q_rating = data.get('q_rating', 'q1')
        session_id = data.get('session_id', 'default')
        api_key = data.get('api_key')
        openalex_email = data.get('openalex_email')
        
        # Get reference search workflow
        workflow = get_reference_search_workflow(session_id, api_key, openalex_email)
        if not workflow:
            return jsonify({"error": "Failed to initialize reference search workflow"}), 500
        
        # Process the reference search
        result = workflow.search_references(
            title=title,
            problem_statement=problem_statement,
            num_references=num_references,
            q_rating=q_rating
        )
        
        logger.info(f"Reference search completed successfully for session {session_id}: success={result.get('success')}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error searching references: {str(e)}")
        return jsonify({"error": f"Error searching references: {str(e)}"}), 500

@reference_search_bp.route('/queries', methods=['POST'])
def generate_search_queries():
    """
    Generate search queries for academic references.
    
    Request body:
    {
        "title": "string",
        "problem_statement": "string",
        "num_references": "number",
        "session_id": "string (optional)",
        "api_key": "string (optional)"
    }
    
    Response:
    {
        "success": true,
        "queries": "array",
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
        title = data.get('title')
        problem_statement = data.get('problem_statement')
        if not title or not problem_statement:
            return jsonify({"error": "title and problem_statement are required"}), 400
        
        num_references = data.get('num_references', 20)
        session_id = data.get('session_id', 'default')
        api_key = data.get('api_key')
        
        # Get reference search workflow
        workflow = get_reference_search_workflow(session_id, api_key)
        if not workflow:
            return jsonify({"error": "Failed to initialize reference search workflow"}), 500
        
        # Generate search queries
        result = workflow.generate_search_queries(
            title=title,
            problem_statement=problem_statement,
            num_references=num_references
        )
        
        logger.info(f"Search queries generated successfully for session {session_id}: success={result.get('success')}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error generating search queries: {str(e)}")
        return jsonify({"error": f"Error generating search queries: {str(e)}"}), 500
