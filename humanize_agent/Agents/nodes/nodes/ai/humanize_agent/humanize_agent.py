"""
Humanize Agent
Makes text sound more human and natural.
"""

import os
import re
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from .prompts import get_main_system_prompt


class HumanizeAgent:
    """
    Agent that makes text sound more human and natural.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the humanize agent.
        
        Args:
            api_key (str): OpenAI API key
        """
        # Set API key
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        # Initialize with GPT-4o for maximum humanization
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=1.0,  # Maximum temperature for maximum creativity
            max_tokens=4000,
            top_p=1.0,  # Maximum nucleus sampling
            frequency_penalty=0.8,  # Maximum frequency penalty to reduce repetition
            presence_penalty=0.6  # High presence penalty to encourage new topics
        )
        
        # Store user prompt template (system prompt will be reloaded dynamically on each use)
        self._humanize_user_prompt = "**CRITICAL: HUMAN-LIKE ACADEMIC WRITING - SINGLE PARAGRAPH ONLY**\n\nTransform this text into natural, human-like academic writing following ALL patterns:\n\n<INPUT_TEXT>\n{text}\n</INPUT_TEXT>\n\n**MANDATORY REQUIREMENTS - MUST FOLLOW:**\n1. **CRITICAL: RETURN ONLY ONE PARAGRAPH** - No line breaks, no multiple paragraphs, just one continuous paragraph\n2. Use NATURAL transitions: \"And,\" \"Also,\" \"But,\" \"So\" instead of \"Furthermore,\" \"Moreover\"\n3. Use HUMAN word choices: \"increasingly become,\" \"considers,\" \"powerful,\" \"large corpora\"\n4. Mix sentence lengths: short declarative + complex sentences\n5. Start sentences with \"And,\" \"But,\" \"So\" when natural\n6. Use parenthetical expressions: \"(specific details)\"\n7. **ABSOLUTELY FORBIDDEN:** em dashes (—), en dashes (–), or any special Unicode characters\n8. **ABSOLUTELY FORBIDDEN:** Multiple paragraphs or line breaks - output must be ONE continuous paragraph\n9. **ONLY ALLOWED:** periods, commas, semicolons, colons, question marks, exclamation points, and standard hyphens (-)\n10. **CONTENT MODIFICATION:** You MAY modify structure, sentence order, and phrasing as needed - just preserve the original meaning\n11. **WORD COUNT:** Maintain similar word count (can be slightly longer for natural enhancement)\n12. Provide ONLY the humanized text - no XML tags or wrappers, no multiple paragraphs\n13. **OUTPUT FORMAT:** Return text as a single continuous paragraph with spaces between sentences, NO line breaks or paragraph separators\n\n**AVOID:** \"Furthermore,\" \"Moreover,\" \"significant,\" \"critical,\" \"profound,\" \"comprehensive,\" \"utilize,\" \"facilitate\", multiple paragraphs, line breaks\n**USE INSTEAD:** \"And,\" \"Also,\" \"powerful,\" \"important,\" \"use,\" \"help,\" \"enable\", single continuous paragraph"
    
    def humanize_text(self, text: str) -> Dict[str, Any]:
        """
        Humanize the given text.
        Reloads prompts from JSON files on each call to ensure latest modifications are used.
        
        Args:
            text (str): Text to humanize
            
        Returns:
            Dict with humanized text and metadata
        """
        try:
            # Reload system prompt from JSON files dynamically
            system_prompt = get_main_system_prompt()
            
            # Create prompt template with fresh system prompt
            humanize_prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", self._humanize_user_prompt)
            ])
            
            # Create chain with fresh prompts
            chain = humanize_prompt | self.llm | StrOutputParser()
            
            # Process the text
            humanized_text = chain.invoke({"text": text})
            
            # Post-process to ensure single paragraph
            # Remove multiple line breaks and join into single paragraph
            humanized_text = self._ensure_single_paragraph(humanized_text)
            
            return {
                "original_text": text,
                "humanized_text": humanized_text,
                "success": True,
                "timestamp": "2024-01-01T00:00:00Z",  # TODO: Use actual timestamp
                "model": "gpt-4o-mini",
                "agent": "humanize"
            }
            
        except Exception as e:
            return {
                "original_text": text,
                "humanized_text": "",
                "success": False,
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z",
                "model": "gpt-4o-mini",
                "agent": "humanize"
            }
    
    def _ensure_single_paragraph(self, text: str) -> str:
        """
        Ensure the output is a single paragraph by removing line breaks and extra whitespace.
        
        Args:
            text (str): Text to process
            
        Returns:
            str: Single paragraph text
        """
        if not text:
            return text
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Replace multiple line breaks (paragraph breaks) with spaces
        # This handles \n\n, \r\n\r\n, and other paragraph separators
        text = re.sub(r'\n\s*\n', ' ', text)  # Multiple newlines -> space
        text = re.sub(r'\r\n\s*\r\n', ' ', text)  # Windows line breaks -> space
        text = re.sub(r'\n+', ' ', text)  # Single or multiple newlines -> space
        text = re.sub(r'\r+', ' ', text)  # Carriage returns -> space
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Remove any remaining leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def process_input(self, text: str) -> Dict[str, Any]:
        """
        Process input text for humanization.
        
        Args:
            text (str): Text to process
            
        Returns:
            Dict with processing results
        """
        return self.humanize_text(text)
