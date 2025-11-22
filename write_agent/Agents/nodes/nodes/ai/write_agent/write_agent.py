"""
Write Agent
Generates text content from topics/prompts with multiple writing style options.
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from .prompts import get_main_prompt


class WriteAgent:
    """
    Agent that generates text content from topics/prompts with multiple writing style options.
    """
    
    def __init__(self, api_key: str = None, project_id: str = None, user_id: str = None, db_manager=None):
        """
        Initialize the write agent.
        
        Args:
            api_key (str): OpenAI API key
            project_id (str): Project ID for database storage
            user_id (str): User ID for database storage
            db_manager: Database manager instance
        """
        # Set API key
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        # Initialize the GPT-4o mini model
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,  # Lower temperature for more consistent writing
            max_tokens=4000
        )
        
        # Store metadata
        self.project_id = project_id
        self.user_id = user_id
        self.db_manager = db_manager
    
    def _create_chain(self, writing_style: str = "academic", word_count: Optional[int] = None):
        """
        Create a chain runnable that generates text content.
        
        Args:
            writing_style: Writing style to use
            word_count: Optional target word count
            
        Returns:
            Runnable: The complete writing chain
        """
        # Get the system prompt for the specified writing style
        system_prompt = get_main_prompt(writing_style, word_count)
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", """Please write about the following topic:

Topic/Prompt: {topic}

{context_text}

Generate comprehensive content based on the topic above. Follow the specified writing style guidelines and ensure the content is well-structured, engaging, and complete.""")
        ])
        
        # Create the chain
        chain = prompt | self.llm | StrOutputParser()
        
        return chain
    
    def generate_text(
        self,
        topic: str,
        writing_style: str = "academic",
        word_count: Optional[int] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text content from a topic/prompt.
        
        Args:
            topic (str): The topic or prompt to write about
            writing_style (str): Writing style to use (default: "academic")
            word_count (int, optional): Target word count
            context (str, optional): Additional context for generation
            
        Returns:
            Dict with generated text and metadata
        """
        try:
            # Create context text if provided
            context_text = ""
            if context:
                context_text = f"\nAdditional Context: {context}\n"
            
            # Create the chain for this request
            chain = self._create_chain(writing_style, word_count)
            
            # Process the topic
            generated_text = chain.invoke({
                "topic": topic,
                "context_text": context_text
            })
            
            return {
                "topic": topic,
                "generated_text": generated_text,
                "success": True,
                "writing_style": writing_style,
                "word_count": word_count,
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "write"
            }
            
        except Exception as e:
            return {
                "topic": topic,
                "generated_text": "",
                "success": False,
                "error": str(e),
                "writing_style": writing_style,
                "word_count": word_count,
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "write"
            }
    
    def process_input(
        self,
        topic: str,
        writing_style: str = "academic",
        word_count: Optional[int] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process input topic for text generation.
        
        Args:
            topic (str): Topic or prompt to write about
            writing_style (str): Writing style to use
            word_count (int, optional): Target word count
            context (str, optional): Additional context
            
        Returns:
            Dict with processing results
        """
        return self.generate_text(topic, writing_style, word_count, context)

