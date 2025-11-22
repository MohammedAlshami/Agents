"""
Presly Conversation Agent Server - Main Application
Handles greetings, questions, and conversational responses naturally.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
def setup_logging():
    """Setup logging configuration that works in both local and Lambda environments."""
    # Check if we're running in AWS Lambda
    is_lambda = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None
    
    # Use only console logging for Lambda compatibility
    handlers = [logging.StreamHandler()]
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

# Initialize logging
setup_logging()

logger = logging.getLogger(__name__)

# Create Flask app with static folder configuration
app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static')

# Configure app to prevent redirect loops in Lambda
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# CRITICAL: Disable strict slashes to prevent redirect loops in Lambda
app.url_map.strict_slashes = False

# Configure CORS with more comprehensive settings
CORS(app, 
     origins=[
         'http://localhost:3000', 
         'http://127.0.0.1:3000', 
         'http://localhost:3001', 
         'http://localhost:3002', 
         'http://127.0.0.1:3002', 
         'http://10.190.42.225:3000',
         'http://10.190.42.225:3001',
         "https://www.presly.xyz"
     ], 
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-User-ID', 'Accept'],
     supports_credentials=True,
     max_age=86400)  # Cache preflight requests for 24 hours

# Import conversation blueprint
from server.routes.api.v1.conversation_routes import conversation_bp

# Register conversation blueprint
app.register_blueprint(conversation_bp, url_prefix='/api/v1/conversation')

# Log registered routes for debugging
logger.info("Registered blueprints:")
for rule in app.url_map.iter_rules():
    logger.info(f"  {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")


@app.route('/')
def index():
    """Root endpoint with API information."""
    return jsonify({
        'message': 'Conversation Agent API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'conversation': '/api/v1/conversation',
            'health': '/api/v1/conversation'
        },
        'description': 'Conversation agent for handling greetings, questions, and conversational responses'
    })


@app.route('/test')
def test():
    """Simple test endpoint for debugging."""
    return jsonify({
        'status': 'ok',
        'message': 'Conversation Agent Server is running',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5020))
    
    # Get host from environment or use default
    host = os.environ.get('HOST', '0.0.0.0')
    
    # Get debug mode from environment
    debug = True  # Always run in debug mode
    
    logger.info(f"Starting Presly Conversation Agent Server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete")







