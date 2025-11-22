"""
Pydantic schemas for Router Agent responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from .chat_schema import ChatMode

class RouterResponse(BaseModel):
    """
    Router Agent response schema.
    """
    # Response type determines the action
    response_type: Literal["direct_response", "route_to_agent"] = Field(
        description="Type of response: direct_response for simple cases, route_to_agent for complex cases"
    )
    
    # The actual response content
    response: str = Field(
        description="The response message to send to the user"
    )
    
    # Reasoning for the decision
    reasoning: str = Field(
        description="Explanation of why this response type was chosen"
    )
    
    # Target agent (only if routing)
    target_agent: Optional[Literal["conversation", "questionnaire"]] = Field(
        default=None,
        description="Target agent for routing (only used when response_type is 'route_to_agent')"
    )
    
    # Chat mode
    mode: ChatMode = Field(
        default=ChatMode.CHAT,
        description="Chat mode for the response"
    )
    
    # Confidence score
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for the routing decision"
    )



