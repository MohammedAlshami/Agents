"""
Reference Extract Agent for extracting and structuring references from text.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import openai
from openai import OpenAI

logger = logging.getLogger(__name__)


class ReferenceExtractAgent:
    """
    Agent for extracting and structuring references from text.
    
    This agent uses OpenAI to intelligently parse text and extract references
    in various formats (APA, MLA, Chicago, URLs, etc.) and return structured JSON.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Reference Extract Agent.
        
        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key
        
        # Initialize OpenAI client
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            # Try to get from environment
            import os
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                raise ValueError("OpenAI API key not provided")
    
    def extract_references(self, text: str) -> Dict[str, Any]:
        """
        Extract references from the given text.
        
        Args:
            text: The text to extract references from
            
        Returns:
            Dict containing extracted references and metadata
        """
        try:
            logger.info(f"Extracting references from text: {text[:100]}...")
            
            # Create the system prompt for reference extraction
            system_prompt = self._get_system_prompt()
            
            # Create the user prompt
            user_prompt = f"""
Please extract all references from the following text and return them in a structured JSON format.

Text to analyze:
{text}

Return a JSON object with the following structure:
{{
    "references": [
        {{
            "id": "unique_reference_id",
            "full_citation": "Complete reference in proper format",
            "short_form": "Author, Year format (e.g., 'Smith, 2024')",
            "type": "academic|url|book|journal|other",
            "order": 1,
            "original_text": "The text that was identified as a reference"
        }}
    ],
    "extraction_metadata": {{
        "total_references": 0,
        "extraction_confidence": 0.95,
        "detected_formats": ["APA", "MLA"],
        "processing_time": "2024-01-01T00:00:00Z"
    }}
}}

Guidelines:
1. Extract ALL references, including URLs, academic citations, books, journals, etc.
2. For academic citations, try to identify the format (APA, MLA, Chicago, etc.)
3. Generate a unique ID for each reference
4. Create a short form citation in "Author, Year" format
5. Maintain the original text that was identified as a reference
6. Order references in the order they appear in the text
7. If you can't determine the format, use "other" as the type
8. Be confident in your extraction - set confidence to 0.95 or higher if you're sure
"""
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=2000
            )
            
            # Parse the response
            response_content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            try:
                # Look for JSON in the response
                if "```json" in response_content:
                    json_start = response_content.find("```json") + 7
                    json_end = response_content.find("```", json_start)
                    json_str = response_content[json_start:json_end].strip()
                elif "```" in response_content:
                    json_start = response_content.find("```") + 3
                    json_end = response_content.find("```", json_start)
                    json_str = response_content[json_start:json_end].strip()
                else:
                    # Try to find JSON object in the response
                    json_start = response_content.find("{")
                    json_end = response_content.rfind("}") + 1
                    json_str = response_content[json_start:json_end]
                
                result = json.loads(json_str)
                
                # Validate the result structure
                if "references" not in result:
                    raise ValueError("No references found in response")
                
                # Add processing metadata
                result["extraction_metadata"]["processing_time"] = datetime.now().isoformat()
                result["extraction_metadata"]["agent_version"] = "1.0.0"
                
                logger.info(f"Successfully extracted {len(result['references'])} references")
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from response: {e}")
                logger.error(f"Response content: {response_content}")
                
                # Return a fallback response
                return {
                    "references": [],
                    "extraction_metadata": {
                        "total_references": 0,
                        "extraction_confidence": 0.0,
                        "detected_formats": [],
                        "processing_time": datetime.now().isoformat(),
                        "error": f"JSON parsing failed: {str(e)}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error extracting references: {str(e)}")
            return {
                "references": [],
                "extraction_metadata": {
                    "total_references": 0,
                    "extraction_confidence": 0.0,
                    "detected_formats": [],
                    "processing_time": datetime.now().isoformat(),
                    "error": str(e)
                }
            }
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for reference extraction."""
        return """You are an expert reference extraction agent. Your task is to identify and extract all references from academic and non-academic text.

You should be able to identify:
1. Academic citations in various formats (APA, MLA, Chicago, etc.)
2. URLs and web links
3. Book references
4. Journal articles
5. Conference papers
6. Reports and documents
7. Any other type of reference

For each reference, you should:
- Extract the complete citation
- Identify the reference type
- Create a short form citation (Author, Year format)
- Generate a unique ID
- Preserve the original text that was identified

Be thorough and accurate in your extraction. If you're unsure about a reference, include it but mark the confidence appropriately."""
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the system status of the reference extract agent."""
        return {
            "agent_type": "reference_extract",
            "version": "1.0.0",
            "api_configured": bool(self.api_key),
            "project_id": self.project_id,
            "user_id": self.user_id,
            "supported_formats": ["APA", "MLA", "Chicago", "URL", "Book", "Journal", "Other"],
            "status": "ready"
        }
