"""
Writing style sub-prompts for write agent.
"""

from .academic import ACADEMIC_WRITING_PROMPT
from .technical import TECHNICAL_WRITING_PROMPT
from .analytical import ANALYTICAL_WRITING_PROMPT
from .comparative import COMPARATIVE_WRITING_PROMPT
from .descriptive import DESCRIPTIVE_WRITING_PROMPT
from .argumentative import ARGUMENTATIVE_WRITING_PROMPT

# Map writing styles to their prompts
WRITING_STYLE_PROMPTS = {
    "academic": ACADEMIC_WRITING_PROMPT,
    "technical": TECHNICAL_WRITING_PROMPT,
    "analytical": ANALYTICAL_WRITING_PROMPT,
    "comparative": COMPARATIVE_WRITING_PROMPT,
    "descriptive": DESCRIPTIVE_WRITING_PROMPT,
    "argumentative": ARGUMENTATIVE_WRITING_PROMPT,
}

def get_writing_style_prompt(style: str) -> str:
    """
    Get the prompt for a specific writing style.
    
    Args:
        style: Writing style name (case-insensitive)
        
    Returns:
        The writing style prompt, or academic prompt if style not found
    """
    style_lower = style.lower() if style else "academic"
    return WRITING_STYLE_PROMPTS.get(style_lower, ACADEMIC_WRITING_PROMPT)

__all__ = [
    'ACADEMIC_WRITING_PROMPT',
    'TECHNICAL_WRITING_PROMPT',
    'ANALYTICAL_WRITING_PROMPT',
    'COMPARATIVE_WRITING_PROMPT',
    'DESCRIPTIVE_WRITING_PROMPT',
    'ARGUMENTATIVE_WRITING_PROMPT',
    'WRITING_STYLE_PROMPTS',
    'get_writing_style_prompt'
]

