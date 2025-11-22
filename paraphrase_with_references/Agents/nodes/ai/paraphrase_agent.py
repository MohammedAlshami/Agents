"""
Paraphrase Agent using Perplexity for academic text paraphrasing with credible sources.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to the path to import Agents modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from Agents.engines.search.perplexity import PerplexitySearchService
except ImportError:
    # Try alternative import path
    try:
        agents_path = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        if agents_path not in sys.path:
            sys.path.insert(0, agents_path)
        from engines.search.perplexity import PerplexitySearchService
    except ImportError as e:
        import traceback
        traceback.print_exc()
        raise ImportError(f"Failed to import PerplexitySearchService: {e}")

# Load environment variables
load_dotenv()


class ParaphraseAgent:
    """
    Paraphrase agent using Perplexity for academic text paraphrasing with credible sources.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the paraphrase agent with Perplexity API key.
        
        Args:
            api_key (str): Perplexity API key. If None, will use environment variable.
        """
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        
        # Initialize Perplexity service
        try:
            self.perplexity_service = PerplexitySearchService(api_key=self.api_key)
            print("[OK] ParaphraseAgent connected to Perplexity service")
        except Exception as e:
            print(f"[ERROR] Error initializing Perplexity service: {e}")
            raise
    
    def paraphrase(self, text: str) -> Dict[str, Any]:
        """
        Paraphrase text with academic sources using Perplexity.
        
        Args:
            text (str): Text to paraphrase
            
        Returns:
            Dict[str, Any]: Paraphrased text with structured data
        """
        try:
            # Create the paraphrase prompt with academic focus
            paraphrase_prompt = f"""Please paraphrase the following text while maintaining its original meaning, but rewrite it to be more academically credible and supported by research. Focus on academic writing style and include references to relevant research when possible.

Original text: {text}

Requirements:
1. Paraphrase to express the same meaning in different words
2. Use academic writing style
3. Make it sound more credible and research-backed
4. Maintain the original intent and key points
5. Use formal academic language
6. MAINTAIN THE EXACT SAME STRUCTURE as the original text (same number of paragraphs, same paragraph breaks, same formatting)
7. MAINTAIN SIMILAR LENGTH for each paragraph (if original paragraph 1 is 3 sentences, paraphrased paragraph 1 should be approximately 3 sentences)
8. PRESERVE THE ESSAY STRUCTURE (if input has 5 paragraphs, output must have 5 paragraphs with similar length distribution)
9. DO NOT include a references section at the end - just provide the paraphrased text

Provide ONLY the paraphrased version that maintains the exact same structure and paragraph length distribution as the original text:"""
            
            # Use Perplexity to paraphrase
            response = self.perplexity_service.perplexity.invoke(paraphrase_prompt)
            
            # Clean the paraphrased text - remove any references section
            paraphrased_text = response.content
            
            # Remove references section if it exists
            if "**References:**" in paraphrased_text:
                paraphrased_text = paraphrased_text.split("**References:**")[0].strip()
            elif "References:" in paraphrased_text:
                paraphrased_text = paraphrased_text.split("References:")[0].strip()
            
            # Try to extract sources from additional_kwargs if available
            sources = []
            if hasattr(response, 'additional_kwargs') and response.additional_kwargs:
                sources = response.additional_kwargs.get("search_results", [])
            
            # Format sources for the frontend
            formatted_sources = []
            if sources:
                for i, source in enumerate(sources[:10]):  # Limit to 10 sources
                    formatted_sources.append({
                        "id": f"ref-{i+1}",
                        "title": source.get("title", f"Reference {i+1}"),
                        "url": source.get("url", ""),
                        "snippet": source.get("snippet", ""),
                        "domain": source.get("domain", ""),
                        "order": i + 1
                    })
            
            # Format the results
            formatted_results = {
                "original_text": text,
                "paraphrased_text": paraphrased_text,
                "response_length": len(paraphrased_text),
                "timestamp": datetime.now().isoformat(),
                "paraphrase_type": "academic",
                "sources": formatted_sources,
                "success": True
            }
            
            return formatted_results
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error paraphrasing text: {str(e)}",
                "original_text": text,
                "paraphrased_text": "",
                "sources": []
            }
    
    def process_input(self, text: str) -> Dict[str, Any]:
        """
        Process input text for paraphrasing.
        
        Args:
            text (str): Text to process
            
        Returns:
            Dict with processing results
        """
        return self.paraphrase(text)

