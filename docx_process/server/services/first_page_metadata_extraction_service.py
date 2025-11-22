"""
AI-based service for extracting first page metadata (abstract, authors, keywords) from document text.
"""

import logging
import os
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class FirstPageMetadataExtractionService:
    """Service for extracting abstract, authors, and keywords from first page content using AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the first page metadata extraction service."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.client = OpenAI(api_key=self.api_key)
        logger.info("First page metadata extraction service initialized")
    
    def extract_metadata(self, first_page_text: str) -> Dict[str, Any]:
        """
        Extract abstract, authors, and keywords from first page text using AI.
        
        Args:
            first_page_text: Text content from the first page of the document
            
        Returns:
            Dictionary with abstract, authors (list), and keywords (string)
        """
        try:
            logger.info(f"Extracting first page metadata from {len(first_page_text)} characters of text")
            
            system_prompt = """You are an expert at extracting academic document metadata from the first page of research papers.

Your task is to extract:
1. Abstract - The abstract text (if present). This is usually a summary paragraph describing the research.
2. Authors - A list of author information with name, email, department, university, and country (if available)
3. Keywords - A comma-separated or semicolon-separated list of keywords (if present)

Return a JSON object with this exact structure:
{
  "abstract": "Full abstract text here, or empty string if not found",
  "authors": [
    {
      "name": "Author Full Name",
      "email": "email@example.com",
      "department": "Department Name",
      "university": "University Name",
      "country": "Country Name",
      "order": 1
    }
  ],
  "keywords": ["keyword1", "keyword2", "keyword3"]
}

IMPORTANT:
- Extract the FULL abstract text, not just a summary
- Extract ALL authors with as much information as possible
- Keywords can be separated by commas, semicolons, or newlines - parse them into an array of individual keyword strings
- Each keyword should be trimmed of whitespace
- If any field is not found, return an empty string (for abstract) or empty array (for authors/keywords)
- Be thorough and extract all available information"""

            user_prompt = f"""Extract the abstract, authors, and keywords from the following first page content:

{first_page_text}

Return ONLY valid JSON, no additional text or explanation."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # Ensure proper structure
            metadata = {
                "abstract": result.get("abstract", "").strip(),
                "authors": result.get("authors", []),
                "keywords": result.get("keywords", [])
            }
            
            # Validate authors structure
            if not isinstance(metadata["authors"], list):
                metadata["authors"] = []
            
            # Ensure each author has required fields
            for i, author in enumerate(metadata["authors"]):
                if not isinstance(author, dict):
                    metadata["authors"][i] = {}
                author.setdefault("name", "")
                author.setdefault("email", "")
                author.setdefault("department", "")
                author.setdefault("university", "")
                author.setdefault("country", "")
                author.setdefault("order", i + 1)
            
            # Validate keywords structure - ensure it's a list
            if not isinstance(metadata["keywords"], list):
                # If it's a string, try to parse it
                if isinstance(metadata["keywords"], str):
                    keywords_str = metadata["keywords"].strip()
                    if keywords_str:
                        # Split by comma, semicolon, or newline
                        keywords_list = []
                        for separator in [',', ';', '\n']:
                            if separator in keywords_str:
                                keywords_list = [k.strip() for k in keywords_str.split(separator) if k.strip()]
                                break
                        if not keywords_list:
                            # If no separator found, treat as single keyword
                            keywords_list = [keywords_str] if keywords_str else []
                        metadata["keywords"] = keywords_list
                    else:
                        metadata["keywords"] = []
                else:
                    metadata["keywords"] = []
            
            # Clean up keywords - remove empty strings and trim
            metadata["keywords"] = [k.strip() for k in metadata["keywords"] if k and str(k).strip()]
            
            logger.info(f"Extracted metadata: abstract={len(metadata['abstract'])} chars, authors={len(metadata['authors'])}, keywords={len(metadata['keywords'])} items")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting first page metadata: {str(e)}")
            return {
                "abstract": "",
                "authors": [],
                "keywords": []
            }

