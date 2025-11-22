"""
Base schemas for fundamental data structures used in document elements.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class TableSchema(BaseModel):
    """Schema for table structure"""
    headers: List[str] = Field(description="Table headers")
    rows: List[List[str]] = Field(description="Table rows as list of lists")

class ListItemSchema(BaseModel):
    """Schema for list item structure"""
    id: str = Field(description="Item ID")
    text: str = Field(description="Item text")

class QuerySchema(BaseModel):
    """Schema for generating search queries."""
    query: str = Field(description="The search query to retrieve relevant documents")
    reasoning: str = Field(description="Brief explanation of why this query was generated")

class ReferenceSchema(BaseModel):
    """Schema for a single reference document."""
    title: Optional[str] = Field(default=None, description="The title of the reference document")
    authors: Optional[str] = Field(default=None, description="The authors of the document")
    url: Optional[str] = Field(default=None, description="The URL of the reference document")
    abstract: Optional[str] = Field(default=None, description="The abstract of the document")
    text_snippet: str = Field(description="A snippet of the document content")
    source: Optional[str] = Field(default=None, description="The source of the document (e.g., Perplexity, Pinecone)")
    year: Optional[float] = Field(default=None, description="The publication year")

class ReferencesSchema(BaseModel):
    """Schema for a collection of reference documents."""
    references: List[ReferenceSchema] = Field(description="List of reference documents used")

