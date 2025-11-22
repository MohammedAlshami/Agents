"""
Academic Structure Sub-Prompt
Based on the four-part academic structure and real business journal patterns
"""

import json
import os

# Get the directory of this file
_current_dir = os.path.dirname(os.path.abspath(__file__))
_json_file = os.path.join(_current_dir, "academic_structure.json")

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

ACADEMIC_STRUCTURE_PROMPT = _load_prompt()
