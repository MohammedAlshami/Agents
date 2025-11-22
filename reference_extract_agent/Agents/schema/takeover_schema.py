"""
Schema definitions for takeover document generation system.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class ProjectData(BaseModel):
    """Schema for project data used in takeover document generation."""
    
    project_id: str = Field(..., description="Unique identifier for the project")
    project_name: Optional[str] = Field(None, description="Name of the project")
    target_company: Optional[str] = Field(None, description="Name of the target company")
    offeror: Optional[str] = Field(None, description="Name of the offeror company")
    offer_price: Optional[str] = Field(None, description="Offer price per share")
    questions_answers: Dict[str, str] = Field(default_factory=dict, description="Project-specific Q&A data")
    additional_data: Dict[str, Any] = Field(default_factory=dict, description="Additional project data")


class Block(BaseModel):
    """Schema for individual document blocks."""
    
    order: int = Field(..., description="Order of the block")
    block_type: str = Field(..., description="Type of block (paragraph, h1, h2, h3, bullet_item, box, etc.)")
    content: str = Field(..., description="Content of the block")
    alignment: Optional[str] = Field(default="left", description="Text alignment")
    variables: Optional[Dict[str, str]] = Field(None, description="Variables for dynamic content")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the block")
    
    class Config:
        json_schema_extra = {
            "example": {
                "order": 1,
                "block_type": "paragraph",
                "content": "This is a sample paragraph",
                "alignment": "left",
                "variables": {"company_name": "TechCorp Ltd"},
                "id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class SubSection(BaseModel):
    """Schema for a subsection containing blocks."""
    
    blocks: List[Block] = Field(..., description="List of blocks in this subsection")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the subsection")
    
    class Config:
        json_schema_extra = {
            "example": {
                "blocks": [
                    {
                        "order": 1,
                        "block_type": "paragraph",
                        "content": "Sample content",
                        "alignment": "left",
                        "id": "550e8400-e29b-41d4-a716-446655440000"
                    }
                ],
                "id": "550e8400-e29b-41d4-a716-446655440001"
            }
        }


class Section(BaseModel):
    """Schema for a section containing subsections."""
    
    subsections: Dict[str, SubSection] = Field(..., description="Dictionary of subsections by key")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the section")
    
    class Config:
        json_schema_extra = {
            "example": {
                "subsections": {
                    "sub_section_1_1": {
                        "blocks": [
                            {
                                "order": 1,
                                "block_type": "paragraph",
                                "content": "Sample content",
                                "id": "550e8400-e29b-41d4-a716-446655440000"
                            }
                        ],
                        "id": "550e8400-e29b-41d4-a716-446655440001"
                    }
                },
                "id": "550e8400-e29b-41d4-a716-446655440002"
            }
        }


class TakeoverDocumentSchema(BaseModel):
    """Schema for the complete takeover document - simplified for OpenAI compatibility."""
    
    blocks: List[Block] = Field(..., description="List of blocks for the section")
    section_name: str = Field(..., description="Name of the section")
    
    class Config:
        json_schema_extra = {
            "example": {
                "blocks": [
                    {
                        "order": 1,
                        "block_type": "paragraph",
                        "content": "Sample content",
                        "alignment": "left",
                        "variables": {"company_name": "TechCorp Ltd"}
                    }
                ],
                "section_name": "introduction"
            }
        }




class SectionGenerationRequest(BaseModel):
    """Schema for section generation request."""
    
    section_name: str = Field(..., description="Name of the section to generate")
    project_description: str = Field(..., description="Description of the project")
    project_data: ProjectData = Field(..., description="Project data including Q&A")
    
    class Config:
        json_schema_extra = {
            "example": {
                "section_name": "introduction",
                "project_description": "Strategic acquisition of TechCorp Ltd",
                "project_data": {
                    "project_id": "123",
                    "target_company": "TechCorp Ltd",
                    "offeror": "Acquisition Holdings Inc",
                    "questions_answers": {
                        "What is the target company?": "TechCorp Ltd is a technology company"
                    }
                }
            }
        }


class TemplateContent(BaseModel):
    """Schema for template content."""
    
    template_files: List[str] = Field(..., description="List of template file paths used")
    content: Dict[str, Any] = Field(..., description="Loaded template content")
    section_name: str = Field(..., description="Name of the section")
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_files": ["page_7_ui_blocks.json", "page_8_ui_blocks.json"],
                "content": {"blocks": [...]},
                "section_name": "introduction"
            }
        }


class GeneratedContent(BaseModel):
    """Schema for generated content."""
    
    section_name: str = Field(..., description="Name of the generated section")
    content: TakeoverDocumentSchema = Field(..., description="Generated content in the new schema format")
    template_files_used: List[str] = Field(..., description="Template files used for generation")
    generation_timestamp: datetime = Field(default_factory=datetime.now, description="When content was generated")
    status: str = Field(default="success", description="Generation status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "section_name": "introduction",
                "content": {
                    "sections": {
                        "section_introduction": {
                            "subsections": {
                                "sub_section_1_1": {
                                    "blocks": []
                                }
                            }
                        }
                    }
                },
                "template_files_used": ["page_7_ui_blocks.json"],
                "generation_timestamp": "2025-01-27T10:30:00Z",
                "status": "success"
            }
        }


class SectionGenerationResponse(BaseModel):
    """Schema for section generation response."""
    
    section_name: str = Field(..., description="Name of the section")
    generated_content: Optional[GeneratedContent] = Field(None, description="Generated content if successful")
    error: Optional[str] = Field(None, description="Error message if generation failed")
    status: str = Field(..., description="Response status (success/error)")
    processing_time: Optional[float] = Field(None, description="Time taken to process in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "section_name": "introduction",
                "generated_content": {
                    "section_name": "introduction",
                    "content": {
                        "sections": {
                            "section_introduction": {
                                "subsections": {
                                    "sub_section_1_1": {
                                        "blocks": []
                                    }
                                }
                            }
                        }
                    },
                    "template_files_used": ["page_7_ui_blocks.json"],
                    "status": "success"
                },
                "status": "success",
                "processing_time": 2.5
            }
        }


class AvailableSectionsResponse(BaseModel):
    """Schema for available sections response."""
    
    sections: List[str] = Field(..., description="List of available section names")
    total_sections: int = Field(..., description="Total number of available sections")
    template_base_path: str = Field(..., description="Base path to templates directory")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sections": ["introduction", "definitions", "terms_conditions"],
                "total_sections": 16,
                "template_base_path": "/backend/templates/"
            }
        }


class MultipleSectionsRequest(BaseModel):
    """Schema for multiple sections generation request."""
    
    sections: List[str] = Field(..., description="List of section names to generate")
    project_description: str = Field(..., description="Description of the project")
    project_data: ProjectData = Field(..., description="Project data including Q&A")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sections": ["introduction", "definitions"],
                "project_description": "Strategic acquisition of TechCorp Ltd",
                "project_data": {
                    "project_id": "123",
                    "questions_answers": {...}
                }
            }
        }


class MultipleSectionsResponse(BaseModel):
    """Schema for multiple sections generation response."""
    
    results: Dict[str, SectionGenerationResponse] = Field(..., description="Results for each section")
    total_sections: int = Field(..., description="Total number of sections processed")
    successful_sections: int = Field(..., description="Number of successfully generated sections")
    failed_sections: int = Field(..., description="Number of failed sections")
    overall_status: str = Field(..., description="Overall processing status")
    processing_time: Optional[float] = Field(None, description="Total processing time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": {
                    "introduction": {
                        "section_name": "introduction",
                        "generated_content": {
                            "section_name": "introduction",
                            "content": {
                                "sections": {
                                    "section_introduction": {
                                        "subsections": {
                                            "sub_section_1_1": {
                                                "blocks": []
                                            }
                                        }
                                    }
                                }
                            },
                            "status": "success"
                        },
                        "status": "success"
                    }
                },
                "total_sections": 2,
                "successful_sections": 2,
                "failed_sections": 0,
                "overall_status": "success",
                "processing_time": 5.2
            }
        }


# Legacy schemas for backward compatibility
class TakeoverDocumentBlock(BaseModel):
    """Legacy schema for individual document blocks."""
    
    order: int = Field(..., description="Order of the block")
    block_type: str = Field(..., description="Type of block (paragraph, h1, h2, etc.)")
    content: str = Field(..., description="Content of the block")
    alignment: str = Field(default="left", description="Text alignment")
    variables: Optional[Dict[str, Any]] = Field(None, description="Variables for dynamic content")
    
    class Config:
        json_schema_extra = {
            "example": {
                "order": 1,
                "block_type": "paragraph",
                "content": "This is a sample paragraph",
                "alignment": "left",
                "variables": {"company_name": "TechCorp Ltd"}
            }
        }


class TakeoverDocumentPage(BaseModel):
    """Legacy schema for a document page."""
    
    page_number: int = Field(..., description="Page number")
    blocks: List[TakeoverDocumentBlock] = Field(..., description="List of blocks on this page")
    total_blocks: int = Field(..., description="Total number of blocks")
    block_types: List[str] = Field(..., description="Types of blocks used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "page_number": 7,
                "blocks": [],
                "total_blocks": 10,
                "block_types": ["paragraph", "h1", "h2"]
            }
        }


class TakeoverDocumentContent(BaseModel):
    """Legacy schema for the complete takeover document content."""
    
    pages: Dict[str, Any] = Field(..., description="Dictionary of pages by filename")
    section_name: str = Field(..., description="Name of the section")
    template_files_used: List[str] = Field(..., description="Template files used for generation")
    generation_timestamp: str = Field(..., description="When content was generated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pages": {
                    "page_7_ui_blocks.json": {
                        "page_number": 7,
                        "blocks": [],
                        "total_blocks": 10,
                        "block_types": ["paragraph", "h1"]
                    }
                },
                "section_name": "introduction",
                "template_files_used": ["page_7_ui_blocks.json"],
                "generation_timestamp": "2025-01-27T10:30:00Z"
            }
        }
