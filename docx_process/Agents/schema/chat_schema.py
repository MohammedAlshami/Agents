"""
Schema for Chat Agent responses and MCP operations.
"""

from typing import List, Optional, Dict, Any, Literal, Union
from pydantic import BaseModel, Field
from enum import Enum
from .document_schema import DocumentSchema
import uuid

class MCPOperationType(str, Enum):
    """Available MCP operation types."""
    DATA_RETRIEVAL = "DATA_RETRIEVAL"
    DOCUMENT_GENERATION = "DOCUMENT_GENERATION"
    DOCUMENT_STRUCTURE_GENERATION = "DOCUMENT_STRUCTURE_GENERATION"  # New: Generate document structure from takeover templates
    SECTION_GENERATION = "SECTION_GENERATION"  # New: Generate individual sections
    INTRODUCTION_GENERATION = "INTRODUCTION_GENERATION"
    BACKGROUND_GENERATION = "BACKGROUND_GENERATION"
    ANALYSIS_GENERATION = "ANALYSIS_GENERATION"
    FINDINGS_GENERATION = "FINDINGS_GENERATION"
    CONCLUSIONS_GENERATION = "CONCLUSIONS_GENERATION"
    RECOMMENDATIONS_GENERATION = "RECOMMENDATIONS_GENERATION"
    APPENDICES_GENERATION = "APPENDICES_GENERATION"
    QUERY_GENERATION = "QUERY_GENERATION"
    COMBINED_WORKFLOW = "COMBINED_WORKFLOW"
    OUTLINE_GENERATION = "OUTLINE_GENERATION"  # Deprecated: Use DOCUMENT_STRUCTURE_GENERATION instead
    ANALYSIS = "ANALYSIS"
    SUMMARIZATION = "SUMMARIZATION"
    # Introduction Sub-Agent Operations
    TRANSACTION_AGENT_GENERATION = "TRANSACTION_AGENT_GENERATION"
    REGULATORY_NOTICES_AGENT_GENERATION = "REGULATORY_NOTICES_AGENT_GENERATION"
    SHAREHOLDING_AGENT_GENERATION = "SHAREHOLDING_AGENT_GENERATION"
    EMPLOYEE_SCHEMES_AGENT_GENERATION = "EMPLOYEE_SCHEMES_AGENT_GENERATION"
    REGULATORY_TIMELINE_AGENT_GENERATION = "REGULATORY_TIMELINE_AGENT_GENERATION"

class DataSource(str, Enum):
    """Available data sources for MCP operations."""
    PINECONE = "pinecone"
    PERPLEXITY = "perplexity"

class DocumentType(str, Enum):
    """Available document types for generation."""
    ACADEMIC = "academic"
    GENERAL = "general"
    COMPREHENSIVE = "comprehensive"
    RESEARCH = "research"
    SUMMARY = "summary"
    ANALYSIS = "analysis"

class ChatMode(str, Enum):
    """Available chat response modes."""
    CHAT = "chat"
    CONTEXT_LOOKUP = "context_lookup"  # Mode for searching uploaded files/context
    CLARIFICATION = "clarification"  # Mode for handling clarification requests
    QUESTIONNAIRE = "questionnaire"  # Mode for questionnaire progression

class QuestionType(str, Enum):
    """Available question types for questionnaire."""
    TEXT = "text"
    TEXTAREA = "textarea"
    SELECT = "select"
    MULTISELECT = "multiselect"
    NUMBER = "number"
    DATE = "date"
    EMAIL = "email"
    URL = "url"
    BOOLEAN = "boolean"

class ClarificationType(str, Enum):
    """Types of clarification requests."""
    QUESTION_CLARIFICATION = "question_clarification"  # User needs clarification about a question
    PROCESS_CLARIFICATION = "process_clarification"  # User needs clarification about the process
    INFORMATION_CLARIFICATION = "information_clarification"  # User needs clarification about information
    GENERAL_HELP = "general_help"  # User needs general help

class DataSourceInfo(BaseModel):
    """Detailed information about a data source."""
    name: str = Field(..., description="Name of the data source")
    description: str = Field(..., description="Detailed description of what this source provides")
    content_type: str = Field(..., description="Type of content this source provides")
    update_frequency: str = Field(..., description="How often this source is updated")
    best_for: List[str] = Field(..., description="What this source is best suited for")
    limitations: List[str] = Field(..., description="Limitations of this source")
    api_rate_limit: Optional[str] = Field(None, description="API rate limits if applicable")
    coverage: str = Field(..., description="Geographic or temporal coverage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Perplexity",
                "description": "Real-time web search and current information service",
                "content_type": "Current web information and real-time data",
                "update_frequency": "Real-time",
                "best_for": ["Current events", "Recent developments", "Web search", "Live information"],
                "limitations": ["Web-based content only", "May not include academic papers"],
                "api_rate_limit": "Varies by plan",
                "coverage": "Global web content"
            }
        }

class MCPOperation(BaseModel):
    """Schema for MCP operation parameters with detailed options."""
    operation: MCPOperationType = Field(..., description="Type of MCP operation to perform")
    data_sources: List[DataSource] = Field(..., description="List of data sources to use")
    user_instruction: str = Field(..., description="Instruction to send to MCP")
    parameters: Dict[str, Any] = Field(
        default_factory=lambda: {
            "max_results": 5,
            "document_type": "general",
            "include_metadata": True,
            "sort_by": "relevance",
            "time_filter": None,
            "language": "en"
        },
        description="Detailed parameters for the MCP operation"
    )
    
    # Detailed parameter descriptions
    max_results: int = Field(5, ge=1, le=50, description="Maximum number of results to retrieve per source")
    document_type: DocumentType = Field(DocumentType.GENERAL, description="Type of document to generate")
    include_metadata: bool = Field(True, description="Whether to include metadata in results")
    sort_by: Literal["relevance", "date", "title", "author"] = Field("relevance", description="How to sort results")
    time_filter: Optional[str] = Field(None, description="Time filter (e.g., '2024', 'last_year', 'last_month')")
    language: str = Field("en", description="Language preference for results")
    
    class Config:
        json_schema_extra = {
            "example": {
                "operation": "COMBINED_WORKFLOW",
                "data_sources": ["perplexity", "pinecone"],
                "user_instruction": "Search comprehensively for information about AI in banking systems",
                "parameters": {
                    "max_results": 5,
                    "document_type": "comprehensive",
                    "include_metadata": True,
                    "sort_by": "relevance",
                    "time_filter": "2024",
                    "language": "en"
                }
            }
        }





class FollowUpQuestion(BaseModel):
    """Schema for follow-up questions."""
    question: str = Field(..., description="The follow-up question to ask")
    purpose: str = Field(..., description="Why this question is being asked")
    expected_response_type: str = Field(..., description="Type of response expected")
    is_required: bool = Field(False, description="Whether this question is required to proceed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What specific topic would you like to research?",
                "purpose": "To narrow down the research scope",
                "expected_response_type": "string",
                "is_required": True
            }
        }

class QuestionnaireQuestion(BaseModel):
    """Schema for questionnaire questions."""
    id: str = Field(..., description="Unique identifier for the question")
    question: str = Field(..., description="The question text")
    question_type: QuestionType = Field(..., description="Type of question")
    placeholder: Optional[str] = Field(None, description="Placeholder text for the question")
    options: Optional[List[str]] = Field(None, description="Options for select/multiselect questions")
    required: bool = Field(False, description="Whether this question is required")
    order: int = Field(0, description="Order of the question in the questionnaire")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the question")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "q1",
                "question": "What is the target company name?",
                "question_type": "text",
                "placeholder": "Enter the company name",
                "required": True,
                "order": 1
            }
        }

class ClarificationRequest(BaseModel):
    """Schema for clarification requests."""
    clarification_type: ClarificationType = Field(..., description="Type of clarification needed")
    original_question: Optional[str] = Field(None, description="The original question that needs clarification")
    user_message: str = Field(..., description="The user's clarification request")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the clarification")
    
    class Config:
        json_schema_extra = {
            "example": {
                "clarification_type": "question_clarification",
                "original_question": "What is the target company name?",
                "user_message": "I don't understand what you mean by target company",
                "context": {"questionnaire_step": 1}
            }
        }

class ChatResponse(BaseModel):
    """Schema for Chat Agent response with detailed information."""
    mode: ChatMode = Field(..., description="Response mode: chat, context_lookup, clarification, or questionnaire")
    response: str = Field(..., description="The response message to show to the user")
    reasoning: str = Field(..., description="Brief explanation of the decision made")
    question_type: Optional[QuestionType] = Field(None, description="Type of question if in questionnaire mode")
    clarification_type: Optional[ClarificationType] = Field(None, description="Type of clarification if in clarification mode")
    current_question: Optional[QuestionnaireQuestion] = Field(None, description="Current question if in questionnaire mode")
    progress: Optional[str] = Field(None, description="Progress indicator for questionnaire")
    
    # Detection fields - these should be set by the AI based on user intent
    is_clarification_request: bool = Field(False, description="Whether the user is asking for clarification")
    should_start_questionnaire: bool = Field(False, description="Whether the user wants to start the questionnaire")
    should_fill_from_documents: bool = Field(False, description="Whether the user wants to fill questions from documents")
    is_questionnaire_response: bool = Field(False, description="Whether the user is responding to a questionnaire question")
    needs_context_lookup: bool = Field(False, description="Whether the user needs information from uploaded documents")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mode": "questionnaire",
                "response": "What is the target company name?",
                "reasoning": "User is in questionnaire mode and needs to answer the first question",
                "question_type": "text",
                "current_question": {
                    "id": "q1",
                    "question": "What is the target company name?",
                    "question_type": "text",
                    "required": True,
                    "order": 1
                },
                "progress": "1/5"
            }
        }


class MCPCapabilities(BaseModel):
    """Detailed information about MCP capabilities."""
    available_operations: List[MCPOperationType] = Field(..., description="All available MCP operations")
    available_sources: List[DataSourceInfo] = Field(..., description="All available data sources with details")
    available_document_types: List[DocumentType] = Field(..., description="All available document types")
    operation_descriptions: Dict[str, str] = Field(..., description="Detailed descriptions of each operation")
    source_descriptions: Dict[str, str] = Field(..., description="Detailed descriptions of each data source")
    limitations: List[str] = Field(..., description="General limitations of the MCP system")
    best_practices: List[str] = Field(..., description="Best practices for using the MCP system")
    
    class Config:
        json_schema_extra = {
            "example": {
                "available_operations": ["DATA_RETRIEVAL", "DOCUMENT_GENERATION", "QUERY_GENERATION", "COMBINED_WORKFLOW"],
                "available_sources": [
                    {
                        "name": "Perplexity",
                        "description": "Real-time search engine",
                        "content_type": "Current events",
                        "update_frequency": "Real-time",
                        "best_for": ["Current events", "Recent developments"],
                        "limitations": ["Limited historical data"],
                        "coverage": "Global real-time information"
                    }
                ],
                "available_document_types": ["academic", "general", "comprehensive", "research"],
                "operation_descriptions": {
                    "DATA_RETRIEVAL": "Retrieve data from specified sources",
                    "DOCUMENT_GENERATION": "Generate structured documents",
                    "QUERY_GENERATION": "Generate optimized search queries",
                    "COMBINED_WORKFLOW": "Complete workflow from query to document generation"
                },
                "limitations": ["Rate limits on some APIs", "Some sources may be temporarily unavailable"],
                "best_practices": ["Be specific in requests", "Use appropriate sources for your needs"]
            }
        }

class ConversationContext(BaseModel):
    """Context information for ongoing conversations."""
    conversation_id: str = Field(..., description="Unique identifier for the conversation")
    user_id: Optional[str] = Field(None, description="User identifier if available")
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, description="History of messages")
    current_topic: Optional[str] = Field(None, description="Current topic being discussed")
    research_requests: List[Dict[str, Any]] = Field(default_factory=list, description="Previous research requests")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences and settings")
    session_start_time: Optional[str] = Field(None, description="When the conversation session started")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_12345",
                "user_id": "user_67890",
                "conversation_history": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi! How can I help you?"}
                ],
                "current_topic": "AI in banking",
                "research_requests": [
                    {"query": "AI banking", "sources": ["perplexity", "pinecone"], "timestamp": "2024-01-01T10:00:00Z"}
                ],
                                  "user_preferences": {"preferred_sources": ["perplexity", "pinecone"], "max_results": 10},
                "session_start_time": "2024-01-01T09:00:00Z"
            }
        }

class SearchEngineStats(BaseModel):
    """Statistics and information about search engines."""
    engine_name: str = Field(..., description="Name of the search engine")
    total_requests: int = Field(0, description="Total number of requests made")
    successful_requests: int = Field(0, description="Number of successful requests")
    average_response_time: float = Field(0.0, description="Average response time in seconds")
    last_used: Optional[str] = Field(None, description="When this engine was last used")
    status: Literal["active", "rate_limited", "error", "unavailable"] = Field("active", description="Current status")
    error_count: int = Field(0, description="Number of errors encountered")
    rate_limit_info: Optional[Dict[str, Any]] = Field(None, description="Rate limit information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "engine_name": "Perplexity",
                "total_requests": 150,
                "successful_requests": 145,
                "average_response_time": 2.5,
                "last_used": "2024-01-01T10:00:00Z",
                "status": "active",
                "error_count": 5,
                "rate_limit_info": {"requests_per_day": 1000, "remaining": 850}
            }
        }

class SystemStatus(BaseModel):
    """Overall system status and health information."""
    overall_status: Literal["healthy", "degraded", "unhealthy"] = Field(..., description="Overall system health")
    available_engines: List[str] = Field(..., description="List of currently available search engines")
    unavailable_engines: List[str] = Field(default_factory=list, description="List of currently unavailable engines")
    engine_stats: Dict[str, SearchEngineStats] = Field(default_factory=dict, description="Statistics for each engine")
    system_load: float = Field(0.0, ge=0.0, le=1.0, description="Current system load (0-1)")
    active_conversations: int = Field(0, description="Number of active conversations")
    total_requests_today: int = Field(0, description="Total requests processed today")
    average_response_time: float = Field(0.0, description="Average response time across all operations")
    last_maintenance: Optional[str] = Field(None, description="When the system was last maintained")
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_status": "healthy",
                "available_engines": ["perplexity", "pinecone"],
                "unavailable_engines": [],
                "system_load": 0.3,
                "active_conversations": 5,
                "total_requests_today": 1250,
                "average_response_time": 3.2,
                "last_maintenance": "2024-01-01T06:00:00Z"
            }
        }
