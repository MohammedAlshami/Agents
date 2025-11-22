"""
Prompts module for write agent.
"""

from .main_system_prompt import MAIN_SYSTEM_PROMPT, get_main_prompt
from .sub_prompts import (
    ACADEMIC_WRITING_PROMPT,
    TECHNICAL_WRITING_PROMPT,
    ANALYTICAL_WRITING_PROMPT,
    COMPARATIVE_WRITING_PROMPT,
    DESCRIPTIVE_WRITING_PROMPT,
    ARGUMENTATIVE_WRITING_PROMPT,
    get_writing_style_prompt
)

__all__ = [
    'MAIN_SYSTEM_PROMPT',
    'get_main_prompt',
    'ACADEMIC_WRITING_PROMPT',
    'TECHNICAL_WRITING_PROMPT',
    'ANALYTICAL_WRITING_PROMPT',
    'COMPARATIVE_WRITING_PROMPT',
    'DESCRIPTIVE_WRITING_PROMPT',
    'ARGUMENTATIVE_WRITING_PROMPT',
    'get_writing_style_prompt'
]

