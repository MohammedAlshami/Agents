"""
Perplexity search service using LangChain runnable integration.
"""

import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_perplexity import ChatPerplexity
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

# Load environment variables
load_dotenv()

class PerplexitySearchService:
    """Service class for Perplexity search operations using LangChain runnables."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Perplexity service with API key."""
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in environment variables")
        
        # Initialize Perplexity client with runnable support
        self.perplexity = ChatPerplexity(
            model="sonar",
            temperature=0.7,
            api_key=self.api_key
        )
        
        # Create prompt templates for different use cases
        self._setup_prompt_templates()
    
    def _setup_prompt_templates(self):
        """Setup prompt templates for different search operations."""
        
        # Search results prompt template
        self.search_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful search assistant. Return search results in the specified JSON format."),
            ("human", """Please search for information about: {query}
            
            Return the results in this exact JSON format:
            {{
                "results": [
                    {{
                        "title": "Result title",
                        "url": "Source URL", 
                        "snippet": "Brief description or snippet",
                        "source": "Source name (e.g., Wikipedia, news site, etc.)"
                    }}
                ]
            }}
            
            Provide up to {max_results} most relevant results.""")
        ])
        
        # Simple search prompt template
        self.simple_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Provide clear and accurate information."),
            ("human", "{query}")
        ])
        
        # Contextual search prompt template
        self.context_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Use the provided context to enhance your search results."),
            ("human", "Context: {context}\n\nPlease search for: {query}")
        ])
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search using Perplexity and return structured results using runnables.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, url, snippet, and source
        """
        try:
            # Create the runnable chain
            chain = self.search_prompt | self.perplexity
            
            # Invoke the chain with input parameters
            response = chain.invoke({
                "query": query,
                "max_results": max_results
            })
            
            # Parse the response
            return self._parse_search_response(response.content, query)
                
        except Exception as e:
            print(f"Error in Perplexity search: {e}")
            return []
    
    def _parse_search_response(self, content: str, query: str) -> List[Dict[str, Any]]:
        """Parse the search response and extract structured results."""
        try:
            # Try to parse as JSON
            if content.strip().startswith('{'):
                json_data = json.loads(content)
                if 'results' in json_data:
                    return json_data['results']
            
            # If not JSON, try to extract from markdown or plain text
            results = []
            lines = content.split('\n')
            current_result = {}
            
            for line in lines:
                line = line.strip()
                if 'title' in line.lower() or '**' in line:
                    if current_result:
                        results.append(current_result)
                    current_result = {'title': line.replace('**', '').strip(), 'url': '', 'snippet': '', 'source': ''}
                elif 'url' in line.lower() or 'http' in line:
                    current_result['url'] = line
                elif line:
                    if 'snippet' not in current_result:
                        current_result['snippet'] = line
                    else:
                        current_result['snippet'] += ' ' + line
            
            if current_result:
                results.append(current_result)
            
            return results[:5] if results else [{'title': query, 'url': '', 'snippet': content[:200], 'source': 'Perplexity'}]
            
        except Exception as e:
            print(f"Error parsing search response: {e}")
            return [{'title': query, 'url': '', 'snippet': content[:200], 'source': 'Perplexity'}]
    
    def search_simple(self, query: str) -> str:
        """
        Simple search that returns plain text response.
        
        Args:
            query: Search query
            
        Returns:
            Plain text response
        """
        try:
            chain = self.simple_prompt | self.perplexity
            response = chain.invoke({"query": query})
            return response.content
        except Exception as e:
            print(f"Error in simple search: {e}")
            return f"Error searching: {str(e)}"
    
    def search_with_context(self, query: str, context: str) -> str:
        """
        Search with additional context.
        
        Args:
            query: Search query
            context: Additional context
            
        Returns:
            Plain text response
        """
        try:
            chain = self.context_prompt | self.perplexity
            response = chain.invoke({"query": query, "context": context})
            return response.content
        except Exception as e:
            print(f"Error in contextual search: {e}")
            return f"Error searching: {str(e)}"
    
    def create_custom_chain(self, system_message: str, user_template: str):
        """
        Create a custom chain with system and user messages.
        
        Args:
            system_message: System message
            user_template: User message template
            
        Returns:
            Runnable chain
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", user_template)
        ])
        return prompt | self.perplexity
    
    def stream_search(self, query: str):
        """
        Stream search results.
        
        Args:
            query: Search query
            
        Yields:
            Chunks of response
        """
        try:
            chain = self.simple_prompt | self.perplexity
            for chunk in chain.stream({"query": query}):
                if hasattr(chunk, 'content'):
                    yield chunk.content
                else:
                    yield str(chunk)
        except Exception as e:
            yield f"Error searching: {query}"

