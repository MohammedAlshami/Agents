"""
Content Modification Sub-Prompt
Based on Reddit findings about content modification freedom and human insights
"""

import json
import os

# Get the directory of this file
_current_dir = os.path.dirname(os.path.abspath(__file__))
_json_file = os.path.join(_current_dir, "content_modification.json")

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

CONTENT_MODIFICATION_PROMPT = _load_prompt()
