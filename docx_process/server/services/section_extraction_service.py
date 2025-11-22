"""
Section extraction service that orchestrates document extraction, AI classification, and content organization.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

from .document_extractor import DocumentExtractor
from .section_mapper import SectionMapper
from .content_organizer import ContentOrganizer
from .word_document_service import WordDocumentService
from .first_page_metadata_extraction_service import FirstPageMetadataExtractionService
from .section_paragraph_parser_service import SectionParagraphParserService

logger = logging.getLogger(__name__)


class SectionExtractionService:
    """Service for extracting sections from Word documents using AI classification."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize section extraction service."""
        self.extractor = DocumentExtractor()
        self.mapper = SectionMapper(api_key=api_key)
        self.organizer = ContentOrganizer()
        self.word_service = WordDocumentService()
        self.metadata_extractor = FirstPageMetadataExtractionService(api_key=api_key)
        self.paragraph_parser = SectionParagraphParserService(api_key=api_key)
        logger.info("Section extraction service initialized")
    
    def extract_sections_from_docx(self, file_content: bytes, filename: str, sections: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Extract sections from a Word document using AI classification.
        
        Args:
            file_content: Raw file content as bytes
            filename: Original filename
            sections: Optional list of section names to extract. If None, uses default sections.
                      Always includes 'references' section even if not provided.
            
        Returns:
            Dictionary containing extracted sections and metadata
        """
        try:
            logger.info(f"Starting section extraction from document: {filename}")
            
            # Step 0: Extract first page metadata (abstract, authors, keywords) using AI
            logger.info("Step 0: Extracting first page metadata (abstract, authors, keywords) using AI...")
            first_page_metadata = self._extract_first_page_metadata_ai(file_content)
            logger.info(f"Extracted first page metadata: abstract={bool(first_page_metadata.get('abstract'))}, authors={len(first_page_metadata.get('authors', []))}, keywords={bool(first_page_metadata.get('keywords'))}")
            
            # Step 1: Extract chunks with ID numbering
            logger.info("Step 1: Extracting chunks with ID numbering...")
            chunks = self.extractor.extract_chunks_from_docx(file_content)
            logger.info(f"Extracted {len(chunks)} chunk(s) with {len(chunks[0].id_to_content) if chunks else 0} segments")
            
            # Prepare sections list - always include references
            # NOTE: abstract, authors, and keywords should NOT be in sections - they go in document header
            if sections is None:
                sections = []
            
            # Normalize section names and ensure references is included
            normalized_sections = [s.lower().strip() for s in sections if s and s.strip()]
            if 'references' not in normalized_sections:
                normalized_sections.append('references')
            
            # Remove abstract from sections if it was included - abstract goes in document header, not sections
            if 'abstract' in normalized_sections:
                normalized_sections.remove('abstract')
                logger.info("Removed 'abstract' from sections - abstract belongs in document header, not sections")
            
            logger.info(f"Processing sections: {normalized_sections}")
            
            # Step 2: Get classification instructions from AI (with parallel processing)
            logger.info("Step 2: Getting classification instructions from AI (parallel processing enabled)...")
            mapping = self.mapper.map_chunks(chunks, sections=normalized_sections, parallel=True, num_parallel_chunks=6)
            logger.info(f"AI provided {len(mapping.mappings)} mapping instructions")
            
            # Step 3: Extract actual content from chunks based on AI's mapping instructions
            logger.info("Step 3: Extracting content from chunks based on AI mapping instructions...")
            extracted_sections = self.organizer.organize(chunks, mapping, sections=normalized_sections)
            
            # NOTE: Do NOT merge abstract, authors, or keywords into extracted sections
            # These belong in document header (first_page_metadata), not in sections
            
            # Step 4: Convert sections to frontend-compatible format and process document in parallel
            logger.info("Step 4: Converting sections to frontend-compatible format (parallel processing)...")
            
            # Run section conversion and document processing in parallel
            with ThreadPoolExecutor(max_workers=2) as executor:
                sections_future = executor.submit(self._convert_to_frontend_format, extracted_sections, normalized_sections, first_page_metadata)
                processed_future = executor.submit(self.word_service.process_word_document, file_content, filename)
                
                sections_list = sections_future.result()
                processed_content = processed_future.result()
            
            logger.info("Step 4 completed: sections converted and document processed")
            
            result = {
                "filename": filename,
                "sections": sections_list,
                "extracted_sections": extracted_sections.model_dump(),
                "processed_content": processed_content,
                "first_page_metadata": first_page_metadata,
                "metadata": {
                    "total_sections": len([s for s in sections_list if s.get("content", "")]),
                    "extraction_method": "ai_classification",
                    "sections_requested": normalized_sections
                }
            }
            
            logger.info(f"Successfully extracted {len(sections_list)} sections from document")
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract sections from document: {str(e)}")
            raise Exception(f"Failed to extract sections: {str(e)}")
    
    def _extract_first_page_metadata_ai(self, file_content: bytes) -> Dict[str, Any]:
        """
        Extract abstract, authors, and keywords from the first page of the document using AI.
        
        Args:
            file_content: Raw file content as bytes
            
        Returns:
            Dictionary with abstract, authors, and keywords
        """
        try:
            from io import BytesIO
            from docx import Document
            
            doc = Document(BytesIO(file_content))
            
            # Extract first page content (first ~50 paragraphs or until we find a major section heading)
            first_page_paragraphs = []
            section_indicators = ["introduction", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9."]
            
            for i, para in enumerate(doc.paragraphs[:50]):  # Check first 50 paragraphs
                text = para.text.strip()
                if not text:
                    continue
                
                # Stop if we hit a major section heading
                text_lower = text.lower()
                if any(indicator in text_lower for indicator in section_indicators) and len(text) < 100:
                    # Likely a section heading, stop here
                    break
                
                first_page_paragraphs.append(text)
            
            # Also check tables in the first page for keywords/metadata
            first_page_text = "\n\n".join(first_page_paragraphs)
            
            # Check tables in first page
            for table in doc.tables[:3]:  # Check first 3 tables
                for row in table.rows:
                    for cell in row.cells:
                        cell_text = cell.text.strip()
                        if cell_text:
                            first_page_text += "\n\n" + cell_text
            
            # Use AI to extract metadata
            if first_page_text.strip():
                metadata = self.metadata_extractor.extract_metadata(first_page_text)
            else:
                metadata = {"abstract": "", "authors": [], "keywords": []}
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Failed to extract first page metadata using AI: {str(e)}")
            return {"abstract": "", "authors": [], "keywords": []}
    
    def _parse_authors(self, author_lines: List[str], author_names_line: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Parse author lines into structured format.
        
        Args:
            author_lines: List of author affiliation text lines
            author_names_line: Optional line containing author names (e.g., "Name1, Name2, Name3")
            
        Returns:
            List of dictionaries with author information (name, department, university, country, email)
        """
        import re
        parsed_authors = []
        
        # Extract author names from the names line if provided
        author_names = {}
        if author_names_line:
            # Pattern: "Name1, Name2, Name3" or "Name1 Name2 Name3"
            name_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\s*(\d+)'
            name_matches = re.finditer(name_pattern, author_names_line)
            for match in name_matches:
                name = match.group(1).strip()
                number = int(match.group(2))
                author_names[number] = name
        
        for line in author_lines:
            author_info = {
                "name": "",
                "department": "",
                "university": "",
                "country": "",
                "email": "",
                "order": len(parsed_authors) + 1
            }
            
            # Extract email if present
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, line)
            if email_match:
                author_info["email"] = email_match.group(0)
                line = line.replace(email_match.group(0), "").strip()
            
            # Extract author number (1, 2, 3, etc.) at the start
            number_match = re.match(r'^(\d+)', line)
            author_number = None
            if number_match:
                author_number = int(number_match.group(1))
                line = line[number_match.end():].strip()
                # Get author name from names line if available
                if author_number in author_names:
                    author_info["name"] = author_names[author_number]
            
            # Look for "Department" keyword - extract just the department name
            dept_pattern = r'Department\s+of\s+([^,]+?)(?:\s*,\s*(?:University|College|Institute|School)|$)'
            dept_match = re.search(dept_pattern, line, re.IGNORECASE)
            if dept_match:
                author_info["department"] = dept_match.group(1).strip()
                # Remove department from line
                line = re.sub(r'Department\s+of\s+[^,]+?', '', line, flags=re.IGNORECASE).strip()
                line = re.sub(r'^,\s*', '', line).strip()  # Remove leading comma
            
            # Look for University/College/Institute
            university_patterns = [
                r'([^,]+?)\s+(?:University|College|Institute|School)(?:\s+of\s+[^,]+)?',
                r'(?:University|College|Institute|School)\s+of\s+([^,]+)',
            ]
            university_found = False
            for pattern in university_patterns:
                univ_match = re.search(pattern, line, re.IGNORECASE)
                if univ_match:
                    author_info["university"] = univ_match.group(0).strip()
                    line = line.replace(univ_match.group(0), "").strip()
                    university_found = True
                    break
            
            # If no university pattern found, look for common university keywords
            if not university_found:
                univ_keywords = ["university", "college", "institute", "school"]
                for keyword in univ_keywords:
                    if keyword in line.lower():
                        # Try to extract university name
                        parts = re.split(rf'\b{keyword}\b', line, flags=re.IGNORECASE)
                        if len(parts) > 1:
                            # Take text before and including the keyword
                            univ_text = parts[0] + keyword
                            author_info["university"] = univ_text.strip()
                            line = line.replace(univ_text, "").strip()
                            break
            
            # Extract country only if clearly present (no fallback patterns)
            # Look for "City, Country" or "City-Country" pattern
            country_found = False
            if "," in line:
                # Try to find pattern like "City, Country" at the end
                parts = line.rsplit(",", 1)
                if len(parts) == 2:
                    potential_country = parts[1].strip()
                    # Only extract if it looks like a country (not email, zip code, etc.)
                    if potential_country and not re.search(r'[@\d]', potential_country) and len(potential_country) > 2:
                        author_info["country"] = potential_country
                        line = parts[0].strip()  # Remove country from line
                        country_found = True
            elif "-" in line:
                # Try "City-Country" pattern
                parts = line.rsplit("-", 1)
                if len(parts) == 2:
                    potential_country = parts[1].strip()
                    if potential_country and not re.search(r'[@\d]', potential_country) and len(potential_country) > 2:
                        author_info["country"] = potential_country
                        line = parts[0].strip()
                        country_found = True
            
            # Remove common prefixes and clean up
            line = re.sub(r'^(?:Zip\s+code|E-mail|Email|Phone|Tel)[:\s]*', '', line, flags=re.IGNORECASE)
            line = re.sub(r'[+\d\s-]+$', '', line)  # Remove trailing phone/zip codes
            line = re.sub(r'\s*Orcid:.*$', '', line, flags=re.IGNORECASE)  # Remove ORCID
            line = re.sub(r'\s*https?://[^\s]+', '', line)  # Remove URLs
            line = line.strip(' ,.-')
            
            # Clean up university field - remove trailing commas and extra text
            if author_info["university"]:
                author_info["university"] = re.sub(r',\s*$', '', author_info["university"]).strip()
            
            # Clean up department field - remove extra commas and text
            if author_info["department"]:
                # Remove everything after the department name (like city, country, etc.)
                dept_clean = author_info["department"].split(',')[0].strip()
                author_info["department"] = dept_clean
            
            # Clean up all fields
            for key in author_info:
                if isinstance(author_info[key], str):
                    author_info[key] = author_info[key].strip(' ,.-')
            
            parsed_authors.append(author_info)
        
        logger.info(f"Parsed {len(parsed_authors)} authors with structured information")
        return parsed_authors
    
    def _convert_to_frontend_format(self, extracted_sections, sections: List[str], first_page_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert extracted sections to frontend-compatible format.
        
        Args:
            extracted_sections: ExtractedSections object with content
            sections: List of section names to include
            first_page_metadata: Metadata from first page (abstract, authors, keywords)
        
        Frontend expects sections with:
        - id: string
        - title: string
        - description: string
        - order: number
        - required: boolean
        - content_type: string
        - content: string | object
        - is_complete: boolean
        """
        sections_list = []
        
        # Section name to metadata mapping
        section_metadata = {
            "abstract": {"id": "abstract", "title": "Abstract", "description": "Abstract of the research", "content_type": "abstract"},
            "introduction": {"id": "introduction", "title": "Introduction", "description": "Introduction to the research topic and context", "content_type": "introduction"},
            "literature_review": {"id": "literature_review", "title": "Literature Review", "description": "Review of relevant literature and previous research", "content_type": "literature_review"},
            "research_model": {"id": "research_model_hypotheses", "title": "Research Model and Hypotheses", "description": "Research model, framework, and hypotheses", "content_type": "research_model"},
            "methodology": {"id": "methodology", "title": "Methodology", "description": "Research methodology and methods used", "content_type": "methodology"},
            "data_analysis": {"id": "data_analysis_results", "title": "Data Analysis and Results", "description": "Data analysis and research results", "content_type": "results"},
            "discussion": {"id": "discussion_implications", "title": "Discussion and Implications", "description": "Discussion of results and implications", "content_type": "discussion"},
            "conclusion": {"id": "conclusion", "title": "Conclusion", "description": "Conclusion and summary of the research", "content_type": "conclusion"},
            "references": {"id": "references", "title": "References", "description": "References and bibliography", "content_type": "references"},
            "additional": {"id": "additional", "title": "Additional Content", "description": "Additional content that doesn't fit into other sections", "content_type": "additional"},
            "other": {"id": "additional", "title": "Additional Content", "description": "Additional content that doesn't fit into other sections", "content_type": "additional"},
        }
        
        # Field name mapping
        field_mapping = {
            "abstract": "abstract",
            "introduction": "introduction",
            "literature_review": "literature_review",
            "research_model": "research_model",
            "methodology": "methodology",
            "data_analysis": "data_analysis",
            "discussion": "discussion",
            "conclusion": "conclusion",
            "references": "references",
            "additional": "other",
            "other": "other"
        }
        
        order = 1
        
        # Collect all sections that need parsing (including "other" section)
        sections_to_parse = {}
        section_info_map = {}
        
        for section_name in sections:
            if section_name not in section_metadata:
                continue
            
            section_info = section_metadata[section_name]
            content_field = field_mapping.get(section_name, section_name)
            content = getattr(extracted_sections, content_field, "")
            
            # Skip abstract - it should not be in sections, it belongs in document header
            if section_name == "abstract":
                logger.info("Skipping abstract - it belongs in document header, not sections")
                continue
            
            if content and content.strip():
                sections_to_parse[section_name] = content
                section_info_map[section_name] = {
                    "info": section_info,
                    "content_field": content_field
                }
        
        # Also add "other" section if it exists
        other_content = getattr(extracted_sections, "other", "")
        if other_content and other_content.strip() and "other" not in sections_to_parse:
            sections_to_parse["other"] = other_content
        
        # Parse sections - use simple splitting for speed (skip AI paragraph parsing to save time)
        # AI paragraph parsing is slow and not critical for most documents
        parsed_sections = {}
        for section_name, content in sections_to_parse.items():
            # Simple paragraph splitting (fast, no AI calls)
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            # If no double newlines, try single newlines
            if not paragraphs:
                paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
            # Fallback to whole content
            if not paragraphs:
                paragraphs = [content] if content.strip() else []
            parsed_sections[section_name] = paragraphs
            logger.info(f"Parsed section '{section_name}' into {len(paragraphs)} paragraphs (simple parsing)")
        
        # Process requested sections in parallel
        def process_section(section_name: str, section_order: int) -> Dict[str, Any]:
            """Process a single section and return its TipTap content."""
            if section_name not in section_metadata:
                return None
            
            section_info = section_metadata[section_name]
            content_field = field_mapping.get(section_name, section_name)
            content = getattr(extracted_sections, content_field, "")
            
            # Skip abstract - it should not be in sections, it belongs in document header
            if section_name == "abstract":
                return None
            
            # Get tables for this section
            section_tables = []
            if hasattr(extracted_sections, 'tables') and extracted_sections.tables:
                # Try to get tables by content field name
                section_tables = extracted_sections.tables.get(content_field, [])
                # Also try section name directly in case it's stored differently
                if not section_tables:
                    section_tables = extracted_sections.tables.get(section_name, [])
            
            # Convert content to TipTap format if it has content
            tiptap_content = None
            tiptap_nodes = []
            
            if content and content.strip():
                # Use AI-parsed paragraphs if available
                paragraphs = parsed_sections.get(section_name, [])
                
                if paragraphs:
                    # Convert paragraphs to TipTap format (sequential - fast operation)
                    for para_text in paragraphs:
                        if para_text.strip():
                            para_tiptap = self.word_service._convert_text_to_tiptap(para_text)
                            if para_tiptap and para_tiptap.get("content"):
                                tiptap_nodes.extend(para_tiptap["content"])
                else:
                    # Fallback: use original content
                    text_tiptap = self.word_service._convert_text_to_tiptap(content)
                    if text_tiptap and text_tiptap.get("content"):
                        tiptap_nodes.extend(text_tiptap["content"])
            
            # Convert tables to TipTap format and add them
            for table_data in section_tables:
                table_node = self.word_service._convert_table_to_tiptap(table_data)
                if table_node:
                    tiptap_nodes.append(table_node)
            
            # Create final TipTap content
            if tiptap_nodes:
                tiptap_content = {
                    "type": "doc",
                    "content": tiptap_nodes
                }
            else:
                tiptap_content = {"type": "doc", "content": []}
            
            return {
                "id": section_info["id"],
                "title": section_info["title"],
                "description": section_info["description"],
                "order": section_order,
                "required": section_name == "references",
                "content_type": section_info["content_type"],
                "content": tiptap_content,
                "is_complete": bool(content and content.strip()) or len(section_tables) > 0,
                "section_name": section_name  # For sorting
            }
        
        # Process all sections in parallel
        logger.info(f"Processing {len(sections)} sections in parallel...")
        section_results = []
        with ThreadPoolExecutor(max_workers=min(len(sections), 8)) as executor:
            future_to_section = {
                executor.submit(process_section, section_name, i+1): (section_name, i+1)
                for i, section_name in enumerate(sections)
                if section_name in section_metadata
            }
            
            for future in as_completed(future_to_section):
                section_name, section_order = future_to_section[future]
                try:
                    result = future.result()
                    if result:
                        section_results.append(result)
                        logger.info(f"Completed processing section '{section_name}'")
                except Exception as e:
                    logger.error(f"Error processing section '{section_name}': {str(e)}")
        
        # Sort sections by original order
        section_results.sort(key=lambda x: x["order"])
        sections_list.extend([{k: v for k, v in r.items() if k != "section_name"} for r in section_results])
        order = len(sections_list) + 1
        
        # Add additional section if there's unmatched content (process in parallel if needed)
        other_content = getattr(extracted_sections, "other", "")
        if other_content and other_content.strip():
            section_info = section_metadata["additional"]
            tiptap_content = None
            tiptap_nodes = []
            
            if other_content and other_content.strip():
                # Parse "other" section using AI (already done in parallel parsing above)
                other_paragraphs = parsed_sections.get("other", [])
                
                # If not in parsed sections, parse it now
                if not other_paragraphs:
                    other_paragraphs = self.paragraph_parser.parse_section_to_paragraphs(other_content, "other")
                
                if other_paragraphs:
                    # Convert paragraphs to TipTap format (sequential - fast operation)
                    for para_text in other_paragraphs:
                        if para_text.strip():
                            para_tiptap = self.word_service._convert_text_to_tiptap(para_text)
                            if para_tiptap and para_tiptap.get("content"):
                                tiptap_nodes.extend(para_tiptap["content"])
                else:
                    # Fallback: use original content
                    text_tiptap = self.word_service._convert_text_to_tiptap(other_content)
                    if text_tiptap and text_tiptap.get("content"):
                        tiptap_nodes.extend(text_tiptap["content"])
            
            # Get tables for the "other" section
            other_tables = []
            if hasattr(extracted_sections, 'tables') and extracted_sections.tables:
                # Check for tables in "other" section
                other_tables = extracted_sections.tables.get("other", [])
                # Also check for tables that weren't assigned to any specific section
                if "none" in extracted_sections.tables:
                    other_tables.extend(extracted_sections.tables.get("none", []))
            
            # Convert tables to TipTap format and add them
            for table_data in other_tables:
                table_node = self.word_service._convert_table_to_tiptap(table_data)
                if table_node:
                    tiptap_nodes.append(table_node)
                    logger.info(f"Added table to additional section")
            
            if tiptap_nodes:
                tiptap_content = {
                    "type": "doc",
                    "content": tiptap_nodes
                }
            else:
                tiptap_content = {"type": "doc", "content": []}
            
            sections_list.append({
                "id": section_info["id"],
                "title": section_info["title"],
                "description": section_info["description"],
                "order": order,
                "required": False,
                "content_type": section_info["content_type"],
                "content": tiptap_content,
                "is_complete": bool(other_content and other_content.strip()) or len(other_tables) > 0
            })
        
        return sections_list

