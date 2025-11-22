"""
Schema for content outline structure with nested sections.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class SectionType(str, Enum):
    """Types of sections in the outline"""
    MAIN_SECTION = "main_section"
    SUBSECTION = "subsection"
    APPENDIX = "appendix"
    DEFINITION = "definition"
    NOTICE = "notice"
    PROCEDURE = "procedure"
    FORM = "form"

class ContentType(str, Enum):
    """Types of content to be included in sections"""
    # Text content
    TEXT = "text"
    PARAGRAPH = "paragraph"
    INTRO_PARAGRAPH = "intro_paragraph"
    CONCLUSION_PARAGRAPH = "conclusion_paragraph"
    SUMMARY_PARAGRAPH = "summary_paragraph"
    
    # Lists
    LIST = "list"
    ORDERED_LIST = "ordered_list"
    UNORDERED_LIST = "unordered_list"
    BULLET_POINTS = "bullet_points"
    NUMBERED_STEPS = "numbered_steps"
    
    # Tables
    TABLE = "table"
    DATA_TABLE = "data_table"
    COMPARISON_TABLE = "comparison_table"
    STATISTICS_TABLE = "statistics_table"
    SUMMARY_TABLE = "summary_table"
    
    # Charts and visualizations
    CHART = "chart"
    CHART_DESCRIPTION = "chart_description"
    GRAPH_DESCRIPTION = "graph_description"
    
    # Forms and interactive elements
    FORM = "form"
    FORM_SECTION = "form_section"
    CHECKLIST = "checklist"
    
    # Special content
    DEFINITION = "definition"
    DEFINITION_BOX = "definition_box"
    WARNING_BOX = "warning_box"
    INFO_BOX = "info_box"
    QUOTE_BLOCK = "quote_block"
    
    # Legal and compliance
    NOTICE = "notice"
    PROCEDURE = "procedure"
    DISCLOSURE = "disclosure"
    DISCLOSURE_BLOCK = "disclosure_block"
    LEGAL_NOTICE = "legal_notice"
    COMPLIANCE_STATEMENT = "compliance_statement"

class OutlineSection(BaseModel):
    """Schema for a single section in the outline"""
    
    model_config = {"extra": "forbid"}
    
    title: str = Field(description="Title of the section")
    description: str = Field(description="Description of what should be included in this section")
    level: int = Field(description="Hierarchical level (1 for main sections, 2 for subsections, etc.)")
    section_type: SectionType = Field(default=SectionType.MAIN_SECTION, description="Type of section")
    content_types: List[ContentType] = Field(default=[ContentType.TEXT], description="Types of content to include")
    required_elements: Optional[List[str]] = Field(default=None, description="Specific elements that must be included")
    regulatory_requirements: Optional[List[str]] = Field(default=None, description="Regulatory requirements for this section")
    data_points: Optional[List[str]] = Field(default=None, description="Specific data points to include")
    subsections: Optional[List['OutlineSection']] = Field(default=None, description="Nested subsections")
    metadata: Optional[Dict[str, str]] = Field(default=None, description="Additional metadata for the section")
    
    def add_subsection(self, title: str, description: str, section_type: SectionType = SectionType.SUBSECTION) -> 'OutlineSection':
        """Add a subsection to this section"""
        if self.subsections is None:
            self.subsections = []
        
        subsection = OutlineSection(
            title=title,
            description=description,
            level=self.level + 1,
            section_type=section_type
        )
        self.subsections.append(subsection)
        return subsection

class DocumentMetadata(BaseModel):
    """Metadata for the document"""
    
    model_config = {"extra": "forbid"}
    
    document_type: str = Field(description="Type of document (e.g., 'Take-Over Offer Document')")
    regulatory_body: Optional[str] = Field(default=None, description="Regulatory body requirements (e.g., 'SC', 'SEC')")
    jurisdiction: Optional[str] = Field(default=None, description="Legal jurisdiction")
    industry: Optional[str] = Field(default=None, description="Industry sector")
    compliance_requirements: Optional[List[str]] = Field(default=None, description="Specific compliance requirements")
    key_parties: Optional[List[str]] = Field(default=None, description="Key parties involved")

class ContentOutlineSchema(BaseModel):
    """Schema for a complete content outline"""
    
    model_config = {"extra": "forbid"}
    
    document_title: str = Field(description="Title of the document")
    overview: str = Field(description="Brief overview of the document's purpose and scope")
    document_metadata: Optional[DocumentMetadata] = Field(default=None, description="Document metadata")
    sections: List[OutlineSection] = Field(description="Main sections of the document")
    appendices: Optional[List[OutlineSection]] = Field(default=None, description="Appendix sections")
    required_disclosures: Optional[List[str]] = Field(default=None, description="Required disclosures")
    compliance_checklist: Optional[List[str]] = Field(default=None, description="Compliance checklist")
    
    def add_section(self, title: str, description: str, section_type: SectionType = SectionType.MAIN_SECTION) -> OutlineSection:
        """Add a main section to the outline"""
        section = OutlineSection(
            title=title,
            description=description,
            level=1,
            section_type=section_type
        )
        self.sections.append(section)
        return section
    
    def add_appendix(self, title: str, description: str) -> OutlineSection:
        """Add an appendix section"""
        if self.appendices is None:
            self.appendices = []
        
        appendix = OutlineSection(
            title=title,
            description=description,
            level=1,
            section_type=SectionType.APPENDIX
        )
        self.appendices.append(appendix)
        return appendix
    
    def to_table_of_contents(self) -> str:
        """Convert the outline to a formatted table of contents string"""
        toc_parts = [f"# {self.document_title}\n"]
        
        if self.document_metadata:
            toc_parts.append(f"**Document Type:** {self.document_metadata.document_type}")
            if self.document_metadata.regulatory_body:
                toc_parts.append(f"**Regulatory Body:** {self.document_metadata.regulatory_body}")
            toc_parts.append("")
        
        def format_section(section: OutlineSection, indent: int = 0) -> str:
            prefix = "  " * indent
            section_type_icon = {
                SectionType.MAIN_SECTION: "📄",
                SectionType.SUBSECTION: "📝",
                SectionType.APPENDIX: "📎",
                SectionType.DEFINITION: "📖",
                SectionType.NOTICE: "⚠️",
                SectionType.PROCEDURE: "📋",
                SectionType.FORM: "📝"
            }.get(section.section_type, "📄")
            
            result = f"{prefix}{section_type_icon} **{section.title}**: {section.description}\n"
            
            # Add content type indicators
            if section.content_types and len(section.content_types) > 1:
                content_indicators = [f"[{ct.value}]" for ct in section.content_types]
                result += f"{prefix}    Content: {', '.join(content_indicators)}\n"
            
            # Add required elements if specified
            if section.required_elements:
                result += f"{prefix}    Required: {', '.join(section.required_elements)}\n"
            
            if section.subsections:
                for subsection in section.subsections:
                    result += format_section(subsection, indent + 1)
            
            return result
        
        # Format main sections
        for section in self.sections:
            toc_parts.append(format_section(section))
        
        # Format appendices if they exist
        if self.appendices:
            toc_parts.append("\n## Appendices")
            for appendix in self.appendices:
                toc_parts.append(format_section(appendix))
        
        # Add compliance checklist if available
        if self.compliance_checklist:
            toc_parts.append("\n## Compliance Checklist")
            for item in self.compliance_checklist:
                toc_parts.append(f"- [ ] {item}")
        
        return "\n".join(toc_parts)
    
    def get_section_by_title(self, title: str) -> Optional[OutlineSection]:
        """Get a section by its title (recursive search)"""
        def search_sections(sections: List[OutlineSection]) -> Optional[OutlineSection]:
            for section in sections:
                if section.title.lower() == title.lower():
                    return section
                if section.subsections:
                    result = search_sections(section.subsections)
                    if result:
                        return result
            return None
        
        return search_sections(self.sections)
    
    def get_all_sections(self) -> List[OutlineSection]:
        """Get all sections including subsections (flattened list)"""
        all_sections = []
        
        def collect_sections(sections: List[OutlineSection]):
            for section in sections:
                all_sections.append(section)
                if section.subsections:
                    collect_sections(section.subsections)
        
        collect_sections(self.sections)
        if self.appendices:
            collect_sections(self.appendices)
        
        return all_sections
