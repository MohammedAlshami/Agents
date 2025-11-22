"""
Document extraction module for DOCX files with ID numbering.
Extracts content and assigns IDs to each segment for AI classification.
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from io import BytesIO
from docx import Document

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a chunk of document content with ID-based numbering"""
    page_number: int
    content: str
    numbered_content: str = ""  # Content with IDs for each segment
    id_to_content: Optional[Dict[str, str]] = None  # Mapping of ID to actual content
    id_to_table_data: Optional[Dict[str, Dict]] = None  # Mapping of ID to table structure data
    has_table: bool = False
    has_image: bool = False
    table_placeholder: Optional[str] = None
    image_placeholder: Optional[str] = None
    
    def __post_init__(self):
        """Initialize id_to_content if not provided"""
        if self.id_to_content is None:
            self.id_to_content = {}
        if self.id_to_table_data is None:
            self.id_to_table_data = {}


class DocumentExtractor:
    """Handles extraction of text content from DOCX document formats with ID numbering"""
    
    def __init__(self):
        self.supported_formats = ['.docx']
    
    def extract_chunks_from_docx(self, file_content: bytes) -> List[DocumentChunk]:
        """Extract all content from DOCX file with ID numbering.
        
        Extracts the entire document content at once, numbering each segment with unique IDs.
        Images are replaced with placeholders. Returns a single chunk with numbered content.
        """
        logger.info("Extracting all content from DOCX file with ID numbering")
        doc = Document(BytesIO(file_content))
        
        all_content = []  # Original content segments
        numbered_content_list = []  # Numbered content for AI
        id_to_content = {}  # Mapping: ID -> actual content
        id_to_table_data = {}  # Mapping: ID -> table structure data
        current_id = 1
        table_counter = 1
        image_counter = 1
        has_table = False
        has_image = False
        table_placeholders = []
        image_placeholders = []
        
        logger.info("Processing all paragraphs and numbering each segment...")
        
        # Extract all paragraphs and number each one
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                # Use paragraph as unit - each paragraph gets an ID
                segment_id = f"id{current_id}"
                all_content.append(text)
                numbered_content_list.append(f"[{segment_id}] {text}")
                id_to_content[segment_id] = text
                current_id += 1
        
        # Process tables and insert placeholders with IDs
        logger.info(f"Processing {len(doc.tables)} table(s)...")
        if doc.tables:
            has_table = True
            for idx, table in enumerate(doc.tables, 1):
                # Extract table structure data
                table_data = {
                    "rows": len(table.rows),
                    "columns": len(table.columns) if table.rows else 0,
                    "cells": []
                }
                
                # Extract table text for AI classification
                table_text = []
                for row_idx, row in enumerate(table.rows):
                    row_text = []
                    row_data = []
                    for col_idx, cell in enumerate(row.cells):
                        cell_text = cell.text.strip()
                        row_text.append(cell_text)
                        row_data.append({
                            "row": row_idx,
                            "column": col_idx,
                            "text": cell_text
                        })
                    table_text.append(" | ".join(row_text))
                    table_data["cells"].append(row_data)
                
                if table_text:
                    table_id = f"TABLE_{table_counter}"
                    placeholder = f"[{table_id}]"
                    table_content = "\n".join(table_text)
                    table_full_content = f"Table {table_counter} content:\n{table_content}"
                    
                    all_content.append(table_full_content)
                    numbered_content_list.append(f"[{table_id}] {table_full_content}")
                    id_to_content[table_id] = table_full_content
                    id_to_table_data[table_id] = table_data  # Store structured table data
                    table_placeholders.append(placeholder)
                    table_counter += 1
                    current_id += 1
                    logger.info(f"Extracted table {idx} with {len(table_text)} rows as {table_id}")
        
        # Process images and replace with placeholders
        logger.info("Processing images and replacing with placeholders...")
        image_count = 0
        image_placeholder_positions = []  # Track where to insert placeholders
        
        # Check for images in relationships
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref.lower() or "image" in str(rel.reltype).lower():
                image_count += 1
        
        # Also check inline shapes (pictures) in paragraphs
        try:
            for para_idx, para in enumerate(doc.paragraphs):
                for run in para.runs:
                    # Check if run contains an image (blip element indicates image)
                    try:
                        if hasattr(run, '_element'):
                            # Simple check for image elements
                            if run._element.xpath('.//a:blip') or run._element.xpath('.//pic:pic'):
                                image_count += 1
                                # Mark this paragraph as having an image
                                if para.text.strip():
                                    image_placeholder_positions.append((para_idx, para.text.strip()[:50]))
                    except:
                        pass
        except Exception as e:
            logger.debug(f"Could not fully scan for inline images: {e}")
        
        if image_count > 0:
            has_image = True
            # Add image placeholders with IDs
            placeholder_index = 0
            for para_idx, para_text in image_placeholder_positions:
                placeholder_index += 1
                image_id = f"IMAGE_{placeholder_index}"
                placeholder = f"[{image_id}]"
                image_placeholders.append(placeholder)
                image_content = f"Image {placeholder_index} placeholder - image content not available"
                # Try to insert placeholder near the paragraph
                inserted = False
                for content_idx, content_item in enumerate(all_content):
                    if para_text in content_item:
                        all_content.insert(content_idx + 1, image_content)
                        numbered_content_list.insert(content_idx + 1, f"[{image_id}] {image_content}")
                        id_to_content[image_id] = image_content
                        inserted = True
                        break
                if not inserted:
                    all_content.append(image_content)
                    numbered_content_list.append(f"[{image_id}] {image_content}")
                    id_to_content[image_id] = image_content
            
            # Add remaining placeholders for images found in relationships
            remaining_images = image_count - len(image_placeholders)
            for i in range(remaining_images):
                placeholder_index += 1
                image_id = f"IMAGE_{placeholder_index}"
                placeholder = f"[{image_id}]"
                image_placeholders.append(placeholder)
                image_content = f"Image {placeholder_index} placeholder - image content not available"
                all_content.append(image_content)
                numbered_content_list.append(f"[{image_id}] {image_content}")
                id_to_content[image_id] = image_content
            
            logger.info(f"Replaced {image_count} image(s) with placeholders")
        
        # Combine all content into a single chunk
        full_content = "\n".join(all_content)
        numbered_content = "\n".join(numbered_content_list)
        
        # Create a single chunk with all content and ID mapping
        chunk = DocumentChunk(
            page_number=1,  # Single chunk for entire document
            content=full_content,
            numbered_content=numbered_content,
            id_to_content=id_to_content,
            id_to_table_data=id_to_table_data,  # Store table data
            has_table=has_table,
            has_image=has_image,
            table_placeholder=", ".join(table_placeholders) if table_placeholders else None,
            image_placeholder=", ".join(image_placeholders) if image_placeholders else None
        )
        
        logger.info(f"Extracted entire document as single chunk ({len(full_content)} characters)")
        logger.info(f"  - Total segments: {len(id_to_content)} (numbered from id1 to id{len(id_to_content)})")
        logger.info(f"  - Tables: {len(table_placeholders)}")
        logger.info(f"  - Images: {len(image_placeholders)} (replaced with placeholders)")
        
        return [chunk]

