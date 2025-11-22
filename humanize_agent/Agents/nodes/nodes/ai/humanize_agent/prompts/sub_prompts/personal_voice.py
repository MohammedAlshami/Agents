"""
Personal Voice Sub-Prompt
Based on Reddit findings about shaping AI through consistent interaction and personal voice
"""

import json
import os

# Get the directory of this file
_current_dir = os.path.dirname(os.path.abspath(__file__))
_json_file = os.path.join(_current_dir, "personal_voice.json")

# Load prompt from JSON file
def _load_prompt():
    """Load prompt content from JSON file."""
    try:
        with open(_json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("content", "")
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        # Fallback to empty string if JSON file is missing or invalid
        return ""

# Property to reload prompt dynamically
def get_personal_voice_prompt():
    """Get personal voice prompt, reloading from JSON each time."""
    return _load_prompt()

# For backward compatibility, also provide as constant (but it will be stale)
PERSONAL_VOICE_PROMPT = _load_prompt()
