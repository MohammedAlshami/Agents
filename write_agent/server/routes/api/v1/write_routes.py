"""
Simple Write routes for API v1 - Text generation from topics/prompts only.
"""

from flask import Blueprint, request, jsonify
import sys
import os
import logging
from datetime import datetime

# Add the parent directory to the path to import Agents modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from Agents.nodes.workflows.write_workflow import SimpleWriteWorkflow
from Agents.nodes.workflows.text_operations_workflow import TextOperationsWorkflow

# Create blueprint
write_bp = Blueprint('write', __name__)

# Configure logging
logger = logging.getLogger(__name__)

# Global workflow instances (one per session)
write_workflows = {}
text_operations_workflows = {}

def get_write_workflow(session_id: str = None, api_key: str = None):
    """Get or create write workflow instance for session."""
    global write_workflows
    
    if session_id is None:
        session_id = "default"
    
    if session_id not in write_workflows:
        try:
            write_workflows[session_id] = SimpleWriteWorkflow(
                api_key=api_key
            )
            logger.info(f"Simple Write Workflow initialized for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Simple Write Workflow for session {session_id}: {e}")
            return None
    
    return write_workflows[session_id]

def get_text_operations_workflow(session_id: str = None, api_key: str = None):
    """Get or create text operations workflow instance for session."""
    global text_operations_workflows
    
    if session_id is None:
        session_id = "default"
    
    if session_id not in text_operations_workflows:
        try:
            text_operations_workflows[session_id] = TextOperationsWorkflow(
                api_key=api_key
            )
            logger.info(f"Text Operations Workflow initialized for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Text Operations Workflow for session {session_id}: {e}")
            return None
    
    return text_operations_workflows[session_id]

@write_bp.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint for the write service.
    
    Response:
    {
        "status": "healthy",
        "service": "write",
        "timestamp": "string"
    }
    """
    return jsonify({
        "status": "healthy",
        "service": "write",
        "timestamp": datetime.now().isoformat()
    })

@write_bp.route('/', methods=['POST'])
def generate_text():
    """
    Generate text content from a topic or prompt, or perform text operations.
    
    Request body for text generation:
    {
        "topic": "string (required for generation)",
        "writing_style": "string (optional, default: 'academic')",
        "word_count": "integer (optional)",
        "context": "string (optional)",
        "session_id": "string (optional)",
        "api_key": "string (optional)"
    }
    
    Request body for text operations:
    {
        "operation": "string (required: improve_transitions, continue_writing, make_formal, make_shorter, make_longer, fix_grammar_spelling)",
        "text": "string (required for operations)",
        "target_length": "integer (optional, for make_shorter/make_longer)",
        "context": "string (optional)",
        "session_id": "string (optional)",
        "api_key": "string (optional)"
    }
    
    Response:
    {
        "success": true,
        "operation": "string (if operation was specified)",
        "topic": "string (if topic was specified)",
        "generated_text": "string (or improved_text, continuation, formal_text, condensed_text, expanded_text, corrected_text)",
        "writing_style": "string",
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
        operation = data.get('operation')
        text = data.get('text')
        topic = data.get('topic')
        session_id = data.get('session_id', 'default')
        api_key = data.get('api_key')
        context = data.get('context', '')
        target_length = data.get('target_length')
        
        # If operation is specified, route to text operations workflow
        if operation:
            valid_operations = [
                'improve_transitions',
                'continue_writing',
                'make_formal',
                'make_shorter',
                'make_longer',
                'fix_grammar_spelling'
            ]
            
            if operation.lower() not in valid_operations:
                return jsonify({
                    "error": f"Invalid operation. Must be one of: {', '.join(valid_operations)}"
                }), 400
            
            if not text:
                return jsonify({"error": "text is required for operations"}), 400
            
            # Get text operations workflow
            workflow = get_text_operations_workflow(session_id, api_key)
            if not workflow:
                return jsonify({"error": "Failed to initialize text operations workflow"}), 500
            
            # Process the operation
            result = workflow.process_operation(
                operation=operation.lower(),
                text=text,
                target_length=target_length,
                context=context
            )
            
            logger.info(f"Operation {operation} completed for session {session_id}: success={result.get('success')}")
            return jsonify(result)
        
        # Otherwise, route to write workflow for text generation
        else:
            if not topic:
                return jsonify({"error": "topic is required for text generation"}), 400
            
            writing_style = data.get('writing_style', 'academic')
            word_count = data.get('word_count')
            
            # Validate writing style
            valid_styles = ['academic', 'technical', 'analytical', 'comparative', 'descriptive', 'argumentative']
            if writing_style.lower() not in valid_styles:
                return jsonify({"error": f"Invalid writing_style. Must be one of: {', '.join(valid_styles)}"}), 400
            
            # Get write workflow
            workflow = get_write_workflow(session_id, api_key)
            if not workflow:
                return jsonify({"error": "Failed to initialize write workflow"}), 500
            
            # Process the topic
            result = workflow.process_topic(
                topic=topic,
                writing_style=writing_style.lower(),
                word_count=word_count,
                context={"context": context} if context else None
            )
            
            logger.info(f"Text generated successfully for session {session_id}: success={result.get('success')}")
            return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": f"Error processing request: {str(e)}"}), 500

