"""
Improve Transitions Agent
Improves transitions between sentences and paragraphs in existing text.
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .prompts import get_main_prompt


class ImproveTransitionsAgent:
    """
    Agent that improves transitions between sentences and paragraphs in existing text.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the improve transitions agent.
        
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
    
    def improve_transitions(
        self,
        text: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Improve transitions in the provided text.
        
        Args:
            text (str): The text to improve transitions for
            context (str, optional): Additional context about the text
            
        Returns:
            Dict with improved text and metadata
        """
        try:
            system_prompt = get_main_prompt()
            
            context_text = ""
            if context:
                context_text = f"\n\nAdditional Context: {context}\n"
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", f"""Please improve the transitions in the following text:

{text}

{context_text}

Improve the transitions between sentences and paragraphs to make the text flow more smoothly. Return the complete improved text.""")
            ])
            
            chain = prompt | self.llm | StrOutputParser()
            improved_text = chain.invoke({"text": text, "context": context})
            
            return {
                "original_text": text,
                "improved_text": improved_text,
                "success": True,
                "operation": "improve_transitions",
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "improve_transitions"
            }
            
        except Exception as e:
            return {
                "original_text": text,
                "improved_text": "",
                "success": False,
                "error": str(e),
                "operation": "improve_transitions",
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "improve_transitions"
            }

