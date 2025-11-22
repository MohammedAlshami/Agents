"""
Table of Contents Schema for AI-generated hierarchical content structure.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SubSection(BaseModel):
    """Schema for a subsection."""
    title: str = Field(description="Title of the subsection")
    description: str = Field(description="Brief description of what this subsection covers")
    word_count_estimate: int = Field(description="Estimated word count for this subsection")
    key_points: List[str] = Field(default=[], description="Key points to cover in this subsection")

class Section(BaseModel):
    """Schema for a main section."""
    title: str = Field(description="Title of the section")
    description: str = Field(description="Brief description of what this section covers")
    word_count_estimate: int = Field(description="Estimated word count for this section")
    subsections: List[SubSection] = Field(default=[], description="List of subsections within this section")
    key_points: List[str] = Field(default=[], description="Key points to cover in this section")

class TableOfContents(BaseModel):
    """Schema for a complete table of contents."""
    title: str = Field(description="The title of the research paper")
    abstract: str = Field(description="Brief abstract of the research")
    total_word_count: int = Field(description="Total estimated word count")
    sections: List[Section] = Field(description="List of main sections")
    methodology_approach: str = Field(description="Description of the research methodology approach")
    expected_outcomes: List[str] = Field(default=[], description="Expected research outcomes")

class Metadata(BaseModel):
    """Schema for metadata about the generation process."""
    execution_time: float = Field(description="Time taken to generate the table of contents")
    timestamp: str = Field(description="Timestamp of generation")
    word_count: int = Field(description="Target word count")
    number_of_sections: int = Field(description="Number of main sections generated")
    total_subsections: int = Field(description="Total number of subsections generated")

class TableOfContentsOutput(BaseModel):
    """Schema for the complete table of contents output."""
    success: bool = Field(description="Whether the generation was successful")
    table_of_contents: TableOfContents = Field(description="The complete table of contents")
    metadata: Metadata = Field(description="Metadata about the generation process")
