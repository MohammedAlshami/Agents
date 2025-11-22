"""
Section mapper using AI to map chunks to sections.
Uses OpenAI to classify document chunks and provide mapping instructions.
"""

import os
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import math

from .document_extractor import DocumentChunk

load_dotenv()
logger = logging.getLogger(__name__)


class ChunkMapping(BaseModel):
    """Mapping instruction telling Python where to extract content using ID ranges."""
    chunk_index: int = Field(description="Index of the chunk (0-based, usually 0 for full document)")
    section: str = Field(description="Section name to assign: 'title', 'abstract', 'introduction', 'literature_review', 'research_model', 'methodology', 'data_analysis', 'discussion', 'conclusion', 'references', or 'none'")
    start_id: Optional[str] = Field(default=None, description="Start ID (e.g., 'id1', 'TABLE_1', 'IMAGE_1')")
    end_id: Optional[str] = Field(default=None, description="End ID (e.g., 'id50', 'TABLE_1', 'IMAGE_1')")
    notes: Optional[str] = Field(default=None, description="Classification notes")


class ContentMapping(BaseModel):
    """Complete mapping instructions for all chunks."""
    mappings: List[ChunkMapping] = Field(description="List of mapping instructions")


class SectionMapper:
    """Maps document chunks to sections using AI classification."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key"""
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not provided")
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=api_key
        )
    
    def create_mapping_chain(self, sections: List[str]) -> Runnable:
        """Create mapping chain with structured output"""
        
        # Build sections list for prompt
        sections_list = []
        section_descriptions = {
            "title": "Title of the document (usually at the beginning)",
            "abstract": "Abstract section (may be labeled as \"ABSTRACT\", \"Abstract\", etc.)",
            "introduction": "Introduction section (may be labeled as \"1. INTRODUCTION\", \"INTRODUCTION\", \"1. Introduction\", etc.)",
            "literature_review": "Literature Review section (may be labeled as \"2. LITERATURE REVIEW\", \"LITERATURE REVIEW\", \"Literature Review\", etc.)",
            "research_model": "Research Model and Hypotheses section (may be labeled as \"3. RESEARCH MODEL\", \"RESEARCH MODEL\", \"Research Model\", etc.)",
            "methodology": "Methodology section (may be labeled as \"4. METHODOLOGY\", \"METHODOLOGY\", \"Methodology\", etc.)",
            "data_analysis": "Data Analysis and Results section (may be labeled as \"5. DATA ANALYSIS\", \"DATA ANALYSIS\", \"Results\", \"Data Analysis\", etc.)",
            "discussion": "Discussion and Implications section (may be labeled as \"6. DISCUSSION\", \"DISCUSSION\", \"Discussion\", etc.)",
            "conclusion": "Conclusion section (may be labeled as \"7. CONCLUSION\", \"CONCLUSION\", \"Conclusion\", etc.)",
            "references": "References list (may be labeled as \"REFERENCES\", \"References\", \"Bibliography\", \"Works Cited\", etc.). This section contains a numbered or bulleted list of citations/references, typically at the end of the document. Each reference usually contains author names, publication year, title, journal/book name, etc. DO NOT confuse this with regression analysis, data analysis, or other content sections.",
        }
        
        # Always include title and abstract if not in sections
        sections_to_use = list(sections)
        if "title" not in sections_to_use:
            sections_to_use.insert(0, "title")
        if "abstract" not in sections_to_use:
            sections_to_use.insert(1, "abstract")
        
        for section in sections_to_use:
            if section in section_descriptions:
                sections_list.append(f"- {section}: {section_descriptions[section]}")
        
        sections_list.append("- none: Content that doesn't belong to any section")
        sections_text = "\n".join(sections_list)
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"""You are a document classifier. Your ONLY job is to classify document content and tell Python where to extract content using ID ranges.

IMPORTANT: 
- You MUST NOT generate or create any text content. You ONLY classify existing content and tell Python which ID ranges to extract.
- The document content is numbered with IDs like [id1], [id2], [id3], etc. Each segment has a unique ID.
- Tables have IDs like [TABLE_1], [TABLE_2], etc.
- Images have IDs like [IMAGE_1], [IMAGE_2], etc. (already placeholders, ignore them for classification)
- You need to tell Python which ID ranges belong to each section.
- EXCLUDE section headings/titles from the ID ranges. For example, if you see "ABSTRACT" as a heading, exclude that ID from the abstract section content. Only include the actual content, not the section title.

You ONLY classify content and tell Python:
- Which chunk index contains each section (usually 0 for full document)
- Which ID range to extract (start_id and end_id)
- Which section name to assign

Sections (in order):
{sections_text}

IMPORTANT: Look for section headings in the document. They may appear as:
- Numbered headings (e.g., "1. INTRODUCTION", "2. LITERATURE REVIEW")
- Unnumbered headings (e.g., "INTRODUCTION", "LITERATURE REVIEW")
- Mixed case (e.g., "Introduction", "Literature Review")
- With or without periods/colons

CRITICAL FOR REFERENCES SECTION:
- The references section is typically at the END of the document, AFTER conclusion, recommendations, acknowledgments, etc.
- Look for headings like "REFERENCE", "REFERENCES", "Bibliography", "Works Cited" - these indicate the start of the references section
- After finding a "REFERENCE" or "REFERENCES" heading, ALL content that follows (until the end of the document) is the references list
- The references section contains a LIST of citations/references (usually numbered 1, 2, 3... or formatted as citations)
- Each reference typically contains: author names, year, title, journal/book, pages, DOI, etc.
- References section does NOT contain regression analysis, statistical analysis, or data analysis content
- If you see content like "4.3 Regression analysis" or statistical analysis, that is NOT the references section
- The actual references list comes AFTER all analysis sections, recommendations, acknowledgments, etc., usually at the very end
- IMPORTANT: If you see a heading "REFERENCE" or "REFERENCES", map ALL content that comes after it (until the end) to the references section

You MUST map ALL content to appropriate sections. If content doesn't fit any section, map it to "none". Do not leave sections empty if content exists!

Your output should ONLY contain:
- chunk_index: Which chunk (0-based index) contains this section (usually 0)
- section: Which section name it belongs to
- start_id: First ID in the range (e.g., 'id1', 'TABLE_1') - required
- end_id: Last ID in the range (e.g., 'id50', 'TABLE_1') - required. If single segment, use same value as start_id.
- notes: Optional - brief classification notes (NOT content)

CRITICAL: You MUST map ALL tables to their appropriate sections. Tables are numbered as TABLE_1, TABLE_2, TABLE_3, etc. Each table should be mapped to the section where it appears (e.g., methodology, data_analysis, etc.). Do NOT skip tables!

DO NOT generate any actual text content. Python will extract the actual text from the chunks based on your ID range instructions."""),
            ("human", """Classify the following document content and tell Python which ID ranges to extract for each section:

{{chunks_text}}

The document content is numbered with IDs like [id1], [id2], [TABLE_1], [IMAGE_1], etc.

For each section you find, provide ONLY classification/mapping instructions:
1. chunk_index: The chunk number (0-based, usually 0)
2. section: Which section name this content belongs to
3. start_id: First ID in the range (e.g., "id1", "id10", "TABLE_1") - REQUIRED
4. end_id: Last ID in the range (e.g., "id50", "id100", "TABLE_1") - REQUIRED. If single segment, use same as start_id.
5. notes: (Optional) Brief classification note (e.g., "title section", "introduction section", NOT actual text)

Return mappings for all sections you find. Use ID ranges like:
- title: id1 to id5
- abstract: id11 to id15 (EXCLUDE the "ABSTRACT" heading if it exists as a separate ID)
- introduction: id16 to id50 (EXCLUDE the "INTRODUCTION" or "1. INTRODUCTION" heading)
- references: id96 to id127 (if you see "REFERENCE" at id95, map id96 to id127 - ALL IDs from id96 to the last ID)
- etc.

CONCRETE EXAMPLE FOR REFERENCES:
- If the document has IDs from id1 to id127
- And you see "[id95] REFERENCE" (just the heading)
- Then the references section is id96 to id127 (ALL 32 IDs: id96, id97, id98, ..., id127)
- You MUST create a mapping: references section = id96 to id127
- DO NOT create multiple mappings - create ONE mapping that covers id96 to id127

SPECIFIC INSTRUCTION FOR REFERENCES:
- Scan the document from the END backwards
- Look for a segment that contains ONLY "REFERENCE" or "REFERENCES" (this is the heading)
- Once you find this heading (e.g., at id95), map ALL content that comes AFTER it (e.g., id96 to the last ID in the document) to the references section
- CRITICAL: You MUST map ALL IDs from the "REFERENCE" heading until the very last ID in the document to the references section
- DO NOT map any content that comes BEFORE the "REFERENCE" or "REFERENCES" heading to references
- If you see "REFERENCE" at id95, then references section is id96 to the last ID in the document (e.g., if last ID is id127, then map id96 to id127)
- EXAMPLE: If you see "[id95] REFERENCE" followed by "[id96] Al-Dmour, R., AlShaar, F...", and the last ID is id127, then map id96 to id127 as references
- The references section should contain citations like "Al-Dmour, R., AlShaar, F...", "Albrecht, S. L., Bakker, A. B...", etc.
- DO NOT map content about "regression", "ANOVA", "coefficients", "recommendations", "acknowledgments" to references
- IMPORTANT: If the document has 127 IDs total and "REFERENCE" is at id95, then the references section MUST include id96, id97, id98, ... all the way to id127

CRITICAL: For each table you find (TABLE_1, TABLE_2, etc.), you MUST create a mapping entry that includes it in the appropriate section. Do NOT skip tables!

CRITICAL FOR REFERENCES - FOLLOW THESE STEPS EXACTLY:
1. FIRST: Scan the document from the END backwards, looking for a segment that contains ONLY "REFERENCE" or "REFERENCES" (this is the heading)
2. Once you find this heading (e.g., at id95), note its ID number
3. Find the LAST ID in the document (e.g., id127)
4. Map ALL IDs from (heading_id + 1) to the last ID to the references section
   - EXAMPLE: If "REFERENCE" is at id95 and last ID is id127, then map id96 to id127 as references
   - This means: references section = id96, id97, id98, ..., id127 (ALL of them)
5. DO NOT map the "REFERENCE" heading itself (id95) to references - only map content AFTER it
6. DO NOT map any content that comes BEFORE the "REFERENCE" or "REFERENCES" heading to references
7. The references section should contain citations like "Al-Dmour, R., AlShaar, F...", "Albrecht, S. L., Bakker, A. B...", etc.
8. DO NOT map content about "regression", "ANOVA", "coefficients", "recommendations", "acknowledgments" to references
9. If you see content about "ANOVA", "regression", "coefficients", "R square", "F=9.048", that is NOT references - it's data_analysis or discussion
10. If you cannot find a clear "REFERENCE" or "REFERENCES" heading at the end, do NOT map any content to references - leave it empty

IMPORTANT: 
- When mapping sections, exclude section headings/titles from the content. Only include the actual content text, not headings like "ABSTRACT", "INTRODUCTION", etc.
- INCLUDE tables in the appropriate sections. If a table (e.g., TABLE_1, TABLE_2) belongs to a section, include it in that section's ID range.
- If content doesn't fit any requested section, map it to "none".
- For references: Only map the actual references list (citations), not analysis or discussion about references

DO NOT generate any actual text - only provide ID range instructions."""),
        ])
        
        structured_llm = self.llm.with_structured_output(ContentMapping)
        chain = prompt_template | structured_llm
        return chain
    
    def _split_chunk_into_subchunks(self, chunk: DocumentChunk, num_chunks: int = 6) -> List[DocumentChunk]:
        """
        Split a large chunk into smaller subchunks for parallel processing.
        
        Args:
            chunk: The document chunk to split
            num_chunks: Number of subchunks to create (default: 6)
            
        Returns:
            List of subchunks
        """
        if not chunk.id_to_content:
            return [chunk]
        
        # Get all IDs in order
        all_ids = sorted(chunk.id_to_content.keys(), key=lambda x: (
            int(x[2:]) if x.startswith('id') and x[2:].isdigit() else 999999,
            x
        ))
        
        if len(all_ids) <= num_chunks:
            return [chunk]
        
        # Split IDs into roughly equal chunks
        chunk_size = math.ceil(len(all_ids) / num_chunks)
        subchunks = []
        
        for i in range(0, len(all_ids), chunk_size):
            chunk_ids = all_ids[i:i + chunk_size]
            
            # Create subchunk content
            subchunk_id_to_content = {id_key: chunk.id_to_content[id_key] for id_key in chunk_ids}
            subchunk_id_to_table_data = {}
            if chunk.id_to_table_data:
                subchunk_id_to_table_data = {id_key: chunk.id_to_table_data[id_key] 
                                            for id_key in chunk_ids 
                                            if id_key in chunk.id_to_table_data}
            
            # Create numbered content for this subchunk
            numbered_content_list = [f"[{id_key}] {content}" 
                                    for id_key, content in subchunk_id_to_content.items()]
            numbered_content = "\n".join(numbered_content_list)
            
            # Create subchunk
            subchunk = DocumentChunk(
                page_number=chunk.page_number,
                content="\n".join(subchunk_id_to_content.values()),
                numbered_content=numbered_content,
                id_to_content=subchunk_id_to_content,
                id_to_table_data=subchunk_id_to_table_data if subchunk_id_to_table_data else None,
                has_table=bool(subchunk_id_to_table_data),
                has_image=chunk.has_image,
                table_placeholder=chunk.table_placeholder,
                image_placeholder=chunk.image_placeholder
            )
            subchunks.append(subchunk)
        
        logger.info(f"Split chunk into {len(subchunks)} subchunks for parallel processing")
        return subchunks
    
    def _map_single_chunk(self, chunk: DocumentChunk, sections: List[str], chunk_index: int) -> ContentMapping:
        """
        Map a single chunk using AI (for parallel processing).
        
        Args:
            chunk: The chunk to map
            sections: List of section names
            chunk_index: Index of this chunk
            
        Returns:
            ContentMapping for this chunk
        """
        chunk_info = f"Document Content with IDs (Chunk {chunk_index}):\n"
        if chunk.has_table:
            chunk_info += f"[Contains TABLE(s): {chunk.table_placeholder}]\n"
        if chunk.has_image:
            chunk_info += f"[Contains IMAGE(s): {chunk.image_placeholder} - Images replaced with placeholders]\n"
        chunk_info += f"\nEach segment below is numbered with an ID in brackets [idX], [TABLE_X], or [IMAGE_X].\n"
        chunk_info += f"Use these IDs to specify which segments belong to each section.\n\n"
        chunk_info += chunk.numbered_content
        
        mapping_chain = self.create_mapping_chain(sections)
        mapping = mapping_chain.invoke({"chunks_text": chunk_info})
        
        # Adjust chunk_index in mappings to match original chunk
        for mapping_item in mapping.mappings:
            mapping_item.chunk_index = 0  # All subchunks belong to original chunk 0
        
        return mapping
    
    def map_chunks(self, chunks: List[DocumentChunk], sections: Optional[List[str]] = None, parallel: bool = True, num_parallel_chunks: int = 6) -> ContentMapping:
        """
        Get classification/mapping instructions from AI for document chunks.
        
        OpenAI classifies chunks and provides instructions telling Python where
        to extract content. OpenAI does NOT generate text - only provides mapping.
        
        Args:
            chunks: List of document chunks to classify
            sections: Optional list of section names to extract. If None, uses default sections.
            parallel: Whether to use parallel processing (default: True)
            num_parallel_chunks: Number of parallel chunks to process (default: 6)
            
        Returns:
            ContentMapping with classification/mapping instructions
        """
        logger.info("Getting classification instructions from AI")
        logger.info(f"Total chunks to classify: {len(chunks)}")
        
        # Prepare sections list - always include references
        if sections is None:
            sections = []
        
        normalized_sections = [s.lower().strip() for s in sections if s and s.strip()]
        if 'references' not in normalized_sections:
            normalized_sections.append('references')
        
        logger.info(f"Classifying content for sections: {normalized_sections}")
        
        if not chunks:
            logger.warning("No chunks to classify")
            return ContentMapping(mappings=[])
        
        # For parallel processing, split the first chunk into subchunks
        if parallel and len(chunks) == 1 and chunks[0].id_to_content and len(chunks[0].id_to_content) > 50:
            logger.info(f"Using parallel processing: splitting document into {num_parallel_chunks} chunks")
            subchunks = self._split_chunk_into_subchunks(chunks[0], num_parallel_chunks)
            
            # Process subchunks in parallel
            all_mappings = []
            with ThreadPoolExecutor(max_workers=min(num_parallel_chunks, 8)) as executor:
                future_to_chunk = {
                    executor.submit(self._map_single_chunk, subchunk, normalized_sections, i): i
                    for i, subchunk in enumerate(subchunks)
                }
                
                for future in as_completed(future_to_chunk):
                    chunk_idx = future_to_chunk[future]
                    try:
                        mapping = future.result()
                        all_mappings.extend(mapping.mappings)
                        logger.info(f"Completed AI classification for chunk {chunk_idx} ({len(mapping.mappings)} mappings)")
                    except Exception as e:
                        logger.error(f"Error classifying chunk {chunk_idx}: {str(e)}")
            
            # Combine all mappings
            combined_mapping = ContentMapping(mappings=all_mappings)
            logger.info(f"Parallel classification completed. Total mappings: {len(combined_mapping.mappings)}")
        else:
            # Original sequential processing
            chunks_text = []
            for idx, chunk in enumerate(chunks):
                chunk_info = f"Document Content with IDs (Full Document):\n"
                if chunk.has_table:
                    chunk_info += f"[Contains TABLE(s): {chunk.table_placeholder}]\n"
                if chunk.has_image:
                    chunk_info += f"[Contains IMAGE(s): {chunk.image_placeholder} - Images replaced with placeholders]\n"
                chunk_info += f"\nEach segment below is numbered with an ID in brackets [idX], [TABLE_X], or [IMAGE_X].\n"
                chunk_info += f"Use these IDs to specify which segments belong to each section.\n\n"
                chunk_info += chunk.numbered_content
                chunks_text.append(chunk_info)
            
            chunks_text_combined = "\n\n---\n\n".join(chunks_text)
            logger.info(f"Prepared {len(chunks)} chunk(s) for AI classification with ID numbering")
            logger.info(f"Total segments: {len(chunks[0].id_to_content) if chunks else 0}")
            
            logger.info("Invoking AI to classify chunks and provide mapping instructions...")
            mapping_chain = self.create_mapping_chain(normalized_sections)
            combined_mapping = mapping_chain.invoke({"chunks_text": chunks_text_combined})
        
        logger.info(f"Classification completed. AI provided {len(combined_mapping.mappings)} mapping instructions")
        
        # Log references section mappings specifically
        references_mappings = [m for m in combined_mapping.mappings if m.section.lower() == "references"]
        if references_mappings:
            logger.info(f"Found {len(references_mappings)} mapping(s) for references section:")
            for ref_map in references_mappings:
                logger.info(f"  References: {ref_map.start_id} to {ref_map.end_id} (notes: {ref_map.notes})")
        else:
            logger.warning("WARNING: No references section mapping found! References may not be extracted.")
        
        logger.info("Python will now extract actual content from chunks based on these instructions")
        
        return combined_mapping

