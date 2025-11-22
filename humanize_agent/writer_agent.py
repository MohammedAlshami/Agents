"""
Simple Writer Agent
Generates paragraphs about different topics using LangChain OpenAI.
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class WriterAgent:
    """
    Simple agent that generates paragraphs about different topics.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the writer agent.
        
        Args:
            api_key (str): OpenAI API key
        """
        # Set API key
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        # Initialize the GPT-4o-mini model
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,  # Moderate temperature for varied writing
            max_tokens=500  # Generate a paragraph
        )
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a writer that generates paragraphs about various topics. 
Write a single, well-structured paragraph (approximately 150-200 words) about the given topic. 
The paragraph should be informative, engaging, and written in a clear academic style."""),
            ("human", "Write a paragraph about: {topic}")
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def generate_paragraph(self, topic: str) -> Dict[str, Any]:
        """
        Generate a paragraph about a given topic.
        
        Args:
            topic (str): The topic to write about
            
        Returns:
            Dict with generated paragraph and metadata
        """
        try:
            # Generate the paragraph
            generated_text = self.chain.invoke({"topic": topic})
            
            return {
                "topic": topic,
                "paragraph": generated_text.strip(),
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "writer"
            }
            
        except Exception as e:
            return {
                "topic": topic,
                "paragraph": "",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "writer"
            }

