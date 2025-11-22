"""
Make Shorter Agent
Condenses text while maintaining key information and meaning.
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .prompts import get_main_prompt


class MakeShorterAgent:
    """
    Agent that condenses text while maintaining key information.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the make shorter agent.
        
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
    
    def make_shorter(
        self,
        text: str,
        target_length: Optional[int] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Condense text to make it shorter.
        
        Args:
            text (str): The text to condense
            target_length (int, optional): Target word count or percentage reduction
            context (str, optional): Additional context about desired condensation
            
        Returns:
            Dict with condensed text and metadata
        """
        try:
            system_prompt = get_main_prompt()
            
            length_text = ""
            if target_length:
                length_text = f"\n\nTarget: Condense to approximately {target_length} words or reduce by {target_length}%."
            
            context_text = ""
            if context:
                context_text = f"\n\nAdditional Context: {context}\n"
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", f"""Please condense the following text to make it shorter:

{text}

{length_text}
{context_text}

Return the complete condensed text.""")
            ])
            
            chain = prompt | self.llm | StrOutputParser()
            condensed_text = chain.invoke({"text": text, "target_length": target_length, "context": context})
            
            return {
                "original_text": text,
                "condensed_text": condensed_text,
                "success": True,
                "operation": "make_shorter",
                "target_length": target_length,
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "make_shorter"
            }
            
        except Exception as e:
            return {
                "original_text": text,
                "condensed_text": "",
                "success": False,
                "error": str(e),
                "operation": "make_shorter",
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "make_shorter"
            }

