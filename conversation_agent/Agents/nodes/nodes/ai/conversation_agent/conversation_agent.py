"""
Conversation Agent
Handles greetings, questions, and conversational responses naturally.
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class ConversationAgent:
    """
    Agent that handles conversational interactions, greetings, and questions naturally.
    """
    
    def __init__(self, api_key: str = None, project_id: str = None, user_id: str = None, db_manager=None):
        """
        Initialize the conversation agent.
        
        Args:
            api_key (str): OpenAI API key
            project_id (str): Project ID for database storage
            user_id (str): User ID for database storage
            db_manager: Database manager instance
        """
        # Set API key
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        # Initialize the GPT-4o mini model with higher temperature for natural conversation
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,  # Higher temperature for more natural, varied responses
            max_tokens=500  # Shorter responses for conversations
        )
        
        # Store metadata
        self.project_id = project_id
        self.user_id = user_id
        self.db_manager = db_manager
    
    def _create_chain(self, context: Optional[str] = None):
        """
        Create a chain runnable for conversational responses.
        
        Args:
            context: Optional document context
            
        Returns:
            Runnable: The complete conversation chain
        """
        # System prompt for natural conversation
        system_prompt = """You are a helpful AI writing assistant helping users with their documents. 

Your role is to:
- Respond naturally and conversationally to greetings (hi, hello, hey, etc.)
- Answer questions helpfully and concisely
- Provide brief, friendly assistance (1-3 sentences for greetings, 2-5 sentences for questions)
- Be helpful and friendly without being overly formal
- If the user asks about content generation, suggest how you can help

Keep responses brief, natural, and conversational. Don't write long academic explanations unless specifically asked."""

        # Build the prompt template
        if context:
            human_template = """User message: {message}

Document context (for reference):
{context}

Respond naturally and helpfully. If it's a greeting, be friendly and brief. If it's a question, answer based on the context if relevant, otherwise provide general help."""
        else:
            human_template = """User message: {message}

Respond naturally and helpfully. If it's a greeting, be friendly and brief. If it's a question, provide a concise, helpful answer."""
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_template)
        ])
        
        # Create the chain
        chain = prompt | self.llm | StrOutputParser()
        
        return chain
    
    def respond(
        self,
        message: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Respond to a user message conversationally.
        
        Args:
            message (str): The user's message
            context (str, optional): Document context for reference
            
        Returns:
            Dict with response text and metadata
        """
        try:
            # Create the chain for this request
            chain = self._create_chain(context)
            
            # Process the message
            response_text = chain.invoke({
                "message": message,
                "context": context or ""
            })
            
            return {
                "message": message,
                "response": response_text,
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "conversation"
            }
            
        except Exception as e:
            return {
                "message": message,
                "response": "",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "agent": "conversation"
            }







