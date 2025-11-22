"""
Content organizer that organizes chunks based on AI mapping instructions.
Extracts actual content from document chunks based on OpenAI's classification.
"""

import logging
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from .document_extractor import DocumentChunk
from .section_mapper import ContentMapping

logger = logging.getLogger(__name__)


class ExtractedSections(BaseModel):
    """Structure for extracted sections with content"""
    title: str = Field(description="Title of document", default="")
    abstract: str = Field(description="Abstract section content", default="")
    introduction: str = Field(description="Introduction section content", default="")
    literature_review: str = Field(description="Literature Review section content", default="")
    research_model: str = Field(description="Research Model and Hypotheses section content", default="")
    methodology: str = Field(description="Methodology section content", default="")
    data_analysis: str = Field(description="Data Analysis and Results section content", default="")
    discussion: str = Field(description="Discussion and Implications section content", default="")
    conclusion: str = Field(description="Conclusion section content", default="")
    references: str = Field(description="References section content", default="")
    other: str = Field(description="Other content that doesn't fit any section", default="")
    tables: Dict[str, List[Dict]] = Field(description="Table data by section name", default_factory=dict)


class ContentOrganizer:
    """Organizes document chunks based on AI mapping instructions.
    
    This class extracts actual content from document chunks based on OpenAI's
    classification/mapping instructions. OpenAI tells us WHERE to find content,
    and this class extracts the actual text from those locations.
    """
    
    # Common section headings to strip from content
    SECTION_HEADINGS = [
        "ABSTRACT", "ABSTRACT:", "ABSTRACT.",
        "INTRODUCTION", "INTRODUCTION:", "INTRODUCTION.", "1. INTRODUCTION", "1.   INTRODUCTION",
        "LITERATURE REVIEW", "LITERATURE REVIEW:", "LITERATURE REVIEW.", "2. LITERATURE REVIEW", "2.   LITERATURE REVIEW",
        "RESEARCH MODEL", "RESEARCH MODEL AND HYPOTHESES", "3. RESEARCH MODEL", "3.   RESEARCH MODEL",
        "METHODOLOGY", "METHODOLOGY:", "METHODOLOGY.", "4. METHODOLOGY", "4.   METHODOLOGY",
        "DATA ANALYSIS", "DATA ANALYSIS AND RESULTS", "5. DATA ANALYSIS", "5.   DATA ANALYSIS",
        "RESULTS", "RESULTS:", "RESULTS.",
        "DISCUSSION", "DISCUSSION:", "DISCUSSION.", "DISCUSSION AND IMPLICATIONS", "6. DISCUSSION", "6.   DISCUSSION",
        "CONCLUSION", "CONCLUSION:", "CONCLUSION.", "7. CONCLUSION", "7.   CONCLUSION",
        "REFERENCES", "REFERENCES:", "REFERENCES.",
    ]
    
    @staticmethod
    def strip_section_heading(content: str, section_name: str) -> str:
        """Strip section headings from content."""
        if not content:
            return content
        
        # Split into lines
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            # Skip lines that are just section headings
            is_heading = False
            
            # Check if line is a common section heading
            for heading in ContentOrganizer.SECTION_HEADINGS:
                if line_stripped.upper() == heading.upper() or line_stripped.upper().startswith(heading.upper()):
                    is_heading = True
                    break
            
            # Also check for numbered headings like "1. INTRODUCTION"
            if not is_heading and line_stripped and (line_stripped[0].isdigit() and '.' in line_stripped[:5]):
                # Check if it matches a section heading pattern
                heading_part = line_stripped.split('.', 1)[1].strip() if '.' in line_stripped else line_stripped
                for heading in ContentOrganizer.SECTION_HEADINGS:
                    if heading_part.upper().startswith(heading.upper()):
                        is_heading = True
                        break
            
            # Don't add headings to cleaned content
            if not is_heading:
                cleaned_lines.append(line)
        
        # Join and clean up
        cleaned = '\n'.join(cleaned_lines)
        
        # Remove leading/trailing whitespace and newlines
        cleaned = cleaned.strip()
        
        # Remove any remaining section name at the start
        if cleaned:
            # Check if content starts with section name (case-insensitive)
            for heading in ContentOrganizer.SECTION_HEADINGS:
                if cleaned.upper().startswith(heading.upper()):
                    # Remove the heading
                    cleaned = cleaned[len(heading):].strip()
                    # Remove leading newline or colon if present
                    if cleaned.startswith(':') or cleaned.startswith('.'):
                        cleaned = cleaned[1:].strip()
                    break
        
        return cleaned
    
    def organize(self, chunks: List[DocumentChunk], mapping: ContentMapping, sections: Optional[List[str]] = None) -> ExtractedSections:
        """
        Extract and organize content from chunks based on AI mapping instructions.
        
        OpenAI provides mapping instructions (which chunk, which section).
        This method extracts the actual content from the chunks based on those instructions.
        
        Args:
            chunks: List of document chunks (the actual content)
            mapping: ContentMapping from AI (instructions telling us where to extract from)
            sections: Optional list of section names to organize. If None, uses default sections.
            
        Returns:
            ExtractedSections object with actual extracted content
        """
        logger.info("Extracting content from chunks based on AI mapping instructions")
        
        # Prepare sections list - always include common sections
        if sections is None:
            sections = []
        
        # Normalize sections
        normalized_sections = [s.lower().strip() for s in sections if s and s.strip()]
        
        # Always include these sections
        all_sections = ['title', 'abstract', 'introduction', 'literature_review', 'research_model', 
                        'methodology', 'data_analysis', 'discussion', 'conclusion', 'references', 'other']
        
        # Create sections dictionary dynamically
        sections_dict: Dict[str, List[str]] = {}
        for section in all_sections:
            sections_dict[section] = []
        
        # Track table data by section
        section_tables: Dict[str, List[Dict]] = {}
        
        # Process each mapping instruction from OpenAI
        for map_item in mapping.mappings:
            chunk_idx = map_item.chunk_index
            if chunk_idx >= len(chunks):
                logger.warning(f"Mapping refers to chunk {chunk_idx} but only {len(chunks)} chunks exist")
                continue
            
            chunk = chunks[chunk_idx]
            section = map_item.section.lower()
            
            # Extract actual content from chunk based on OpenAI's ID range instructions
            content_parts = []
            
            # Ensure chunk has ID mapping
            if not hasattr(chunk, 'id_to_content') or not chunk.id_to_content:
                logger.warning(f"Chunk {chunk_idx} does not have ID mapping, skipping")
                continue
            
            if map_item.start_id and map_item.end_id:
                # Extract content based on ID range
                start_id = map_item.start_id.strip()
                end_id = map_item.end_id.strip()
                
                # Get all IDs in the chunk
                all_ids = list(chunk.id_to_content.keys())
                
                # Find the range of IDs to extract
                try:
                    # Handle regular IDs (id1, id2, etc.)
                    if start_id.startswith('id') and end_id.startswith('id'):
                        # Extract numeric parts
                        start_num = int(start_id[2:]) if start_id[2:] else 0
                        end_num = int(end_id[2:]) if end_id[2:] else 0
                        
                        # Extract all IDs in range
                        for i in range(start_num, end_num + 1):
                            id_key = f"id{i}"
                            if id_key in chunk.id_to_content:
                                content_parts.append(chunk.id_to_content[id_key])
                    # Handle table IDs (TABLE_1, TABLE_2, etc.)
                    elif start_id.startswith('TABLE_') or end_id.startswith('TABLE_'):
                        # Single table or table range - store table data separately
                        if start_id == end_id:
                            # Single table
                            if hasattr(chunk, 'id_to_table_data') and start_id in chunk.id_to_table_data:
                                table_data = chunk.id_to_table_data[start_id]
                                if section not in section_tables:
                                    section_tables[section] = []
                                section_tables[section].append(table_data)
                                logger.info(f"Extracted table {start_id} for section {section}")
                        else:
                            # Table range
                            start_num = int(start_id.split('_')[1]) if '_' in start_id else 0
                            end_num = int(end_id.split('_')[1]) if '_' in end_id else 0
                            for i in range(start_num, end_num + 1):
                                table_key = f"TABLE_{i}"
                                if hasattr(chunk, 'id_to_table_data') and table_key in chunk.id_to_table_data:
                                    table_data = chunk.id_to_table_data[table_key]
                                    if section not in section_tables:
                                        section_tables[section] = []
                                    section_tables[section].append(table_data)
                                    logger.info(f"Extracted table {table_key} for section {section}")
                    # Handle direct ID matches
                    else:
                        if start_id in chunk.id_to_content:
                            # Check if it's a table
                            if start_id.startswith('TABLE_') and hasattr(chunk, 'id_to_table_data') and start_id in chunk.id_to_table_data:
                                table_data = chunk.id_to_table_data[start_id]
                                if section not in section_tables:
                                    section_tables[section] = []
                                section_tables[section].append(table_data)
                            else:
                                content_parts.append(chunk.id_to_content[start_id])
                        if end_id != start_id and end_id in chunk.id_to_content:
                            # Check if it's a table
                            if end_id.startswith('TABLE_') and hasattr(chunk, 'id_to_table_data') and end_id in chunk.id_to_table_data:
                                table_data = chunk.id_to_table_data[end_id]
                                if section not in section_tables:
                                    section_tables[section] = []
                                section_tables[section].append(table_data)
                            else:
                                content_parts.append(chunk.id_to_content[end_id])
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error extracting ID range {start_id} to {end_id}: {e}")
                    # Fallback: try to extract by exact ID match
                    if start_id in chunk.id_to_content:
                        # Check if it's a table - if so, extract table data instead
                        if start_id.startswith('TABLE_') and hasattr(chunk, 'id_to_table_data') and start_id in chunk.id_to_table_data:
                            table_data = chunk.id_to_table_data[start_id]
                            if section not in section_tables:
                                section_tables[section] = []
                            section_tables[section].append(table_data)
                            logger.info(f"Extracted table {start_id} for section {section} (fallback)")
                        else:
                            content_parts.append(chunk.id_to_content[start_id])
                
                # Combine extracted content parts
                if content_parts:
                    # Filter out table text content if we have table data for this section
                    # Tables are stored with "Table X content:" prefix, so we should exclude them
                    filtered_parts = []
                    for part in content_parts:
                        # Skip if this is clearly table text (starts with "Table X content:") and we have table data
                        part_stripped = part.strip()
                        is_table_text = (
                            part_stripped.startswith("Table ") and 
                            "content:" in part_stripped and
                            len(part_stripped.split("\n")) > 1  # Has multiple lines (table rows)
                        )
                        
                        if is_table_text and section in section_tables and len(section_tables[section]) > 0:
                            # This is table text, skip it since we have structured table data
                            logger.info(f"Skipping table text content for section {section} (have {len(section_tables[section])} structured table(s))")
                            continue
                        filtered_parts.append(part)
                    
                    if filtered_parts:
                        content = "\n".join(filtered_parts)
                        # Strip section headings from content
                        content = ContentOrganizer.strip_section_heading(content, section)
                    else:
                        # Only tables, no text content
                        content = ""
                else:
                    # No text content, but might have tables
                    content = ""
            else:
                # No ID range specified
                logger.warning(f"Mapping item missing start_id or end_id: {map_item}")
                continue
            
            # Map to appropriate section (only if we have content, or if we have tables)
            # Map "none" to "other"
            target_section = section if section != "none" else "other"
            
            if content or (target_section in section_tables and len(section_tables.get(target_section, [])) > 0):
                if target_section in sections_dict:
                    if content:  # Only add text content if it exists
                        sections_dict[target_section].append(content)
                else:
                    if content:  # Only add text content if it exists
                        sections_dict['other'].append(content)
        
        # Combine extracted content by section
        title_text = " ".join(sections_dict['title']).strip()
        if len(title_text) > 300:
            title_text = title_text[:300]
        
        abstract_text = "\n\n".join(sections_dict['abstract']).strip()
        introduction_text = "\n\n".join(sections_dict['introduction']).strip()
        literature_review_text = "\n\n".join(sections_dict['literature_review']).strip()
        research_model_text = "\n\n".join(sections_dict['research_model']).strip()
        methodology_text = "\n\n".join(sections_dict['methodology']).strip()
        data_analysis_text = "\n\n".join(sections_dict['data_analysis']).strip()
        discussion_text = "\n\n".join(sections_dict['discussion']).strip()
        conclusion_text = "\n\n".join(sections_dict['conclusion']).strip()
        references_text = "\n\n".join(sections_dict['references']).strip()
        other_text = "\n\n".join(sections_dict['other']).strip()
        
        logger.info(f"Organized content:")
        logger.info(f"  Title: {title_text[:50]}...")
        logger.info(f"  Abstract: {len(abstract_text)} characters")
        logger.info(f"  Introduction: {len(introduction_text)} characters")
        logger.info(f"  Literature Review: {len(literature_review_text)} characters")
        logger.info(f"  Research Model: {len(research_model_text)} characters")
        logger.info(f"  Methodology: {len(methodology_text)} characters")
        logger.info(f"  Data Analysis: {len(data_analysis_text)} characters")
        logger.info(f"  Discussion: {len(discussion_text)} characters")
        logger.info(f"  Conclusion: {len(conclusion_text)} characters")
        logger.info(f"  References: {len(references_text)} characters")
        if references_text:
            logger.info(f"  References preview (first 300 chars): {references_text[:300]}...")
            # Check if references section looks like actual references or something else
            if "regression" in references_text.lower() or "analysis" in references_text.lower() or "table" in references_text.lower():
                logger.warning(f"WARNING: References section may contain non-reference content! Preview: {references_text[:200]}...")
        logger.info(f"  Other: {len(other_text)} characters")
        if other_text:
            logger.info(f"  Other preview (first 300 chars): {other_text[:300]}...")
        
        return ExtractedSections(
            title=title_text,
            abstract=abstract_text,
            introduction=introduction_text,
            literature_review=literature_review_text,
            research_model=research_model_text,
            methodology=methodology_text,
            data_analysis=data_analysis_text,
            discussion=discussion_text,
            conclusion=conclusion_text,
            references=references_text,
            other=other_text,
            tables=section_tables
        )

