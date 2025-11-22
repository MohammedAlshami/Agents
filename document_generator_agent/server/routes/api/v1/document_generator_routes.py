"""
Document Generator routes for API v1 - Mock implementation for project creation and document generation.
"""

from flask import Blueprint, request, jsonify
import sys
import os
import logging
from datetime import datetime
import uuid

# Create blueprint
document_generator_bp = Blueprint('document_generator', __name__)

# Configure logging
logger = logging.getLogger(__name__)

# Try to import project model from main server (will work when running through unified server)
PROJECT_MODEL_AVAILABLE = False
ProjectModel = None
ProjectCreateRequest = None
get_shared_mongodb_manager = None

def _try_import_project_model():
    """Try to import project model from main server."""
    global PROJECT_MODEL_AVAILABLE, ProjectModel, ProjectCreateRequest, get_shared_mongodb_manager
    
    try:
        # Try to find main server path relative to current file
        current_file = os.path.abspath(__file__)
        # Go up from: document_generator_agent/server/routes/api/v1/document_generator_routes.py
        # To: servers/
        servers_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))))
        main_server_path = os.path.join(servers_dir, 'main')
        
        # Add main server path if it exists and not already in path
        if os.path.exists(main_server_path) and main_server_path not in sys.path:
            sys.path.insert(0, main_server_path)
            logger.info(f"Added main server path to sys.path: {main_server_path}")
        
        # Try importing
        from server.services.shared_services import get_shared_mongodb_manager
        from server.models.project_models import ProjectModel
        from server.schemas.project_schemas import ProjectCreateRequest
        
        PROJECT_MODEL_AVAILABLE = True
        logger.info("Project model imported successfully from main server")
        return True
    except ImportError as e:
        PROJECT_MODEL_AVAILABLE = False
        logger.warning(f"Project model not available - document generator will use mock responses only: {e}")
        return False

# Try to import on module load
_try_import_project_model()


@document_generator_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for the document generator service.
    
    Response:
    {
        "status": "healthy",
        "service": "document_generator",
        "timestamp": "string"
    }
    """
    return jsonify({
        "status": "healthy",
        "service": "document_generator",
        "timestamp": datetime.now().isoformat()
    })


def get_user_email():
    """Get user email from request headers or use default for development."""
    user_email = request.headers.get('X-User-Email')
    if not user_email:
        user_id = request.headers.get('X-User-Id')
        if user_id and user_id != 'default_user':
            if '@' in user_id:
                user_email = user_id
            else:
                user_email = 'default_user'
        else:
            user_email = 'default_user'
    return user_email


@document_generator_bp.route('/generate', methods=['POST'])
def generate_document():
    """
    Generate a document project - creates project in database and returns it.
    
    Request body:
    {
        "title": "string (required)",
        "description": "string (optional)",
        "company": "string (required)",
        "document_type": "string (optional: general, research_paper, article_paper)",
        "metadata": {
            "document_creation_method": "string (empty or ai_writing)",
            "sections": [
                {
                    "id": "string",
                    "title": "string",
                    "description": "string",
                    "order": "number",
                    "required": "boolean",
                    "content_type": "string"
                }
            ],
            "ai_writing_config": {
                "word_count": "number",
                "academic_sources": ["string"],
                "writing_style": "string"
            },
            "document_prompt": "string",
            "selected_focus": "object"
        },
        "takeover_document_type": "string (optional)",
        "facilitator": "string (optional)"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "project_id": "string",
            "title": "string",
            ...
        },
        "message": "Project created successfully",
        "timestamp": "string"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        if not data.get('title'):
            return jsonify({"error": "title is required"}), 400
        if not data.get('company'):
            return jsonify({"error": "company is required"}), 400
        
        user_email = get_user_email()
        
        # Try to import project model if not already available
        if not PROJECT_MODEL_AVAILABLE:
            _try_import_project_model()
        
        # Try to create project in database if project model is available
        if PROJECT_MODEL_AVAILABLE and get_shared_mongodb_manager and ProjectModel and ProjectCreateRequest:
            try:
                db_manager = get_shared_mongodb_manager()
                project_model = ProjectModel(db_manager)
                
                # Validate request data
                project_request = ProjectCreateRequest(**data)
                
                # Create project in database
                project_id = project_model.create_project(project_request, user_email)
                
                # Get the created project
                project = project_model.get_project_by_id(project_id, user_email)
                
                if project:
                    logger.info(f"Project created via document generator: {project_id} - {data.get('title')}")
                    # Convert to dict - sections should already be preserved by project model
                    project_dict = project.model_dump()
                    
                    # Double-check that sections are in metadata (they should be from create_project)
                    if 'metadata' in data and 'sections' in data['metadata']:
                        sections_count = len(data['metadata']['sections'])
                        logger.info(f"Request contains {sections_count} sections in metadata")
                        if 'metadata' not in project_dict:
                            project_dict['metadata'] = {}
                        if 'sections' not in project_dict.get('metadata', {}) or len(project_dict.get('metadata', {}).get('sections', [])) == 0:
                            # If sections weren't preserved, add them now
                            project_dict['metadata']['sections'] = data['metadata']['sections']
                            logger.info(f"Added {sections_count} sections to project metadata")
                        else:
                            logger.info(f"Project already has {len(project_dict.get('metadata', {}).get('sections', []))} sections in metadata")
                    
                    return jsonify({
                        "success": True,
                        "data": project_dict,
                        "message": "Project created successfully",
                        "timestamp": datetime.now().isoformat()
                    }), 201
            except Exception as db_error:
                logger.warning(f"Failed to create project in database: {str(db_error)}, falling back to mock")
                import traceback
                logger.error(traceback.format_exc())
                # Fall through to mock implementation
        
        # Fallback to mock implementation if database is not available
        project_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        project_data = {
            "project_id": project_id,
            "title": data.get('title', ''),
            "description": data.get('description', ''),
            "company": data.get('company', ''),
            "document_type": data.get('document_type'),
            "takeover_document_type": data.get('takeover_document_type'),
            "facilitator": data.get('facilitator'),
            "acquiring_company": data.get('acquiring_company'),
            "offeror_company": data.get('offeror_company'),
            "number_of_shares": data.get('number_of_shares'),
            "share_price": data.get('share_price'),
            "metadata": data.get('metadata', {}),
            "academic_metadata": data.get('academic_metadata'),
            "variables": data.get('variables', []),
            "created_at": now,
            "updated_at": now,
            "owner_id": user_email,
            "files": [],
            "questions": []
        }
        
        # Ensure sections are preserved in metadata
        if 'metadata' in data and 'sections' in data['metadata']:
            project_data['metadata']['sections'] = data['metadata']['sections']
        
        logger.info(f"Mock project created: {project_id} - {data.get('title')}")
        
        return jsonify({
            "success": True,
            "data": project_data,
            "message": "Project created successfully",
            "timestamp": now
        }), 201
        
    except Exception as e:
        logger.error(f"Error generating document: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Error generating document",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

