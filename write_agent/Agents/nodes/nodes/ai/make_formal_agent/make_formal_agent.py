"""
Make Formal Agent
Converts text to formal writing style.
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .prompts import get_main_prompt


class MakeFormalAgent:
    """
    Agent that converts text to formal writing style.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the make formal agent.
        
        Args:
            api_key (str): OpenAI API key
        """
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=4000
        )
    
    def make_formal(
        self,
        text: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert text to formal writing style.
        
        Args:
            text (str): The text to formalize
            context (str, optional): Additional context about desired formality level
            
        Returns:
            Dict with formalized text and metadata
        """
        try:
            system_prompt = get_main_prompt()
            
            context_text = ""
            if context:
                context_text = f"\n\nAdditional Context: {context}\n"
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", f"""Please convert the following text to formal writing style:

{text}

{context_text}

Return the complete formalized text.""")
            ])
            
            chain = prompt | self.llm | StrOutputParser()
            formal_text = chain.invoke({"text": text, "context": context})
            
            return {
                "original_text": text,
                "formal_text": formal_text,
                "success": True,
                "operation": "make_formal",
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "make_formal"
            }
            
        except Exception as e:
            return {
                "original_text": text,
                "formal_text": "",
                "success": False,
                "error": str(e),
                "operation": "make_formal",
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "make_formal"
            }

