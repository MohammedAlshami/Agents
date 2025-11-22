"""
Fix Grammar and Spelling Agent
Fixes grammar, spelling, and punctuation errors in text.
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .prompts import get_main_prompt


class FixGrammarSpellingAgent:
    """
    Agent that fixes grammar, spelling, and punctuation errors.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the fix grammar and spelling agent.
        
        Args:
            api_key (str): OpenAI API key
        """
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=4000
        )
    
    def fix_grammar_spelling(
        self,
        text: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fix grammar, spelling, and punctuation errors in text.
        
        Args:
            text (str): The text to fix
            context (str, optional): Additional context about desired corrections
            
        Returns:
            Dict with corrected text and metadata
        """
        try:
            system_prompt = get_main_prompt()
            
            context_text = ""
            if context:
                context_text = f"\n\nAdditional Context: {context}\n"
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", f"""Please fix all grammar, spelling, and punctuation errors in the following text:

{text}

{context_text}

Return the complete corrected text with all errors fixed.""")
            ])
            
            chain = prompt | self.llm | StrOutputParser()
            corrected_text = chain.invoke({"text": text, "context": context})
            
            return {
                "original_text": text,
                "corrected_text": corrected_text,
                "success": True,
                "operation": "fix_grammar_spelling",
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "fix_grammar_spelling"
            }
            
        except Exception as e:
            return {
                "original_text": text,
                "corrected_text": "",
                "success": False,
                "error": str(e),
                "operation": "fix_grammar_spelling",
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "fix_grammar_spelling"
            }

