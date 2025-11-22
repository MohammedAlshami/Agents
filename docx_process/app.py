"""
Presly DocX Process Server - Main Application
Handles Word document processing and conversion.
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

# Import docx processing blueprint
from server.routes.api.v1.docx_routes import docx_bp

# Register docx processing blueprint
app.register_blueprint(docx_bp, url_prefix='/api/v1/docx')

# Log registered routes for debugging
logger.info("Registered blueprints:")
for rule in app.url_map.iter_rules():
    logger.info(f"  {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")


@app.route('/')
def index():
    """Root endpoint with API information."""
    return jsonify({
        'message': 'DocX Process API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'docx': '/api/v1/docx',
            'health': '/api/v1/docx/health'
        },
        'description': 'Word document processing and conversion service'
    })


@app.route('/test')
def test():
    """Simple test endpoint for debugging."""
    return jsonify({
        'status': 'ok',
        'message': 'DocX Process server is running',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api')
def api_info():
    """API information endpoint."""
    return jsonify({
        'api_name': 'DocX Process API',
        'version': '1.0.0',
        'description': 'Word document processing and conversion service',
        'endpoints': {
            'v1': {
                'docx': '/api/v1/docx'
            }
        },
        'features': [
            'Word document (.docx) processing',
            'Content extraction and parsing',
            'TipTap JSON conversion',
            'Image extraction and conversion',
            'Table processing',
            'Metadata extraction',
            'Document structure analysis',
            'Cloudflare R2 integration'
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


@app.after_request
def log_response(response):
    """Log responses and add CORS headers."""
    origin = request.headers.get('Origin')
    logger.info(f"Response: {response.status_code} - Origin: {origin}")
    
    # Explicitly set CORS headers for API Gateway compatibility
    allowed_origins = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:3001',
        'http://localhost:3002',
        'http://127.0.0.1:3002',
        'http://10.190.42.225:3000',
        'http://10.190.42.225:3001',
        "https://www.presly.xyz",
        "https://presly.xyz"
    ]
    
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    else:
        # For API Gateway, allow all origins if not in list
        response.headers['Access-Control-Allow-Origin'] = '*'
    
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-User-ID, Accept, X-Requested-With'
    response.headers['Access-Control-Max-Age'] = '86400'
    
    return response


if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5007))
    
    # Get host from environment or use default
    host = os.environ.get('HOST', '0.0.0.0')
    
    # Get debug mode from environment
    debug = True  # Always run in debug mode
    
    logger.info(f"Starting Presly DocX Process Server on {host}:{port}")
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
