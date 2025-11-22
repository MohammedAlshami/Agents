"""
Word document processing service for extracting content from Word documents.
"""

import os
import sys
import logging
import time
from typing import Dict, List, Any, Optional, BinaryIO
from io import BytesIO
import base64

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docx import Document
from docx.document import Document as DocumentType
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class WordDocumentService:
    """Service for processing Word documents and extracting content."""
    
    def __init__(self):
        """Initialize Word document service."""
        logger.info("Word document service initialized")
    
    def process_word_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process a Word document and extract all content parts in document order.
        
        Args:
            file_content: Raw file content as bytes
            filename: Original filename
            
        Returns:
            Dictionary containing extracted content parts
        """
        try:
            # Check file extension
            if not filename.lower().endswith('.docx'):
                raise ValueError(f"Only .docx files are supported. Received: {filename}. Please convert your .doc file to .docx format.")
            
            # Create document from bytes
            document = Document(BytesIO(file_content))
            
            # Extract title
            title = self._extract_title(document)
            
            # Extract content in document order
            ordered_content = self._extract_ordered_content(document)
            
            logger.info(f"Extracted content - Title: {title}")
            logger.info(f"Extracted content - Ordered elements: {len(ordered_content)}")
            
            result = {
                "filename": filename,
                "title": title,
                "ordered_content": ordered_content,
                "headers": self._extract_headers(document),
                "footers": self._extract_footers(document),
                "comments": self._extract_comments(document),
                "footnotes": self._extract_footnotes(document),
                "metadata": self._extract_metadata(document),
                "structure": self._extract_document_structure(document)
            }
            
            logger.info(f"Successfully processed Word document: {filename}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process Word document {filename}: {str(e)}")
            raise Exception(f"Failed to process Word document: {str(e)}")
    
    def _extract_title(self, document: DocumentType) -> Optional[str]:
        """Extract document title."""
        try:
            # Try to get title from document properties
            if document.core_properties.title:
                return document.core_properties.title
            
            # Try to get title from first heading
            for paragraph in document.paragraphs:
                if paragraph.style.name.startswith('Heading') and paragraph.text.strip():
                    return paragraph.text.strip()
            
            # Fallback to first paragraph
            for paragraph in document.paragraphs:
                if paragraph.text.strip():
                    return paragraph.text.strip()
            
            return None
        except Exception as e:
            logger.warning(f"Failed to extract title: {str(e)}")
            return None
    
    def _extract_ordered_content(self, document: DocumentType) -> List[Dict[str, Any]]:
        """
        Extract all content from document in the order it appears.
        This method processes paragraphs, tables, and images in document order.
        """
        ordered_content = []
        
        try:
            # Get all elements in document order by iterating through the document body
            for element in document.element.body:
                element_type = element.tag
                
                if element_type.endswith('p'):  # Paragraph
                    paragraph = self._get_paragraph_from_element(element, document)
                    if paragraph:
                        # Check if paragraph has inline images first
                        inline_images = []
                        self._extract_inline_images_from_paragraph(paragraph, document, inline_images)
                        
                        # Add paragraph if it has text
                        if paragraph.text.strip():
                            content_item = {
                                "type": "paragraph",
                                "text": paragraph.text.strip(),
                                "style": paragraph.style.name if paragraph.style else "Normal",
                                "alignment": str(paragraph.alignment) if paragraph.alignment else None,
                                "runs": self._extract_runs(paragraph)
                            }
                            ordered_content.append(content_item)
                            logger.debug(f"Added paragraph: {paragraph.text.strip()[:50]}...")
                        
                        # Add any inline images from this paragraph
                        for image_data in inline_images:
                            content_item = {
                                "type": "image",
                                "data": image_data
                            }
                            ordered_content.append(content_item)
                            logger.debug(f"Added inline image: {image_data.get('filename', 'unknown')}")
                
                elif element_type.endswith('tbl'):  # Table
                    table = self._get_table_from_element(element, document)
                    if table:
                        table_data = self._extract_table_data_with_images(table, document)
                        content_item = {
                            "type": "table",
                            "data": table_data
                        }
                        ordered_content.append(content_item)
                        logger.debug(f"Added table with {len(table.rows)} rows")
                
                elif element_type.endswith('drawing'):  # Standalone image or drawing
                    image_data = self._extract_image_from_element(element, document)
                    if image_data:
                        content_item = {
                            "type": "image",
                            "data": image_data
                        }
                        ordered_content.append(content_item)
                        logger.debug(f"Added standalone image: {image_data.get('filename', 'unknown')}")
            
            logger.info(f"Successfully extracted {len(ordered_content)} content elements in order")
            return ordered_content
            
        except Exception as e:
            logger.error(f"Failed to extract ordered content: {str(e)}")
            return []
    
    def _get_paragraph_from_element(self, element, document: DocumentType):
        """Get paragraph object from XML element."""
        try:
            # Find the paragraph in document.paragraphs that matches this element
            for paragraph in document.paragraphs:
                if paragraph._element == element:
                    return paragraph
            return None
        except Exception as e:
            logger.warning(f"Failed to get paragraph from element: {str(e)}")
            return None
    
    def _get_table_from_element(self, element, document: DocumentType):
        """Get table object from XML element."""
        try:
            # Find the table in document.tables that matches this element
            for table in document.tables:
                if table._element == element:
                    return table
            return None
        except Exception as e:
            logger.warning(f"Failed to get table from element: {str(e)}")
            return None
    
    def _extract_table_data(self, table) -> Dict[str, Any]:
        """Extract data from table in structured format."""
        try:
            table_data = {
                "rows": len(table.rows),
                "columns": len(table.columns),
                "cells": []
            }
            
            # Extract table content
            for row_idx, row in enumerate(table.rows):
                row_data = []
                for col_idx, cell in enumerate(row.cells):
                    cell_content = {
                        "row": row_idx,
                        "column": col_idx,
                        "text": cell.text.strip(),
                        "paragraphs": []
                    }
                    
                    # Extract paragraphs from cell
                    for paragraph in cell.paragraphs:
                        if paragraph.text.strip():
                            cell_content["paragraphs"].append({
                                "text": paragraph.text.strip(),
                                "style": paragraph.style.name if paragraph.style else "Normal"
                            })
                    
                    row_data.append(cell_content)
                table_data["cells"].append(row_data)
            
            return table_data
            
        except Exception as e:
            logger.warning(f"Failed to extract table data: {str(e)}")
            return {}

    def _extract_table_data_with_images(self, table, document: DocumentType) -> Dict[str, Any]:
        """Extract data from table including any images in cells."""
        try:
            table_data = {
                "rows": len(table.rows),
                "columns": len(table.columns),
                "cells": [],
                "images": []
            }
            
            # Extract table content
            for row_idx, row in enumerate(table.rows):
                row_data = []
                for col_idx, cell in enumerate(row.cells):
                    cell_content = {
                        "row": row_idx,
                        "column": col_idx,
                        "text": cell.text.strip(),
                        "paragraphs": []
                    }
                    
                    # Extract paragraphs from cell
                    for paragraph in cell.paragraphs:
                        if paragraph.text.strip():
                            cell_content["paragraphs"].append({
                                "text": paragraph.text.strip(),
                                "style": paragraph.style.name if paragraph.style else "Normal"
                            })
                        
                        # Check for images in this paragraph
                        inline_images = []
                        self._extract_inline_images_from_paragraph(paragraph, document, inline_images)
                        for image_data in inline_images:
                            # Add image to table images list with position info
                            image_data["table_position"] = {
                                "row": row_idx,
                                "column": col_idx
                            }
                            table_data["images"].append(image_data)
                    
                    row_data.append(cell_content)
                table_data["cells"].append(row_data)
            
            return table_data
            
        except Exception as e:
            logger.warning(f"Failed to extract table data with images: {str(e)}")
            return {}
    
    def _extract_image_from_element(self, element, document: DocumentType) -> Optional[Dict[str, Any]]:
        """Extract image data from drawing element."""
        try:
            # Look for image relationships in the drawing element
            for drawing in element.xpath('.//a:blip', namespaces={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}):
                embed_id = drawing.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                if embed_id and embed_id in document.part.rels:
                    rel = document.part.rels[embed_id]
                    if rel and rel.target_part:
                        return {
                            "filename": f"image_{len([c for c in document.element.body if c.tag.endswith('drawing')])}.png",
                            "content_type": rel.target_part.content_type,
                            "size": len(rel.target_part.blob),
                            "base64": base64.b64encode(rel.target_part.blob).decode('utf-8'),
                            "source": "drawing"
                        }
            return None
        except Exception as e:
            logger.warning(f"Failed to extract image from element: {str(e)}")
            return None
    
    def _extract_inline_images_from_paragraph_simple(self, paragraph: Paragraph, document: DocumentType) -> List[Dict[str, Any]]:
        """Extract all inline images from a paragraph (simple version that returns a list)."""
        images = []
        self._extract_inline_images_from_paragraph(paragraph, document, images, source="inline")
        return images

    def _extract_inline_image(self, run, document: DocumentType) -> Optional[Dict[str, Any]]:
        """Extract inline image from run."""
        try:
            for drawing in run._element.xpath('.//a:blip', namespaces={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}):
                embed_id = drawing.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                if embed_id and embed_id in document.part.rels:
                    rel = document.part.rels[embed_id]
                    if rel and rel.target_part:
                        return {
                            "filename": f"inline_image_{len([c for c in document.element.body if c.tag.endswith('drawing')])}.png",
                            "content_type": rel.target_part.content_type,
                            "size": len(rel.target_part.blob),
                            "base64": base64.b64encode(rel.target_part.blob).decode('utf-8'),
                            "source": "inline"
                        }
            return None
        except Exception as e:
            logger.warning(f"Failed to extract inline image: {str(e)}")
            return None
    
    def _extract_headers(self, document: DocumentType) -> List[Dict[str, Any]]:
        """Extract headers from document."""
        headers = []
        try:
            for section in document.sections:
                header = section.header
                if header:
                    header_content = []
                    for paragraph in header.paragraphs:
                        if paragraph.text.strip():
                            header_content.append({
                                "text": paragraph.text.strip(),
                                "style": paragraph.style.name if paragraph.style else "Normal"
                            })
                    
                    if header_content:
                        headers.append({
                            "content": header_content,
                            "section": len(headers) + 1
                        })
        except Exception as e:
            logger.warning(f"Failed to extract headers: {str(e)}")
        
        return headers
    
    def _extract_footers(self, document: DocumentType) -> List[Dict[str, Any]]:
        """Extract footers from document."""
        footers = []
        try:
            for section in document.sections:
                footer = section.footer
                if footer:
                    footer_content = []
                    for paragraph in footer.paragraphs:
                        if paragraph.text.strip():
                            footer_content.append({
                                "text": paragraph.text.strip(),
                                "style": paragraph.style.name if paragraph.style else "Normal"
                            })
                    
                    if footer_content:
                        footers.append({
                            "content": footer_content,
                            "section": len(footers) + 1
                        })
        except Exception as e:
            logger.warning(f"Failed to extract footers: {str(e)}")
        
        return footers
    
    def _extract_paragraphs(self, document: DocumentType) -> List[Dict[str, Any]]:
        """Extract all paragraphs from document."""
        paragraphs = []
        try:
            for i, paragraph in enumerate(document.paragraphs):
                if paragraph.text.strip():
                    paragraphs.append({
                        "index": i,
                        "text": paragraph.text.strip(),
                        "style": paragraph.style.name if paragraph.style else "Normal",
                        "alignment": str(paragraph.alignment) if paragraph.alignment else None,
                        "runs": self._extract_runs(paragraph)
                    })
        except Exception as e:
            logger.warning(f"Failed to extract paragraphs: {str(e)}")
        
        return paragraphs
    
    def _extract_runs(self, paragraph: Paragraph) -> List[Dict[str, Any]]:
        """Extract runs (formatted text) from paragraph."""
        runs = []
        try:
            for run in paragraph.runs:
                if run.text.strip():
                    runs.append({
                        "text": run.text,
                        "bold": run.bold,
                        "italic": run.italic,
                        "underline": run.underline,
                        "font_name": run.font.name if run.font.name else None,
                        "font_size": run.font.size.pt if run.font.size else None
                    })
        except Exception as e:
            logger.warning(f"Failed to extract runs: {str(e)}")
        
        return runs
    
    def _extract_tables(self, document: DocumentType) -> List[Dict[str, Any]]:
        """Extract all tables from document."""
        tables = []
        try:
            for i, table in enumerate(document.tables):
                table_data = {
                    "index": i,
                    "rows": len(table.rows),
                    "columns": len(table.columns),
                    "cells": []
                }
                
                # Extract table content
                for row_idx, row in enumerate(table.rows):
                    row_data = []
                    for col_idx, cell in enumerate(row.cells):
                        cell_content = {
                            "row": row_idx,
                            "column": col_idx,
                            "text": cell.text.strip(),
                            "paragraphs": []
                        }
                        
                        # Extract paragraphs from cell
                        for paragraph in cell.paragraphs:
                            if paragraph.text.strip():
                                cell_content["paragraphs"].append({
                                    "text": paragraph.text.strip(),
                                    "style": paragraph.style.name if paragraph.style else "Normal"
                                })
                        
                        row_data.append(cell_content)
                    table_data["cells"].append(row_data)
                
                tables.append(table_data)
        except Exception as e:
            logger.warning(f"Failed to extract tables: {str(e)}")
        
        return tables
    
    def _extract_images(self, document: DocumentType) -> List[Dict[str, Any]]:
        """Extract images from document."""
        images = []
        try:
            # Method 1: Extract from relationships
            for rel in document.part.rels.values():
                if self._is_image_relationship(rel):
                    try:
                        image_data = {
                            "filename": rel.target_ref,
                            "content_type": rel.target_part.content_type,
                            "size": len(rel.target_part.blob),
                            "base64": base64.b64encode(rel.target_part.blob).decode('utf-8'),
                            "source": "relationship"
                        }
                        images.append(image_data)
                        logger.info(f"Extracted image from relationship: {rel.target_ref}")
                    except Exception as e:
                        logger.warning(f"Failed to extract image {rel.target_ref}: {str(e)}")
            
            # Method 2: Extract from paragraphs (inline images)
            for paragraph in document.paragraphs:
                try:
                    self._extract_inline_images_from_paragraph(paragraph, document, images)
                except Exception as e:
                    logger.warning(f"Failed to extract inline images from paragraph: {str(e)}")
            
            # Method 3: Extract from tables
            for table in document.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            try:
                                self._extract_inline_images_from_paragraph(paragraph, document, images, source="table")
                            except Exception as e:
                                logger.warning(f"Failed to extract table images from paragraph: {str(e)}")
            
            logger.info(f"Successfully extracted {len(images)} images from document")
            
        except Exception as e:
            logger.warning(f"Failed to extract images: {str(e)}")
        
        return images
    
    def _extract_inline_images_from_paragraph(self, paragraph, document, images, source="inline"):
        """Extract inline images from a paragraph using a more compatible approach."""
        try:
            # Use a more compatible xpath approach
            for run in paragraph.runs:
                # Try to find drawing elements without using namespaces parameter
                try:
                    # Method 1: Try with namespaces (newer lxml versions)
                    drawings = run._element.xpath('.//a:blip', namespaces={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'})
                except TypeError:
                    # Method 2: Fallback for older lxml versions - use local-name()
                    drawings = run._element.xpath('.//*[local-name()="blip"]')
                except Exception:
                    # Method 3: Try without namespaces
                    drawings = run._element.xpath('.//blip')
                
                for drawing in drawings:
                    try:
                        # Get the relationship ID
                        embed_id = drawing.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                        if embed_id:
                            rel = document.part.rels[embed_id]
                            if rel and rel.target_part:
                                image_data = {
                                    "filename": f"{source}_image_{len(images)}.png",
                                    "content_type": rel.target_part.content_type,
                                    "size": len(rel.target_part.blob),
                                    "base64": base64.b64encode(rel.target_part.blob).decode('utf-8'),
                                    "source": source
                                }
                                images.append(image_data)
                                logger.info(f"Extracted {source} image: {image_data['filename']}")
                    except Exception as e:
                        logger.warning(f"Failed to extract {source} image: {str(e)}")
                        
        except Exception as e:
            logger.warning(f"Failed to extract {source} images from paragraph: {str(e)}")
    
    def _is_image_relationship(self, rel) -> bool:
        """Check if a relationship is an image."""
        try:
            # Check by content type
            if hasattr(rel, 'target_part') and rel.target_part:
                content_type = rel.target_part.content_type
                if content_type and content_type.startswith('image/'):
                    return True
            
            # Check by file extension
            if rel.target_ref:
                image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg')
                if rel.target_ref.lower().endswith(image_extensions):
                    return True
                
                # Check if it's in media folder (common for Word images)
                if 'media/' in rel.target_ref.lower() and any(ext in rel.target_ref.lower() for ext in image_extensions):
                    return True
            
            return False
        except Exception:
            return False
    
    def _extract_lists(self, document: DocumentType) -> List[Dict[str, Any]]:
        """Extract lists from document."""
        lists = []
        try:
            current_list = None
            list_items = []
            
            for paragraph in document.paragraphs:
                if paragraph.text.strip():
                    # Check if paragraph is part of a list
                    if paragraph.style.name.startswith('List'):
                        if current_list is None:
                            current_list = {
                                "style": paragraph.style.name,
                                "items": []
                            }
                        
                        current_list["items"].append({
                            "text": paragraph.text.strip(),
                            "level": self._get_list_level(paragraph)
                        })
                    else:
                        # End of current list
                        if current_list:
                            lists.append(current_list)
                            current_list = None
            
            # Add final list if exists
            if current_list:
                lists.append(current_list)
        except Exception as e:
            logger.warning(f"Failed to extract lists: {str(e)}")
        
        return lists
    
    def _get_list_level(self, paragraph: Paragraph) -> int:
        """Get the nesting level of a list item."""
        try:
            # This is a simplified approach - in practice, you might need more sophisticated logic
            return paragraph._element.get(qn('w:ilvl'), 0)
        except:
            return 0
    
    def _extract_comments(self, document: DocumentType) -> List[Dict[str, Any]]:
        """Extract comments from document."""
        comments = []
        try:
            # Try to extract comments from document properties
            if hasattr(document, 'comments'):
                for comment in document.comments:
                    comments.append({
                        "author": getattr(comment, 'author', 'Unknown'),
                        "date": getattr(comment, 'date', None),
                        "text": getattr(comment, 'text', ''),
                        "paragraph": getattr(comment, 'paragraph', None)
                    })
            
            logger.info(f"Extracted {len(comments)} comments from document")
            
        except Exception as e:
            logger.warning(f"Failed to extract comments: {str(e)}")
        
        return comments
    
    def _extract_footnotes(self, document: DocumentType) -> List[Dict[str, Any]]:
        """Extract footnotes from document."""
        footnotes = []
        try:
            # Try to extract footnotes from document
            if hasattr(document, 'footnotes'):
                for footnote in document.footnotes:
                    footnotes.append({
                        "text": getattr(footnote, 'text', ''),
                        "reference": getattr(footnote, 'reference', ''),
                        "paragraph": getattr(footnote, 'paragraph', None)
                    })
            
            logger.info(f"Extracted {len(footnotes)} footnotes from document")
            
        except Exception as e:
            logger.warning(f"Failed to extract footnotes: {str(e)}")
        
        return footnotes
    
    def _extract_metadata(self, document: DocumentType) -> Dict[str, Any]:
        """Extract document metadata."""
        try:
            core_props = document.core_properties
            return {
                "title": core_props.title,
                "author": core_props.author,
                "subject": core_props.subject,
                "keywords": core_props.keywords,
                "comments": core_props.comments,
                "created": core_props.created.isoformat() if core_props.created else None,
                "modified": core_props.modified.isoformat() if core_props.modified else None,
                "last_modified_by": core_props.last_modified_by,
                "revision": core_props.revision,
                "version": core_props.version
            }
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {str(e)}")
            return {}
    
    def _extract_document_structure(self, document: DocumentType) -> Dict[str, Any]:
        """Extract document structure information."""
        try:
            structure = {
                "sections": len(document.sections),
                "paragraphs_count": len([p for p in document.paragraphs if p.text.strip()]),
                "tables_count": len(document.tables),
                "images_count": len(self._extract_images(document)),
                "lists_count": len(self._extract_lists(document)),
                "headers_count": len(self._extract_headers(document)),
                "footers_count": len(self._extract_footers(document))
            }
            
            # Extract heading structure
            headings = []
            for paragraph in document.paragraphs:
                if paragraph.style.name.startswith('Heading') and paragraph.text.strip():
                    level = int(paragraph.style.name.replace('Heading ', '')) if paragraph.style.name.replace('Heading ', '').isdigit() else 1
                    headings.append({
                        "level": level,
                        "text": paragraph.text.strip(),
                        "style": paragraph.style.name
                    })
            
            structure["headings"] = headings
            return structure
            
        except Exception as e:
            logger.warning(f"Failed to extract document structure: {str(e)}")
            return {}
    
    def convert_to_document_blocks(self, processed_content: Dict[str, Any], ai_analyzed_content: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Convert processed Word document content to TipTap JSON format.
        
        Args:
            processed_content: Processed document content with ordered_content
            
        Returns:
            TipTap JSON document structure
        """
        try:
            logger.info(f"Converting processed content to TipTap JSON. Keys: {list(processed_content.keys())}")
            logger.info(f"Title: {processed_content.get('title')}")
            logger.info(f"Ordered content count: {len(processed_content.get('ordered_content', []))}")
            
            # Start with TipTap document structure
            tiptap_content = {
                "type": "doc",
                "content": []
            }
            
            # Add title as heading if exists
            if processed_content.get("title"):
                tiptap_content["content"].append({
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [{"type": "text", "text": processed_content["title"]}]
                })
            
            # Process ordered content to maintain document order
            ordered_content = processed_content.get("ordered_content", [])
            for i, content_item in enumerate(ordered_content):
                content_type = content_item.get("type")
                
                if content_type == "paragraph":
                    # Convert paragraph to TipTap format
                    paragraph_node = self._convert_paragraph_to_tiptap(content_item)
                    if paragraph_node:
                        tiptap_content["content"].append(paragraph_node)
                        logger.debug(f"Added paragraph: {content_item['text'][:50]}...")
                
                elif content_type == "table":
                    # Convert table to TipTap format
                    table_node = self._convert_table_to_tiptap(content_item["data"])
                    if table_node:
                        tiptap_content["content"].append(table_node)
                        logger.debug(f"Added table with {len(table_node.get('content', []))} rows")
                
                elif content_type == "image":
                    # Convert image to TipTap format
                    image_node = self._convert_image_to_tiptap(content_item["data"])
                    if image_node:
                        tiptap_content["content"].append(image_node)
                        logger.debug(f"Added image: {content_item['data'].get('filename', 'unknown')}")
            
            logger.info(f"Successfully converted to TipTap JSON with {len(tiptap_content['content'])} nodes")
            return tiptap_content
            
        except Exception as e:
            logger.error(f"Failed to convert to TipTap JSON: {str(e)}")
            return {"type": "doc", "content": []}
    
    def _convert_paragraph_to_tiptap(self, paragraph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert paragraph data to TipTap format."""
        try:
            style = paragraph_data.get("style", "Normal")
            text = paragraph_data.get("text", "")
            runs = paragraph_data.get("runs", [])
            alignment = paragraph_data.get("alignment")
            
            # Determine node type based on style
            if style.startswith("Heading"):
                level = int(style.replace("Heading ", "")) if style.replace("Heading ", "").isdigit() else 1
                return {
                    "type": "heading",
                    "attrs": {"level": level},
                    "content": self._convert_runs_to_tiptap(runs) if runs else [{"type": "text", "text": text}]
                }
            elif style.startswith("List"):
                return {
                    "type": "bulletList",
                    "content": [{
                        "type": "listItem",
                        "content": [{
                            "type": "paragraph",
                            "content": self._convert_runs_to_tiptap(runs) if runs else [{"type": "text", "text": text}]
                        }]
                    }]
                }
            else:
                # Regular paragraph
                attrs = {}
                if alignment and alignment != "None":
                    attrs["textAlign"] = alignment.lower()
                
                # Convert content normally
                content = self._convert_runs_to_tiptap(runs) if runs else [{"type": "text", "text": text}]
                
                return {
                    "type": "paragraph",
                    "attrs": attrs if attrs else None,
                    "content": content
                }
        except Exception as e:
            logger.warning(f"Failed to convert paragraph to TipTap: {str(e)}")
            return {
                "type": "paragraph",
                "content": [{"type": "text", "text": paragraph_data.get("text", "")}]
            }
    
    
    def _convert_runs_to_tiptap(self, runs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert paragraph runs to TipTap text nodes with marks."""
        try:
            if not runs:
                return [{"type": "text", "text": ""}]
            
            tiptap_nodes = []
            for run in runs:
                text = run.get("text", "")
                if not text:
                    continue
                
                # Build marks array
                marks = []
                if run.get("bold"):
                    marks.append({"type": "bold"})
                if run.get("italic"):
                    marks.append({"type": "italic"})
                if run.get("underline"):
                    marks.append({"type": "underline"})
                
                node = {
                    "type": "text",
                    "text": text
                }
                if marks:
                    node["marks"] = marks
                
                tiptap_nodes.append(node)
            
            return tiptap_nodes if tiptap_nodes else [{"type": "text", "text": ""}]
        except Exception as e:
            logger.warning(f"Failed to convert runs to TipTap: {str(e)}")
            return [{"type": "text", "text": ""}]
    
    def _convert_table_to_tiptap(self, table_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert table data to TipTap table format."""
        try:
            if not table_data.get("cells"):
                return None
            
            table_content = []
            
            # Convert each row
            for row_idx, row in enumerate(table_data["cells"]):
                row_content = []
                
                # Convert each cell in the row
                for col_idx, cell in enumerate(row):
                    cell_content = []
                    
                    # Add cell text as paragraph (always include at least empty paragraph)
                    cell_text = cell.get("text", "").strip() if isinstance(cell, dict) else str(cell).strip()
                    cell_content.append({
                        "type": "paragraph",
                        "content": [{"type": "text", "text": cell_text}] if cell_text else []
                    })
                    
                    # Add any images from this cell
                    if "images" in table_data:
                        for image_data in table_data["images"]:
                            if (image_data.get("table_position", {}).get("row") == row_idx and 
                                image_data.get("table_position", {}).get("column") == col_idx):
                                image_node = self._convert_image_to_tiptap(image_data)
                                if image_node:
                                    cell_content.append(image_node)
                    
                    row_content.append({
                        "type": "tableCell",
                        "content": cell_content
                    })
                
                table_content.append({
                    "type": "tableRow",
                    "content": row_content
                })
            
            return {
                "type": "table",
                "content": table_content
            }
        except Exception as e:
            logger.warning(f"Failed to convert table to TipTap: {str(e)}")
            return None
    
    def _convert_image_to_tiptap(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert image data to TipTap image format."""
        try:
            return {
                "type": "image",
                "attrs": {
                    "src": f"data:{image_data['content_type']};base64,{image_data['base64']}",
                    "alt": image_data.get("filename", "image"),
                    "title": image_data.get("filename", "")
                }
            }
        except Exception as e:
            logger.warning(f"Failed to convert image to TipTap: {str(e)}")
            return None
    
    def _table_to_structure_from_ordered(self, table_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert table data from ordered content to frontend-compatible structure."""
        try:
            if not table_data.get("cells"):
                return {}
            
            # Extract headers from first row
            headers = []
            rows = []
            
            if table_data["cells"]:
                # First row is headers
                header_row = table_data["cells"][0]
                headers = [cell["text"] for cell in header_row]
                
                # Remaining rows are data
                for row in table_data["cells"][1:]:
                    row_cells = [cell["text"] for cell in row]
                    rows.append(row_cells)
            
            return {
                "headers": headers,
                "rows": rows
            }
            
        except Exception as e:
            logger.warning(f"Failed to convert table to structure from ordered content: {str(e)}")
            return {}
    
    def _table_to_structure(self, table: Dict[str, Any]) -> Dict[str, Any]:
        """Convert table to frontend-compatible structure."""
        try:
            if not table.get("cells"):
                return {}
            
            # Extract headers from first row
            headers = []
            rows = []
            
            if table["cells"]:
                # First row is headers
                header_row = table["cells"][0]
                headers = [cell["text"] for cell in header_row]
                
                # Remaining rows are data
                for row in table["cells"][1:]:
                    row_cells = [cell["text"] for cell in row]
                    rows.append(row_cells)
            
            return {
                "headers": headers,
                "rows": rows
            }
            
        except Exception as e:
            logger.warning(f"Failed to convert table to structure: {str(e)}")
            return {}
    
    def _table_to_markdown(self, table: Dict[str, Any]) -> str:
        """Convert table to markdown format."""
        try:
            if not table.get("cells"):
                return ""
            
            markdown_lines = []
            
            # Add header row
            if table["cells"]:
                header_row = table["cells"][0]
                header_cells = [cell["text"] for cell in header_row]
                markdown_lines.append("| " + " | ".join(header_cells) + " |")
                markdown_lines.append("| " + " | ".join(["---"] * len(header_cells)) + " |")
                
                # Add data rows
                for row in table["cells"][1:]:
                    row_cells = [cell["text"] for cell in row]
                    markdown_lines.append("| " + " | ".join(row_cells) + " |")
            
            return "\n".join(markdown_lines)
            
        except Exception as e:
            logger.warning(f"Failed to convert table to markdown: {str(e)}")
            return ""
    
    def _convert_text_to_tiptap(self, text: str) -> Dict[str, Any]:
        """Convert plain text to TipTap format."""
        try:
            if not text or not text.strip():
                return {"type": "doc", "content": []}
            
            # Split text into paragraphs
            paragraphs = text.split('\n\n')
            tiptap_content = []
            
            for para in paragraphs:
                para = para.strip()
                if para:
                    # Check if it's a heading (starts with # or is all caps and short)
                    if para.startswith('#'):
                        # Markdown heading
                        level = len(para) - len(para.lstrip('#'))
                        level = min(level, 6)  # Max heading level is 6
                        heading_text = para.lstrip('#').strip()
                        tiptap_content.append({
                            "type": "heading",
                            "attrs": {"level": level},
                            "content": [{"type": "text", "text": heading_text}]
                        })
                    elif para.isupper() and len(para) < 100:
                        # Likely a heading (all caps and short)
                        tiptap_content.append({
                            "type": "heading",
                            "attrs": {"level": 2},
                            "content": [{"type": "text", "text": para}]
                        })
                    else:
                        # Regular paragraph
                        tiptap_content.append({
                            "type": "paragraph",
                            "content": [{"type": "text", "text": para}]
                        })
            
            return {
                "type": "doc",
                "content": tiptap_content if tiptap_content else [{"type": "paragraph", "content": [{"type": "text", "text": ""}]}]
            }
        except Exception as e:
            logger.warning(f"Failed to convert text to TipTap: {str(e)}")
            return {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}]}