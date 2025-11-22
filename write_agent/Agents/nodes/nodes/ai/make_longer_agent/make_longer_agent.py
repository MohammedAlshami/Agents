"""
Make Longer Agent
Expands text while maintaining coherence and adding value.
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .prompts import get_main_prompt


class MakeLongerAgent:
    """
    Agent that expands text while maintaining quality.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the make longer agent.
        
        Args:
            api_key (str): OpenAI API key
        """
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=4000
        )
    
    def make_longer(
        self,
        text: str,
        target_length: Optional[int] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Expand text to make it longer.
        
        Args:
            text (str): The text to expand
            target_length (int, optional): Target word count or percentage increase
            context (str, optional): Additional context about desired expansion
            
        Returns:
            Dict with expanded text and metadata
        """
        try:
            system_prompt = get_main_prompt()
            
            length_text = ""
            if target_length:
                length_text = f"\n\nTarget: Expand to approximately {target_length} words or increase by {target_length}%."
            
            context_text = ""
            if context:
                context_text = f"\n\nAdditional Context: {context}\n"
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", f"""Please expand the following text to make it longer:

{text}

{length_text}
{context_text}

Return the complete expanded text.""")
            ])
            
            chain = prompt | self.llm | StrOutputParser()
            expanded_text = chain.invoke({"text": text, "target_length": target_length, "context": context})
            
            return {
                "original_text": text,
                "expanded_text": expanded_text,
                "success": True,
                "operation": "make_longer",
                "target_length": target_length,
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "make_longer"
            }
            
        except Exception as e:
            return {
                "original_text": text,
                "expanded_text": "",
                "success": False,
                "error": str(e),
                "operation": "make_longer",
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "make_longer"
            }

