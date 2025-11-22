"""
Content blocks schema for document structure.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class ContentBlockType(str, Enum):
    """Available content block types."""
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    LIST = "list"
    TABLE = "table"
    IMAGE = "image"
    CODE = "code"
    QUOTE = "quote"
    DIVIDER = "divider"

class ContentBlock(BaseModel):
    """Schema for a content block within a document."""
    order: int = Field(description="Order of the block in the document")
    block_type: ContentBlockType = Field(description="Type of content block")
    content: str = Field(description="Main content of the block")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata for the block")
    
    class Config:
        use_enum_values = True
