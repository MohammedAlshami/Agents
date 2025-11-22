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
Please extract ALL references from the following text and return them in a structured JSON format.

CRITICAL: You MUST extract EVERY single reference in the text. Do not skip any references. If there are 26 references, extract all 26. If there are 50 references, extract all 50.

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
1. Extract ALL references - this is critical. Do not miss any references.
2. Count the references first to ensure you extract them all.
3. For academic citations, try to identify the format (APA, MLA, Chicago, etc.)
4. Generate a unique ID for each reference (e.g., "ref_1", "ref_2", etc.)
5. Create a short form citation in "Author, Year" format
6. Maintain the original text that was identified as a reference
7. Order references in the order they appear in the text (order: 1, 2, 3, etc.)
8. If you can't determine the format, use "other" as the type
9. Be confident in your extraction - set confidence to 0.95 or higher if you're sure
10. Make sure the "total_references" in extraction_metadata matches the actual number of references extracted
"""
            
            # Estimate token count needed (roughly 200-300 tokens per reference)
            # For 26 references, we need at least 26 * 200 = 5200 tokens for output
            # Plus input tokens, so we need at least 16000 tokens total
            # gpt-4o-mini has a max output of 16384 tokens, so we cap at that
            estimated_output_tokens = 200 * 30  # Assume up to 30 references at 200 tokens each = 6000 tokens
            max_tokens_needed = min(16384, max(16000, estimated_output_tokens))
            
            logger.info(f"Extracting references with max_tokens={max_tokens_needed}, text_length={len(text)} characters")
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=max_tokens_needed  # Increased token limit for large documents with many references
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
                
                # If JSON is truncated, try to fix it
                if json_str and not json_str.strip().endswith('}'):
                    logger.warning("JSON response appears truncated, attempting to fix...")
                    # Try to find the last complete reference
                    last_complete_ref = json_str.rfind('},')
                    if last_complete_ref > 0:
                        # Find the closing bracket for the references array
                        json_str = json_str[:last_complete_ref + 1] + ']'
                        # Try to add the closing brace for the root object
                        if '"extraction_metadata"' in json_str:
                            # Find where extraction_metadata starts
                            metadata_start = json_str.find('"extraction_metadata"')
                            if metadata_start > 0:
                                # Find the last complete metadata field
                                last_comma = json_str.rfind(',', 0, metadata_start)
                                if last_comma > 0:
                                    # Try to complete the metadata object
                                    json_str = json_str[:last_complete_ref + 1] + '], "extraction_metadata": {}}'
                        else:
                            json_str = json_str[:last_complete_ref + 1] + '], "extraction_metadata": {}}'
                    else:
                        # If no complete references, return empty array
                        logger.warning("No complete references found in truncated JSON")
                        json_str = '{"references": []}'
                
                result = json.loads(json_str)
                
                # Validate the result structure
                if "references" not in result:
                    raise ValueError("No references found in response")
                
                # Validate that total_references matches actual count
                actual_count = len(result.get("references", []))
                metadata_count = result.get("extraction_metadata", {}).get("total_references", 0)
                
                if metadata_count != actual_count:
                    logger.warning(f"Reference count mismatch: metadata says {metadata_count}, but actual count is {actual_count}. Updating metadata.")
                    result["extraction_metadata"]["total_references"] = actual_count
                
                # Add processing metadata
                if "extraction_metadata" not in result:
                    result["extraction_metadata"] = {}
                result["extraction_metadata"]["processing_time"] = datetime.now().isoformat()
                result["extraction_metadata"]["agent_version"] = "1.0.0"
                result["extraction_metadata"]["total_references"] = actual_count
                
                logger.info(f"Successfully extracted {actual_count} references (metadata count: {metadata_count})")
                
                # Log warning if we got very few references (might indicate truncation)
                if actual_count < 5 and len(text) > 5000:
                    logger.warning(f"Only extracted {actual_count} references from large text ({len(text)} chars). This might indicate truncation.")
                
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
        return """You are an expert reference extraction agent. Your task is to identify and extract ALL references from academic and non-academic text.

CRITICAL REQUIREMENTS:
- You MUST extract EVERY single reference in the text
- Do not skip or miss any references
- Count references carefully to ensure completeness
- If the text contains 26 references, extract all 26
- If the text contains 50 references, extract all 50

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
- Generate a unique ID (ref_1, ref_2, ref_3, etc.)
- Preserve the original text that was identified
- Assign order numbers sequentially (1, 2, 3, etc.)

Be thorough and accurate in your extraction. If you're unsure about a reference, include it but mark the confidence appropriately. The total_references count in extraction_metadata MUST match the actual number of references in the references array."""
    
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
