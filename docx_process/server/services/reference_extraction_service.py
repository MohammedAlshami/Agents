"""
Reference extraction service for DOCX processing.
Integrates with the reference extract agent to extract references from document content.
"""

import os
import sys
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


class ReferenceExtractionService:
    """Service for extracting references from document content using the reference extract agent."""
    
    def __init__(self, reference_agent_url: str = None):
        """
        Initialize reference extraction service.
        
        Args:
            reference_agent_url: URL of the reference extract agent service
        """
        self.reference_agent_url = reference_agent_url or os.getenv('REFERENCE_AGENT_URL', 'http://localhost:5003')
        logger.info(f"Reference extraction service initialized with URL: {self.reference_agent_url}")
    
    def extract_references_from_content(self, content: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        """
        Extract references from processed document content.
        
        Args:
            content: Processed document content with ordered_content
            session_id: Optional session ID for tracking
            
        Returns:
            Dictionary containing extracted references and metadata
        """
        try:
            logger.info("Starting reference extraction from document content")
            
            # Extract text content for reference extraction
            text_content = self._extract_text_for_references(content)
            
            if not text_content.strip():
                logger.warning("No text content found for reference extraction")
                return {
                    "success": True,
                    "references": [],
                    "extraction_metadata": {
                        "total_references": 0,
                        "extraction_confidence": 0.0,
                        "detected_formats": [],
                        "processing_time": "0.0s",
                        "agent_version": "1.0.0"
                    },
                    "message": "No text content found for reference extraction"
                }
            
            # Call reference extract agent
            result = self._call_reference_agent(text_content, session_id)
            
            if result.get("success"):
                logger.info(f"Successfully extracted {len(result.get('references', []))} references")
                return result
            else:
                logger.warning(f"Reference extraction failed: {result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "references": [],
                    "extraction_metadata": {},
                    "error": result.get('error', 'Reference extraction failed')
                }
                
        except Exception as e:
            logger.error(f"Error in reference extraction: {str(e)}")
            return {
                "success": False,
                "references": [],
                "extraction_metadata": {},
                "error": f"Reference extraction error: {str(e)}"
            }
    
    def _extract_text_for_references(self, content: Dict[str, Any]) -> str:
        """
        Extract text content from processed document for reference extraction.
        Focuses on paragraphs and reference sections.
        
        Args:
            content: Processed document content
            
        Returns:
            Combined text content for reference extraction
        """
        try:
            text_parts = []
            
            # Add title if exists
            if content.get("title"):
                text_parts.append(content["title"])
            
            # Extract text from ordered content
            ordered_content = content.get("ordered_content", [])
            for item in ordered_content:
                item_type = item.get("type")
                
                if item_type == "paragraph":
                    text = item.get("text", "").strip()
                    if text:
                        # Check if this looks like a reference section
                        if self._is_reference_section(text):
                            text_parts.append(f"REFERENCES SECTION: {text}")
                        else:
                            text_parts.append(text)
                
                elif item_type == "table":
                    # Extract text from table cells
                    table_data = item.get("data", {})
                    table_text = self._extract_table_text(table_data)
                    if table_text:
                        text_parts.append(table_text)
            
            # Also check footnotes for references
            footnotes = content.get("footnotes", [])
            for footnote in footnotes:
                footnote_text = footnote.get("text", "").strip()
                if footnote_text:
                    text_parts.append(f"FOOTNOTE: {footnote_text}")
            
            combined_text = "\n\n".join(text_parts)
            logger.info(f"Extracted {len(text_parts)} text parts for reference extraction")
            return combined_text
            
        except Exception as e:
            logger.error(f"Error extracting text for references: {str(e)}")
            return ""
    
    def _is_reference_section(self, text: str) -> bool:
        """
        Check if text appears to be a reference section.
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be a reference section
        """
        text_lower = text.lower().strip()
        
        # Common reference section indicators
        reference_indicators = [
            "references",
            "bibliography",
            "works cited",
            "sources",
            "citations",
            "literature cited",
            "reference list"
        ]
        
        # Check if text starts with reference indicators
        for indicator in reference_indicators:
            if text_lower.startswith(indicator):
                return True
        
        # Check if text contains reference-like patterns
        reference_patterns = [
            r"\(\d{4}\)",  # (2023)
            r"\[\d+\]",    # [1]
            r"\d+\.\s+\w+",  # 1. Author
            r"et al\.",    # et al.
            r"doi:",       # DOI
            r"http[s]?://", # URLs
            r"vol\.",      # vol.
            r"pp\.",       # pp.
            r"pp\s+\d+",   # pp 123
        ]
        
        import re
        for pattern in reference_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _extract_table_text(self, table_data: Dict[str, Any]) -> str:
        """
        Extract text content from table data.
        
        Args:
            table_data: Table data structure
            
        Returns:
            Combined text from table cells
        """
        try:
            text_parts = []
            cells = table_data.get("cells", [])
            
            for row in cells:
                row_text = []
                for cell in row:
                    cell_text = cell.get("text", "").strip()
                    if cell_text:
                        row_text.append(cell_text)
                
                if row_text:
                    text_parts.append(" | ".join(row_text))
            
            return "\n".join(text_parts)
            
        except Exception as e:
            logger.warning(f"Error extracting table text: {str(e)}")
            return ""
    
    def _call_reference_agent(self, text: str, session_id: str = None) -> Dict[str, Any]:
        """
        Call the reference extract agent API.
        
        Args:
            text: Text content to extract references from
            session_id: Optional session ID
            
        Returns:
            Response from reference extract agent
        """
        try:
            url = f"{self.reference_agent_url}/api/v1/reference-extract/"
            
            payload = {
                "text": text,
                "session_id": session_id or f"docx_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "context": "DOCX document reference extraction"
            }
            
            logger.info(f"Calling reference agent at: {url}")
            logger.info(f"Payload text length: {len(text)} characters")
            
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Reference agent response: success={result.get('success')}")
                return result
            else:
                logger.error(f"Reference agent returned status {response.status_code}: {response.text}")
                return {
                    "success": False,
                    "error": f"Reference agent returned status {response.status_code}",
                    "references": [],
                    "extraction_metadata": {}
                }
                
        except requests.exceptions.Timeout:
            logger.error("Reference agent request timed out")
            return {
                "success": False,
                "error": "Reference agent request timed out",
                "references": [],
                "extraction_metadata": {}
            }
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to reference agent")
            return {
                "success": False,
                "error": "Failed to connect to reference agent",
                "references": [],
                "extraction_metadata": {}
            }
        except Exception as e:
            logger.error(f"Error calling reference agent: {str(e)}")
            return {
                "success": False,
                "error": f"Error calling reference agent: {str(e)}",
                "references": [],
                "extraction_metadata": {}
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status of the reference extraction service.
        
        Returns:
            Dictionary with system status information
        """
        try:
            # Test connection to reference agent
            url = f"{self.reference_agent_url}/api/v1/reference-extract/"
            response = requests.get(url, timeout=5)
            
            return {
                "service": "reference_extraction",
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "reference_agent_url": self.reference_agent_url,
                "reference_agent_status": response.status_code,
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "service": "reference_extraction",
                "status": "unhealthy",
                "reference_agent_url": self.reference_agent_url,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
