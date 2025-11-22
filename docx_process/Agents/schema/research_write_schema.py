"""
Research Write Schema for AI-generated research content.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Reference(BaseModel):
    """Schema for a reference."""
    title: str = Field(description="Title of the reference")
    authors: List[str] = Field(description="List of authors")
    year: int = Field(description="Publication year")
    journal: Optional[str] = Field(default=None, description="Journal name")
    doi: Optional[str] = Field(default=None, description="DOI")
    url: Optional[str] = Field(default=None, description="URL")
    citation_count: Optional[int] = Field(default=None, description="Number of citations")

class Section(BaseModel):
    """Schema for a paper section."""
    title: str = Field(description="Section title")
    content: str = Field(description="Section content")

class ResearchPaper(BaseModel):
    """Schema for a complete research paper."""
    title: str = Field(description="The title of the research paper")
    abstract: str = Field(description="A comprehensive abstract of the research")
    introduction: str = Field(description="Introduction section")
    literature_review: str = Field(description="Literature review section")
    methodology: str = Field(description="Methodology section")
    results: str = Field(description="Results section")
    discussion: str = Field(description="Discussion section")
    conclusion: str = Field(description="Conclusion section")
    references: List[Reference] = Field(default=[], description="List of references used")
    word_count: int = Field(description="Total word count of the paper")
    sections: List[Section] = Field(default=[], description="List of all sections with titles and content")

class Metadata(BaseModel):
    """Schema for metadata about the generation process."""
    execution_time: float = Field(description="Time taken to generate the paper")
    timestamp: str = Field(description="Timestamp of generation")
    sources_used: int = Field(description="Number of sources used")
    q_rating: str = Field(description="Q rating used")
    target_word_count: int = Field(description="Target word count")

class ResearchWriteOutput(BaseModel):
    """Schema for the complete research paper output."""
    research_paper: ResearchPaper = Field(description="The complete research paper")
    metadata: Metadata = Field(description="Metadata about the generation process")
