"""
Continue Writing Agent
Continues writing from existing text seamlessly.
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .prompts import get_main_prompt


class ContinueWritingAgent:
    """
    Agent that continues writing from existing text.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the continue writing agent.
        
        Args:
            api_key (str): OpenAI API key
        """
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=2000
        )
    
    def continue_writing(
        self,
        text: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Continue writing from the provided text.
        
        Args:
            text (str): The text to continue from
            context (str, optional): Additional context about desired continuation
            
        Returns:
            Dict with continuation text and metadata
        """
        try:
            system_prompt = get_main_prompt()
            
            context_text = ""
            if context:
                context_text = f"\n\nAdditional Context: {context}\n"
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", f"""Please continue writing from the following text:

{text}

{context_text}

Continue writing naturally from where the text ends. Return only the continuation text.""")
            ])
            
            chain = prompt | self.llm | StrOutputParser()
            continuation = chain.invoke({"text": text, "context": context})
            
            return {
                "original_text": text,
                "continuation": continuation,
                "success": True,
                "operation": "continue_writing",
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "continue_writing"
            }
            
        except Exception as e:
            return {
                "original_text": text,
                "continuation": "",
                "success": False,
                "error": str(e),
                "operation": "continue_writing",
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "continue_writing"
            }

