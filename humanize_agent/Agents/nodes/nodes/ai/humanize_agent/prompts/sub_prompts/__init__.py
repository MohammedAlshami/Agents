"""
Sub-Prompts Package

Focused sub-prompts for humanizing AI text based on Reddit findings and proven techniques.
"""

# Import all sub-prompts
from .natural_conversation import NATURAL_CONVERSATION_PROMPT
from .academic_structure import ACADEMIC_STRUCTURE_PROMPT
from .human_variance import HUMAN_VARIANCE_PROMPT
from .ai_detection_avoidance import AI_DETECTION_AVOIDANCE_PROMPT
from .personal_voice import PERSONAL_VOICE_PROMPT
from .content_modification import CONTENT_MODIFICATION_PROMPT

# Note: Examples not currently implemented - reserved for future use

__all__ = [
    # Sub-prompts
    'NATURAL_CONVERSATION_PROMPT',
    'ACADEMIC_STRUCTURE_PROMPT', 
    'HUMAN_VARIANCE_PROMPT',
    'AI_DETECTION_AVOIDANCE_PROMPT',
    'PERSONAL_VOICE_PROMPT',
    'CONTENT_MODIFICATION_PROMPT'
]
