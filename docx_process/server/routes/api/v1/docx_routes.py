"""
DocX processing routes for API v1.
Single route that handles both health check and docx processing.
"""

from flask import Blueprint, request, jsonify
import sys
import os
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from functools import wraps

# Add the server directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from server.services.word_document_service import WordDocumentService
from server.services.cloudflare_download_service import cloudflare_download_service
from server.services.section_extraction_service import SectionExtractionService

# Import reference extraction workflow
from Agents.nodes.workflows.reference_extract_workflow import SimpleReferenceExtractWorkflow

# Create blueprint
docx_bp = Blueprint('docx', __name__)

# Initialize services
word_document_service = WordDocumentService()
reference_extraction_workflow = SimpleReferenceExtractWorkflow()
section_extraction_service = SectionExtractionService()

logger = logging.getLogger(__name__)


def timeout_handler(timeout_seconds=60):
    """
    Decorator to add timeout to a function.
    
    Args:
        timeout_seconds: Maximum time in seconds (default: 60)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    result = future.result(timeout=timeout_seconds)
                    return result
                except FutureTimeoutError:
                    logger.error(f"Function {func.__name__} exceeded timeout of {timeout_seconds} seconds")
                    raise TimeoutError(f"Operation exceeded {timeout_seconds} seconds timeout")
        return wrapper
    return decorator


@docx_bp.route('/', methods=['GET', 'POST', 'OPTIONS'], strict_slashes=False)
def process_docx():
    """
    Single route that handles both health check and docx processing.
    GET: Returns health status
    POST: Processes docx file and converts to TipTap JSON
    OPTIONS: Handles CORS preflight requests
    """
    if request.method == 'OPTIONS':
        # Handle CORS preflight request
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-User-ID, Accept, X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Max-Age', '86400')
        return response
    
    if request.method == 'GET':
        # Health check endpoint
        return jsonify({
            'status': 'healthy',
            'service': 'DocX Process API',
            'version': '1.0.0',
            'message': 'DocX processing service is running'
        })
    
    elif request.method == 'POST':
        # Process docx file
        # NOTE: API Gateway REST APIs have a maximum timeout of 30 seconds.
        # If processing takes longer, consider implementing async processing
        # (return job ID immediately, process in background, poll for results).
        try:
            # Debug logging
            logger.info(f"Request method: {request.method}")
            logger.info(f"Request content type: {request.content_type}")
            logger.info(f"Request headers: {dict(request.headers)}")
            
            file_content = None
            filename = None
            sections = None
            
            # Check if this is a file upload (multipart/form-data)
            if 'file' in request.files:
                logger.info("Processing direct file upload")
                uploaded_file = request.files['file']
                
                if uploaded_file.filename == '':
                    return jsonify({"error": "No file selected"}), 400
                
                if not uploaded_file.filename.lower().endswith('.docx'):
                    return jsonify({"error": "Only .docx files are supported"}), 400
                
                file_content = uploaded_file.read()
                filename = uploaded_file.filename
                
                logger.info(f"Successfully received file upload: {filename} ({len(file_content)} bytes)")
                
                # Get sections from form data if provided
                sections_str = request.form.get('sections')
                if sections_str:
                    try:
                        import json as json_lib
                        sections = json_lib.loads(sections_str)
                    except:
                        # If not JSON, try comma-separated
                        sections = [s.strip() for s in sections_str.split(',') if s.strip()]
            
            # Otherwise, check for file_url in JSON request
            elif request.is_json:
                logger.info("Processing file from URL")
                json_data = request.get_json()
                if not json_data:
                    logger.error("No JSON data provided")
                    return jsonify({"error": "JSON data is required"}), 400
                
                file_url = json_data.get('file_url')
                logger.info(f"File URL from request: {file_url}")
                
                if not file_url:
                    logger.error("No file_url provided in request")
                    return jsonify({"error": "Either 'file' (file upload) or 'file_url' (JSON) parameter is required"}), 400
                
                # Download file from the provided URL
                logger.info(f"Processing Word document from URL: {file_url}")
                
                try:
                    # Download file from the URL
                    download_result = cloudflare_download_service.download_file_for_processing(
                        file_url, "document.docx"
                    )
                    
                    logger.info(f"Download result: {download_result}")
                    
                    if not download_result["success"]:
                        logger.error(f"Download failed: {download_result.get('error')}")
                        return jsonify({"error": f"Failed to download file: {download_result.get('error')}"}), 400
                    
                    file_content = download_result["file_object"].read()
                    filename = download_result["file_name"]
                    
                    logger.info(f"Successfully downloaded file: {filename} ({len(file_content)} bytes)")
                    
                except Exception as download_error:
                    logger.error(f"Error downloading file: {str(download_error)}")
                    return jsonify({"error": f"Failed to download file: {str(download_error)}"}), 400
                
                # Get sections list from request (optional)
                sections = json_data.get('sections', None)
            else:
                return jsonify({"error": "Request must be either multipart/form-data with 'file' field or JSON with 'file_url' field"}), 400
            
            # Validate that we have file content
            if not file_content:
                return jsonify({"error": "No file content received"}), 400
            
            if not filename:
                filename = "document.docx"
            if sections and isinstance(sections, list):
                logger.info(f"Processing document with custom sections: {sections}")
            else:
                logger.info("Processing document with default sections")
            
            # Extract sections from the document using AI classification with timeout
            logger.info("Extracting sections from document using AI classification (with 60s timeout)...")
            try:
                # Wrap section extraction with timeout
                @timeout_handler(timeout_seconds=60)
                def extract_sections_with_timeout():
                    return section_extraction_service.extract_sections_from_docx(
                        file_content, 
                        filename, 
                        sections=sections
                    )
                
                section_result = extract_sections_with_timeout()
                
                # Extract references from the references section AFTER organizing content
                references = []
                try:
                    logger.info("Extracting references from references section")
                    
                    # Get references section content from extracted sections
                    extracted_sections = section_result.get("extracted_sections", {})
                    
                    # Helper function to safely get string content from section
                    def get_string_content(content):
                        """Safely extract string content, handling dict/string types."""
                        if isinstance(content, str):
                            return content
                        elif isinstance(content, dict):
                            # If it's a dict, try to extract text from it
                            # Could be a TipTap JSON structure or other format
                            if "content" in content and isinstance(content["content"], list):
                                # TipTap format - extract text from nodes
                                def extract_text_from_node(node):
                                    if isinstance(node, dict):
                                        if node.get("type") == "text" and "text" in node:
                                            return node["text"]
                                        elif "content" in node and isinstance(node["content"], list):
                                            return " ".join(extract_text_from_node(c) for c in node["content"])
                                    return ""
                                return " ".join(extract_text_from_node(node) for node in content["content"])
                            # Try to get a string representation
                            return str(content)
                        return ""
                    
                    references_content = get_string_content(extracted_sections.get("references", ""))
                    
                    logger.info(f"References section content length: {len(references_content)} characters")
                    if references_content:
                        logger.info(f"References section preview (first 200 chars): {references_content[:200]}...")
                    
                    # Check if references section contains actual references or wrong content
                    references_content_lower = references_content.lower() if references_content else ""
                    is_wrong_content = (
                        "regression" in references_content_lower or
                        "anova" in references_content_lower or
                        "coefficients" in references_content_lower or
                        "r square" in references_content_lower or
                        "f=9.048" in references_content_lower or
                        "table 4" in references_content_lower or
                        "table 5" in references_content_lower or
                        "table 6" in references_content_lower or
                        "recommendations" in references_content_lower
                    )
                    
                    # If no references section content or wrong content, try to extract from all sections first
                    if not references_content or not references_content.strip() or is_wrong_content:
                        if is_wrong_content:
                            logger.warning("References section contains wrong content (regression analysis, etc.), trying fallback...")
                        else:
                            logger.info("No references section found, extracting from all sections")
                        
                        # Try to find references in other sections - look for common reference patterns
                        text_content = ""
                        found_references_section = False
                        
                        # First, check if 'other' section contains references
                        other_content = get_string_content(extracted_sections.get("other", ""))
                        if other_content and other_content.strip():
                            # Check if 'other' section looks like references (contains citation patterns)
                            other_lower = other_content.lower()
                            has_citation_patterns = (
                                "doi:" in other_lower or
                                "http://" in other_lower or
                                "https://" in other_lower or
                                "et al." in other_lower or
                                "journal" in other_lower or
                                "vol." in other_lower or
                                "pp." in other_lower or
                                "pp " in other_lower
                            )
                            
                            if has_citation_patterns and len(other_content) > 500:
                                logger.info("Found references-like content in 'other' section, using it for extraction")
                                text_content = other_content
                                found_references_section = True
                        
                        # If not found in 'other', try all sections
                        if not found_references_section:
                            for section_key, section_content in extracted_sections.items():
                                # Skip non-string fields like 'tables' and 'other' (already checked)
                                if section_key in ["tables", "other"]:
                                    continue
                                if section_content:
                                    content_str = get_string_content(section_content)
                                    if content_str and content_str.strip():
                                        text_content += content_str + "\n\n"
                    else:
                        text_content = references_content
                    
                    logger.info(f"Final text content for reference extraction: {len(text_content)} characters")
                    if text_content:
                        logger.info(f"Text content preview (first 500 chars): {text_content[:500]}...")
                    
                    if text_content.strip():
                        # Use the reference extraction workflow (with timeout)
                        logger.info("Calling reference extraction workflow...")
                        @timeout_handler(timeout_seconds=30)
                        def extract_references_with_timeout():
                            return reference_extraction_workflow.process_text(
                                text_content, 
                                context={"context": "Word document reference extraction"}
                            )
                        
                        reference_result = extract_references_with_timeout()
                        
                        logger.info(f"Reference extraction result: success={reference_result.get('success')}, references_count={len(reference_result.get('references', []))}")
                        
                        extracted_count = len(reference_result.get("references", []))
                        
                        # If very few references extracted (less than 5), try fallback to entire document
                        if extracted_count < 5:
                            logger.warning(f"Only extracted {extracted_count} references, trying fallback to entire document...")
                            
                            # Get full document text from all sections combined
                            full_document_text = ""
                            for section_key, section_content in extracted_sections.items():
                                # Skip non-string fields like 'tables'
                                if section_key == "tables":
                                    continue
                                if section_content:
                                    content_str = get_string_content(section_content)
                                    if content_str and content_str.strip():
                                        full_document_text += content_str + "\n\n"
                            
                            # Also add "other" section if it exists
                            other_content = extracted_sections.get("other", "")
                            if other_content:
                                other_content_str = get_string_content(other_content)
                                if other_content_str and other_content_str.strip():
                                    full_document_text += other_content_str + "\n\n"
                            
                            if full_document_text and len(full_document_text) > 1000:
                                logger.info(f"Fallback: Extracting references from entire document ({len(full_document_text)} characters)...")
                                @timeout_handler(timeout_seconds=30)
                                def extract_fallback_references():
                                    return reference_extraction_workflow.process_text(
                                        full_document_text,
                                        context={"context": "Word document reference extraction (fallback from entire document)"}
                                    )
                                
                                fallback_result = extract_fallback_references()
                                
                                fallback_count = len(fallback_result.get("references", []))
                                logger.info(f"Fallback extraction result: success={fallback_result.get('success')}, references_count={fallback_count}")
                                
                                # Use fallback result if it has more references
                                if fallback_count > extracted_count:
                                    logger.info(f"Fallback extracted more references ({fallback_count} vs {extracted_count}), using fallback result")
                                    reference_result = fallback_result
                                    extracted_count = fallback_count
                                else:
                                    logger.info(f"Fallback did not extract more references ({fallback_count} vs {extracted_count}), keeping original result")
                            else:
                                logger.warning(f"Could not get full document text for fallback (length: {len(full_document_text)})")
                        
                        if reference_result.get("success") and reference_result.get("references"):
                            references = reference_result["references"]
                            logger.info(f"Successfully extracted {len(references)} references from document")
                            if len(references) > 0:
                                logger.info(f"First reference: {references[0].get('full_citation', 'N/A')[:100]}...")
                        else:
                            logger.warning(f"No references extracted from document. Result: {reference_result}")
                    else:
                        logger.warning("No text content found for reference extraction")
                        
                except Exception as e:
                    logger.error(f"Error extracting references: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    # Continue without references if extraction fails
                
                # Prepare response data with sections (matching expected output structure)
                response_data = {
                    "filename": filename,
                    "first_page_metadata": section_result.get("first_page_metadata", {}),
                    "metadata": section_result.get("metadata", {}),
                    "references": references,
                    "sections": section_result.get("sections", [])
                }
                
                return jsonify({
                    "status": "success",
                    "data": response_data,
                    "message": "Word document processed successfully with section extraction"
                })
                
            except TimeoutError as timeout_err:
                logger.error(f"Section extraction timed out after 60 seconds: {str(timeout_err)}")
                return jsonify({
                    "error": "Processing timeout",
                    "message": "Document processing exceeded 60 seconds timeout. The document may be too large or complex.",
                    "timestamp": datetime.now().isoformat()
                }), 504
            except Exception as section_error:
                logger.error(f"Error extracting sections: {str(section_error)}")
                # Fallback to original processing if section extraction fails
                logger.info("Falling back to original document processing...")
                
                # Process the Word document (fallback) with timeout
                @timeout_handler(timeout_seconds=30)
                def process_fallback():
                    return word_document_service.process_word_document(file_content, filename)
                
                processed_content = process_fallback()
                
                # Convert to TipTap JSON format
                tiptap_content = word_document_service.convert_to_document_blocks(processed_content)
                
                # Extract references from the processed content
                references = []
                try:
                    logger.info("Extracting references from document content")
                    
                    # Extract text content for reference extraction from TipTap structure
                    text_content = ""
                    
                    # First try to extract from TipTap content structure
                    if tiptap_content.get("content"):
                        logger.info(f"Processing TipTap content with {len(tiptap_content['content'])} nodes for reference extraction")
                        text_content = _extract_text_from_tiptap_content(tiptap_content["content"])
                    
                    # Fallback to ordered content if TipTap extraction fails
                    if not text_content.strip() and processed_content.get("ordered_content"):
                        logger.info(f"Fallback: Processing {len(processed_content['ordered_content'])} ordered content items for reference extraction")
                        for i, item in enumerate(processed_content["ordered_content"]):
                            logger.info(f"Item {i}: type={item.get('type')}, text_length={len(item.get('text', ''))}")
                            # Extract text from paragraph items
                            if item.get("type") == "paragraph" and item.get("text"):
                                text_content += item["text"] + "\n"
                            # Extract text from table items
                            elif item.get("type") == "table" and item.get("data", {}).get("cells"):
                                for row in item["data"]["cells"]:
                                    for cell in row:
                                        if cell.get("text"):
                                            text_content += cell["text"] + " "
                                    text_content += "\n"
                    
                    logger.info(f"Extracted text content length: {len(text_content)} characters")
                    
                    if text_content.strip():
                        # Use the reference extraction workflow
                        reference_result = reference_extraction_workflow.process_text(
                            text_content, 
                            context={"context": "Word document reference extraction"}
                        )
                        
                        if reference_result.get("success") and reference_result.get("references"):
                            references = reference_result["references"]
                            logger.info(f"Successfully extracted {len(references)} references")
                        else:
                            logger.warning("No references extracted from document")
                    else:
                        logger.warning("No text content found for reference extraction")
                        
                except Exception as e:
                    logger.error(f"Error extracting references: {str(e)}")
                    # Continue without references if extraction fails
                
                # Prepare response data (fallback)
                response_data = {
                    "processed_content": processed_content,
                    "tiptap_content": tiptap_content,
                    "references": references,
                    "filename": filename,
                    "sections": []  # Empty sections if extraction failed
                }
                
                return jsonify({
                    "status": "success",
                    "data": response_data,
                    "message": "Word document processed successfully (fallback mode - section extraction failed)"
                })
            
        except Exception as e:
            logger.error(f"Failed to process Word document: {str(e)}")
            return jsonify({"error": f"Failed to process Word document: {str(e)}"}), 500


def _extract_text_from_tiptap_content(content_nodes):
    """Extract plain text from TipTap content nodes recursively."""
    text_content = ""
    
    try:
        for node in content_nodes:
            if node.get("type") == "text":
                text_content += node.get("text", "") + " "
            elif node.get("type") == "paragraph":
                if node.get("content"):
                    text_content += _extract_text_from_tiptap_content(node["content"]) + "\n"
            elif node.get("type") == "heading":
                if node.get("content"):
                    text_content += _extract_text_from_tiptap_content(node["content"]) + "\n"
            elif node.get("type") == "table":
                if node.get("content"):
                    for row in node["content"]:
                        if row.get("type") == "tableRow" and row.get("content"):
                            for cell in row["content"]:
                                if cell.get("type") == "tableCell" and cell.get("content"):
                                    text_content += _extract_text_from_tiptap_content(cell["content"]) + " "
                            text_content += "\n"
            elif node.get("type") == "bulletList":
                if node.get("content"):
                    for item in node["content"]:
                        if item.get("type") == "listItem" and item.get("content"):
                            text_content += _extract_text_from_tiptap_content(item["content"]) + "\n"
            elif node.get("content"):
                # Recursively process nested content
                text_content += _extract_text_from_tiptap_content(node["content"])
    
    except Exception as e:
        logger.warning(f"Error extracting text from TipTap content: {str(e)}")
    
    return text_content


@docx_bp.route('/health', methods=['GET', 'OPTIONS'], strict_slashes=False)
def health_check():
    """Dedicated health check endpoint."""
    if request.method == 'OPTIONS':
        # Handle CORS preflight request
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-User-ID, Accept, X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Max-Age', '86400')
        return response
    
    return jsonify({
        'status': 'healthy',
        'service': 'DocX Process API',
        'version': '1.0.0',
        'message': 'DocX processing service is running'
    })
