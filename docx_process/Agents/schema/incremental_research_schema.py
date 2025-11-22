"""
Incremental Research Write Schema for section-by-section paper generation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ResearchSection(BaseModel):
    """Schema for a single research paper section."""
    section_name: str = Field(description="The name of the section (e.g., 'Introduction', 'Literature Review')")
    content: str = Field(description="The complete content of the section")
    word_count: int = Field(description="Word count of this section")
    citations_used: List[str] = Field(default=[], description="List of citations used in this section")
    key_points: List[str] = Field(default=[], description="Key points covered in this section")

class IncrementalResearchMetadata(BaseModel):
    """Schema for metadata about the generation process."""
    execution_time: float = Field(description="Time taken to generate the section")
    timestamp: str = Field(description="Timestamp of generation")
    word_count: int = Field(description="Target word count for this section")
    section_type: str = Field(description="Type of section (main or subsection)")
    context_length: int = Field(description="Length of previous context used")

class IncrementalResearchOutput(BaseModel):
    """Schema for incremental research section output."""
    section: ResearchSection = Field(description="The generated research section")
    metadata: IncrementalResearchMetadata = Field(description="Metadata about the generation process")
    context_summary: str = Field(description="Summary of how this section builds on previous context")
