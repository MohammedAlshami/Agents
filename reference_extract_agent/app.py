"""
Presly Reference Extract Agent Server - Main Application
Reorganized with structured architecture using blueprints and API versioning.
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

# Import reference extract blueprint
from server.routes.api.v1.reference_extract_routes import reference_extract_bp

# Register reference extract blueprint
app.register_blueprint(reference_extract_bp, url_prefix='/api/v1/reference-extract')

# Log registered routes for debugging
logger.info("Registered blueprints:")
for rule in app.url_map.iter_rules():
    logger.info(f"  {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")


@app.route('/')
def index():
    """Root endpoint with API information."""
    return jsonify({
        'message': 'Reference Extract Agent API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'reference_extract': '/api/v1/reference-extract',
            'health': '/api/v1/reference-extract'
        },
        'description': 'Simple reference extract agent for extracting and structuring references from text'
    })


@app.route('/test')
def test():
    """Simple test endpoint for debugging."""
    return jsonify({
        'status': 'ok',
        'message': 'Backend is running',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api')
def api_info():
    """API information endpoint."""
    return jsonify({
        'api_name': 'Reference Extract Agent API',
        'version': '1.0.0',
        'description': 'Simple reference extract agent for extracting and structuring references from text',
        'endpoints': {
            'v1': {
                'reference_extract': '/api/v1/reference-extract'
            }
        },
        'features': [
            'Reference extraction using OpenAI GPT-4o-mini',
            'Citation format detection (APA, MLA, Chicago)',
            'Academic reference parsing',
            'URL and web link extraction',
            'Book and journal reference extraction',
            'Simple GET/POST endpoints',
            'Health check endpoint',
            'Status monitoring'
        ]
    })




@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'timestamp': datetime.now().isoformat(),
        'path': request.path
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'timestamp': datetime.now().isoformat()
    }), 500


@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'timestamp': datetime.now().isoformat()
    }), 500


@app.before_request
def log_request():
    """Log incoming requests."""
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        # Allow localhost and IP-based origins
        origin = request.headers.get('Origin')
        allowed_origins = [
            'http://localhost:3000', 
            'http://localhost:3001', 
            'http://127.0.0.1:3000',
            'http://127.0.0.1:3001',
            'http://10.190.42.225:3000',
            'http://10.190.42.225:3001'
        ]
        if origin in allowed_origins:
            response.headers.add('Access-Control-Allow-Origin', origin)
        else:
            response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-User-ID, Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Max-Age', '86400')
        return response


@app.after_request
def log_response(response):
    """Log outgoing responses."""
    logger.info(f"Response: {response.status_code}")
    return response


if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5003))
    
    # Get host from environment or use default
    host = os.environ.get('HOST', '0.0.0.0')
    
    # Get debug mode from environment
    debug = True  # Always run in debug mode
    
    logger.info(f"Starting Presly Reference Extract Agent Server on {host}:{port}")
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
