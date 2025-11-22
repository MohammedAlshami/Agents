"""
Problem Statement Schema for AI-generated research problem statements.
"""

from pydantic import BaseModel, Field
from typing import List

class ProblemStatementItem(BaseModel):
    """Schema for a single problem statement."""
    title: str = Field(description="The title of the problem statement")
    description: str = Field(description="A 1-2 sentence description of the research problem")
    points: List[str] = Field(description="List of 4 key research points or focus areas")

class ProblemStatementsOutput(BaseModel):
    """Schema for the complete output containing 4 problem statements."""
    problem_statements: List[ProblemStatementItem] = Field(
        description="List of exactly 4 distinct problem statements",
        min_items=4,
        max_items=4
    )
