"""
Conversation routes for API v1 - Handles greetings, questions, and conversational responses.
"""

from flask import Blueprint, request, jsonify
import sys
import os
import logging
from datetime import datetime

# Add the parent directory to the path to import Agents modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from Agents.nodes.nodes.ai.conversation_agent import ConversationAgent

# Create blueprint
conversation_bp = Blueprint('conversation', __name__)

# Configure logging
logger = logging.getLogger(__name__)

# Global agent instances (one per session)
conversation_agents = {}

def get_conversation_agent(session_id: str = None, api_key: str = None):
    """Get or create conversation agent instance for session."""
    global conversation_agents
    
    if session_id is None:
        session_id = "default"
    
    if session_id not in conversation_agents:
        try:
            conversation_agents[session_id] = ConversationAgent(
                api_key=api_key
            )
            logger.info(f"Conversation Agent initialized for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Conversation Agent for session {session_id}: {e}")
            return None
    
    return conversation_agents[session_id]

@conversation_bp.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint for the conversation service.
    
    Response:
    {
        "status": "healthy",
        "service": "conversation",
        "timestamp": "string"
    }
    """
    return jsonify({
        "status": "healthy",
        "service": "conversation",
        "timestamp": datetime.now().isoformat()
    })

@conversation_bp.route('/', methods=['POST'])
def respond():
    """
    Handle conversational messages (greetings, questions, etc.).
    
    Request body:
    {
        "message": "string (required)",
        "context": "string (optional - document context)",
        "session_id": "string (optional)",
        "api_key": "string (optional)"
    }
    
    Response:
    {
        "success": true,
        "message": "string",
        "response": "string",
        "timestamp": "string",
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
        message = data.get('message')
        context = data.get('context', '')
        session_id = data.get('session_id', 'default')
        api_key = data.get('api_key')
        
        if not message:
            return jsonify({"error": "message is required"}), 400
        
        # Get conversation agent
        agent = get_conversation_agent(session_id, api_key)
        if not agent:
            return jsonify({"error": "Failed to initialize conversation agent"}), 500
        
        # Process the message
        result = agent.respond(
            message=message,
            context=context
        )
        
        logger.info(f"Conversation response generated for session {session_id}: success={result.get('success')}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing conversation request: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat()
        }), 500







