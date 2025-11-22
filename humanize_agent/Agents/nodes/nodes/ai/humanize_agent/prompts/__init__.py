"""
Humanize Agent Prompts Package

Enhanced academic-focused prompts for transforming AI-generated text 
into sophisticated, human-like academic writing based on analysis of
top-tier business research journals.

Main Components:
- main_system_prompt: Complete academic system prompt with enhanced patterns
- sub_prompts: Individual focused prompts for specific aspects
- few_shot_examples: High-quality academic writing samples

Usage:
    from prompts import get_main_system_prompt
    
    # Use the enhanced academic system prompt (dynamically reloads from JSON)
    system_prompt = get_main_system_prompt()
"""

from .main_system_prompt import MAIN_SYSTEM_PROMPT, get_main_system_prompt

__all__ = [
    # Main system prompt (constant, may be stale)
    'MAIN_SYSTEM_PROMPT',
    # Dynamic function that reloads from JSON files
    'get_main_system_prompt'
]
