"""
Schema for takeover document structure based on NTT DATA offer document format.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class TakeoverSectionType(str, Enum):
    """Types of sections in takeover documents"""
    LETTER_FROM_ADVISER = "letter_from_adviser"
    INTRODUCTION = "introduction"
    PRINCIPAL_TERMS = "principal_terms"
    RATIONALE = "rationale"
    LISTING_STATUS = "listing_status"
    COMPULSORY_ACQUISITION = "compulsory_acquisition"
    FINANCIAL_CONSIDERATIONS = "financial_considerations"
    OFFEROR_INFORMATION = "offeror_information"
    FUTURE_PLANS = "future_plans"
    FINANCIAL_RESOURCES = "financial_resources"
    RESPONSIBILITY_STATEMENT = "responsibility_statement"
    FURTHER_INFORMATION = "further_information"
    APPENDIX = "appendix"
    FORM = "form"

class TakeoverContentType(str, Enum):
    """Types of content specific to takeover documents"""
    # Legal and regulatory content
    LEGAL_NOTICE = "legal_notice"
    REGULATORY_DISCLOSURE = "regulatory_disclosure"
    COMPLIANCE_STATEMENT = "compliance_statement"
    DISCLOSURE_REQUIREMENT = "disclosure_requirement"
    
    # Financial content
    FINANCIAL_DETAILS = "financial_details"
    VALUATION_INFORMATION = "valuation_information"
    CONSIDERATION_DETAILS = "consideration_details"
    FINANCIAL_RESOURCES_PROOF = "financial_resources_proof"
    
    # Procedural content
    ACCEPTANCE_PROCEDURE = "acceptance_procedure"
    SETTLEMENT_METHOD = "settlement_method"
    TIMELINE = "timeline"
    CONDITIONS = "conditions"
    
    # Corporate information
    COMPANY_BACKGROUND = "company_background"
    BOARD_INFORMATION = "board_information"
    SHAREHOLDER_INFORMATION = "shareholder_information"
    EMPLOYEE_INFORMATION = "employee_information"
    
    # Standard content
    TEXT = "text"
    PARAGRAPH = "paragraph"
    LIST = "list"
    TABLE = "table"
    FORM_SECTION = "form_section"

class TakeoverSection(BaseModel):
    """Schema for a section in a takeover document"""
    
    model_config = {"extra": "forbid"}
    
    title: str = Field(description="Title of the section")
    description: str = Field(description="Description of what should be included in this section")
    level: int = Field(description="Hierarchical level (1 for main sections, 2 for subsections, etc.)")
    section_type: TakeoverSectionType = Field(description="Type of section")
    content_types: List[TakeoverContentType] = Field(default=[TakeoverContentType.TEXT], description="Types of content to include")
    required_elements: Optional[List[str]] = Field(default=None, description="Specific elements that must be included")
    regulatory_requirements: Optional[List[str]] = Field(default=None, description="Regulatory requirements for this section")
    legal_obligations: Optional[List[str]] = Field(default=None, description="Legal obligations and disclosures")
    subsections: Optional[List['TakeoverSection']] = Field(default=None, description="Nested subsections")
    metadata: Optional[Dict[str, str]] = Field(default=None, description="Additional metadata for the section")
    
    def add_subsection(self, title: str, description: str, section_type: TakeoverSectionType = TakeoverSectionType.APPENDIX) -> 'TakeoverSection':
        """Add a subsection to this section"""
        if self.subsections is None:
            self.subsections = []
        
        subsection = TakeoverSection(
            title=title,
            description=description,
            level=self.level + 1,
            section_type=section_type
        )
        self.subsections.append(subsection)
        return subsection

class TakeoverDocumentMetadata(BaseModel):
    """Metadata specific to takeover documents"""
    
    model_config = {"extra": "forbid"}
    
    document_type: str = Field(description="Type of document (e.g., 'Take-Over Offer Document')")
    regulatory_body: Optional[str] = Field(default=None, description="Regulatory body requirements (e.g., 'SC', 'SEC')")
    jurisdiction: Optional[str] = Field(default=None, description="Legal jurisdiction")
    offer_type: Optional[str] = Field(default=None, description="Type of offer (e.g., 'Mandatory', 'Voluntary')")
    target_company: Optional[str] = Field(default=None, description="Target company name")
    offeror_company: Optional[str] = Field(default=None, description="Offeror company name")
    compliance_requirements: Optional[List[str]] = Field(default=None, description="Specific compliance requirements")
    key_parties: Optional[List[str]] = Field(default=None, description="Key parties involved")

class TakeoverDocumentSchema(BaseModel):
    """Schema for a complete takeover document outline"""
    
    model_config = {"extra": "forbid"}
    
    document_title: str = Field(description="Title of the takeover document")
    overview: str = Field(description="Brief overview of the takeover offer and its purpose")
    document_metadata: Optional[TakeoverDocumentMetadata] = Field(default=None, description="Document metadata")
    sections: List[TakeoverSection] = Field(description="Main sections of the takeover document")
    appendices: Optional[List[TakeoverSection]] = Field(default=None, description="Appendix sections")
    forms: Optional[List[TakeoverSection]] = Field(default=None, description="Required forms")
    required_disclosures: Optional[List[str]] = Field(default=None, description="Required disclosures")
    compliance_checklist: Optional[List[str]] = Field(default=None, description="Compliance checklist")
    regulatory_obligations: Optional[List[str]] = Field(default=None, description="Regulatory obligations")
    
    def add_section(self, title: str, description: str, section_type: TakeoverSectionType = TakeoverSectionType.INTRODUCTION) -> TakeoverSection:
        """Add a main section to the outline"""
        section = TakeoverSection(
            title=title,
            description=description,
            level=1,
            section_type=section_type
        )
        self.sections.append(section)
        return section
    
    def add_appendix(self, title: str, description: str) -> TakeoverSection:
        """Add an appendix section"""
        if self.appendices is None:
            self.appendices = []
        
        appendix = TakeoverSection(
            title=title,
            description=description,
            level=1,
            section_type=TakeoverSectionType.APPENDIX
        )
        self.appendices.append(appendix)
        return appendix
    
    def add_form(self, title: str, description: str) -> TakeoverSection:
        """Add a form section"""
        if self.forms is None:
            self.forms = []
        
        form = TakeoverSection(
            title=title,
            description=description,
            level=1,
            section_type=TakeoverSectionType.FORM
        )
        self.forms.append(form)
        return form
    
    def to_table_of_contents(self) -> str:
        """Convert the outline to a formatted table of contents string"""
        toc_parts = [f"# {self.document_title}\n"]
        
        if self.document_metadata:
            toc_parts.append(f"**Document Type:** {self.document_metadata.document_type}")
            if self.document_metadata.regulatory_body:
                toc_parts.append(f"**Regulatory Body:** {self.document_metadata.regulatory_body}")
            if self.document_metadata.offer_type:
                toc_parts.append(f"**Offer Type:** {self.document_metadata.offer_type}")
            toc_parts.append("")
        
        def format_section(section: TakeoverSection, indent: int = 0) -> str:
            prefix = "  " * indent
            section_type_icon = {
                TakeoverSectionType.LETTER_FROM_ADVISER: "📧",
                TakeoverSectionType.INTRODUCTION: "📋",
                TakeoverSectionType.PRINCIPAL_TERMS: "📄",
                TakeoverSectionType.RATIONALE: "💡",
                TakeoverSectionType.LISTING_STATUS: "📊",
                TakeoverSectionType.COMPULSORY_ACQUISITION: "⚖️",
                TakeoverSectionType.FINANCIAL_CONSIDERATIONS: "💰",
                TakeoverSectionType.OFFEROR_INFORMATION: "🏢",
                TakeoverSectionType.FUTURE_PLANS: "🔮",
                TakeoverSectionType.FINANCIAL_RESOURCES: "💳",
                TakeoverSectionType.RESPONSIBILITY_STATEMENT: "✋",
                TakeoverSectionType.FURTHER_INFORMATION: "ℹ️",
                TakeoverSectionType.APPENDIX: "📎",
                TakeoverSectionType.FORM: "📝"
            }.get(section.section_type, "📄")
            
            result = f"{prefix}{section_type_icon} **{section.title}**: {section.description}\n"
            
            # Add content type indicators
            if section.content_types and len(section.content_types) > 1:
                content_indicators = [f"[{ct.value}]" for ct in section.content_types]
                result += f"{prefix}    Content: {', '.join(content_indicators)}\n"
            
            # Add required elements if specified
            if section.required_elements:
                result += f"{prefix}    Required: {', '.join(section.required_elements)}\n"
            
            # Add regulatory requirements if specified
            if section.regulatory_requirements:
                result += f"{prefix}    Regulatory: {', '.join(section.regulatory_requirements)}\n"
            
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
        
        # Format forms if they exist
        if self.forms:
            toc_parts.append("\n## Forms")
            for form in self.forms:
                toc_parts.append(format_section(form))
        
        # Add compliance checklist if available
        if self.compliance_checklist:
            toc_parts.append("\n## Compliance Checklist")
            for item in self.compliance_checklist:
                toc_parts.append(f"- [ ] {item}")
        
        # Add regulatory obligations if available
        if self.regulatory_obligations:
            toc_parts.append("\n## Regulatory Obligations")
            for obligation in self.regulatory_obligations:
                toc_parts.append(f"- {obligation}")
        
        return "\n".join(toc_parts)
    
    def get_section_by_title(self, title: str) -> Optional[TakeoverSection]:
        """Get a section by its title (recursive search)"""
        def search_sections(sections: List[TakeoverSection]) -> Optional[TakeoverSection]:
            for section in sections:
                if section.title.lower() == title.lower():
                    return section
                if section.subsections:
                    result = search_sections(section.subsections)
                    if result:
                        return result
            return None
        
        return search_sections(self.sections)
    
    def get_all_sections(self) -> List[TakeoverSection]:
        """Get all sections including subsections (flattened list)"""
        all_sections = []
        
        def collect_sections(sections: List[TakeoverSection]):
            for section in sections:
                all_sections.append(section)
                if section.subsections:
                    collect_sections(section.subsections)
        
        collect_sections(self.sections)
        if self.appendices:
            collect_sections(self.appendices)
        if self.forms:
            collect_sections(self.forms)
        
        return all_sections
