"""
AI-based service for parsing section content into proper paragraphs.
"""

import logging
import os
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

logger = logging.getLogger(__name__)


class SectionParagraphParserService:
    """Service for parsing section content into proper paragraphs using AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the section paragraph parser service."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.client = OpenAI(api_key=self.api_key)
        logger.info("Section paragraph parser service initialized")
    
    def parse_section_to_paragraphs(self, section_text: str, section_name: str = "") -> List[str]:
        """
        Parse section text into proper paragraphs using AI.
        
        Args:
            section_text: The section text content
            section_name: Optional name of the section for context
            
        Returns:
            List of paragraph strings
        """
        try:
            if not section_text or not section_text.strip():
                return []
            
            logger.info(f"Parsing section '{section_name}' into paragraphs ({len(section_text)} chars)")
            
            system_prompt = """You are an expert at parsing academic document sections into proper paragraphs.

Your task is to take a section of text and break it into logical paragraphs. Each paragraph should be:
- A complete thought or idea
- Properly separated from other paragraphs
- Not split in the middle of a sentence
- Preserve all formatting, citations, and content

Return a JSON array of strings, where each string is a paragraph:
["Paragraph 1 text here", "Paragraph 2 text here", "Paragraph 3 text here"]

IMPORTANT:
- Preserve ALL text content - do not summarize or omit anything
- Each paragraph should be a complete, coherent unit
- Maintain proper paragraph breaks where they naturally occur
- Do not split sentences across paragraphs
- Preserve citations, references, and formatting"""

            user_prompt = f"""Parse the following section text into proper paragraphs:

Section: {section_name}
Text:
{section_text}

Return a JSON object with a "paragraphs" key containing an array of paragraph strings:
{{"paragraphs": ["Paragraph 1 text", "Paragraph 2 text", ...]}}"""

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
            
            # Try to fix common JSON issues before parsing
            result_text = result_text.strip()
            # Remove any markdown code blocks if present
            if result_text.startswith("```"):
                lines = result_text.split("\n")
                result_text = "\n".join(lines[1:-1]) if len(lines) > 2 else result_text
            
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError as json_err:
                logger.warning(f"JSON parsing error, attempting to fix: {str(json_err)}")
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group(0))
                    except:
                        # Last resort: try to parse as array
                        array_match = re.search(r'\[.*\]', result_text, re.DOTALL)
                        if array_match:
                            result = json.loads(array_match.group(0))
                        else:
                            raise json_err
                else:
                    raise json_err
            
            # Extract paragraphs from result
            paragraphs = []
            if isinstance(result, dict):
                # Try common keys
                if "paragraphs" in result:
                    paragraphs = result["paragraphs"]
                elif "content" in result:
                    paragraphs = result["content"]
                else:
                    # Get first array value
                    for value in result.values():
                        if isinstance(value, list):
                            paragraphs = value
                            break
            elif isinstance(result, list):
                paragraphs = result
            
            # Ensure all items are strings
            paragraphs = [str(p).strip() for p in paragraphs if p and str(p).strip()]
            
            logger.info(f"Parsed section '{section_name}' into {len(paragraphs)} paragraphs")
            
            return paragraphs
            
        except Exception as e:
            logger.error(f"Error parsing section '{section_name}' into paragraphs: {str(e)}")
            # Fallback: split by double newlines
            return [p.strip() for p in section_text.split('\n\n') if p.strip()]
    
    def parse_sections_parallel(self, sections: Dict[str, str], max_workers: int = 5) -> Dict[str, List[str]]:
        """
        Parse multiple sections into paragraphs in parallel.
        
        Args:
            sections: Dictionary mapping section names to section text
            max_workers: Maximum number of parallel workers
            
        Returns:
            Dictionary mapping section names to lists of paragraphs
        """
        logger.info(f"Parsing {len(sections)} sections in parallel (max_workers={max_workers})")
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_section = {
                executor.submit(self.parse_section_to_paragraphs, text, name): name
                for name, text in sections.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_section):
                section_name = future_to_section[future]
                try:
                    paragraphs = future.result()
                    results[section_name] = paragraphs
                    logger.info(f"Completed parsing section '{section_name}' ({len(paragraphs)} paragraphs)")
                except Exception as e:
                    logger.error(f"Error parsing section '{section_name}': {str(e)}")
                    # Fallback: use original text as single paragraph
                    results[section_name] = [sections[section_name]] if sections[section_name].strip() else []
        
        return results

