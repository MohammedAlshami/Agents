"""
Base AI Model configuration for AcademicAI.
"""

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from typing import Optional

# Load environment variables from a .env file
load_dotenv()

# Access the OPENAI_API_KEY environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_llm(
    model_name: str = "gpt-4o-mini",
    temperature: float = 0,
    max_tokens: Optional[int] = None,
    api_key: Optional[str] = None
) -> ChatOpenAI:
    """
    Create a configured LLM instance.
    
    Args:
        model_name: The OpenAI model to use
        temperature: Controls randomness (0 = deterministic, 1 = very random)
        max_tokens: Maximum tokens for response (None = no limit)
        api_key: OpenAI API key (uses env var if None)
        
    Returns:
        Configured ChatOpenAI instance
    """
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key or OPENAI_API_KEY,
        max_tokens=max_tokens
    )

# Default LLM instance
llm = create_llm()

