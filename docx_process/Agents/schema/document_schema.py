"""
Main document schema for complete document structure.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from .content_blocks import ContentBlock
from .base_schemas import TableSchema, ListItemSchema

class DocumentSchema(BaseModel):
    """Schema for a complete document with multiple content blocks"""
    title: Optional[str] = Field(default=None, description="Document title")
    blocks: List[ContentBlock] = Field(description="Ordered list of content blocks")
    
    def add_paragraph(self, text: str) -> None:
        """Add a paragraph block"""
        order = len(self.blocks) + 1
        self.blocks.append(ContentBlock(
            order=order,
            block_type="paragraph",
            content=text
        ))
    
    def add_heading(self, level: int, text: str) -> None:
        """Add a heading block (h1 or h2)"""
        order = len(self.blocks) + 1
        block_type = f"h{level}" if level in [1, 2] else "h1"
        self.blocks.append(ContentBlock(
            order=order,
            block_type=block_type,
            content=text
        ))
    
    def add_table(self, headers: List[str], rows: List[List[str]]) -> None:
        """Add a table block"""
        order = len(self.blocks) + 1
        self.blocks.append(ContentBlock(
            order=order,
            block_type="table",
            table=TableSchema(headers=headers, rows=rows)
        ))
    
    def add_list(self, items: List[str], ordered: bool = True) -> None:
        """Add a list block (ordered or unordered)"""
        order = len(self.blocks) + 1
        block_type = "ordered_list" if ordered else "unordered_list"
        list_items = [ListItemSchema(id=str(i+1), text=item) for i, item in enumerate(items)]
        self.blocks.append(ContentBlock(
            order=order,
            block_type=block_type,
            list_items=list_items
        ))
    
    def to_dict(self) -> dict:
        """Convert DocumentSchema to a JSON-serializable dictionary"""
        return {
            'title': self.title,
            'blocks': [block.to_dict() if hasattr(block, 'to_dict') else block.dict() for block in self.blocks]
        }
    
    @property
    def content(self) -> str:
        """Get the content as a string for backward compatibility"""
        content_parts = []
        for block in self.blocks:
            if hasattr(block, 'content') and block.content:
                content_parts.append(str(block.content))
            elif hasattr(block, 'text') and block.text:
                content_parts.append(str(block.text))
        return '\n\n'.join(content_parts)
