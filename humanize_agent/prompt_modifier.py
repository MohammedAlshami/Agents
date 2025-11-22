"""
Prompt Modifier
Uses LangChain with structured output to analyze failures and modify JSON prompt files.
Includes Perplexity search for humanization tips before prompt modification.
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_perplexity import ChatPerplexity
from pydantic import BaseModel, Field


class PromptModification(BaseModel):
    """Structured output for prompt modifications."""
    prompt_to_modify: str = Field(description="The name of the prompt file to modify (e.g., 'ai_detection_avoidance', 'natural_conversation')")
    new_prompt_content: str = Field(description="The complete new content for the prompt")
    reasoning: str = Field(description="Explanation of why this prompt was chosen and how the modification should help")


class PromptModifier:
    """
    Modifies JSON prompt files using LangChain with structured output.
    """
    
    # Map of prompt names to their JSON file paths
    PROMPT_FILES = {
        "personal_voice": "personal_voice.json",
        "natural_conversation": "natural_conversation.json",
        "ai_detection_avoidance": "ai_detection_avoidance.json",
        "content_modification": "content_modification.json",
        "human_variance": "human_variance.json",
        "academic_structure": "academic_structure.json"
    }
    
    def __init__(self, api_key: str = None, prompts_dir: str = None):
        """
        Initialize the prompt modifier.
        
        Args:
            api_key (str): OpenAI API key
            prompts_dir (str): Directory containing the prompt JSON files
        """
        # Set API key
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        # Set prompts directory
        if prompts_dir is None:
            # Default to the sub_prompts directory
            # Try multiple possible paths
            current_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                os.path.join(current_dir, "Agents", "nodes", "nodes", "ai", "humanize_agent", "prompts", "sub_prompts"),
                os.path.join(os.path.dirname(current_dir), "Agents", "nodes", "nodes", "ai", "humanize_agent", "prompts", "sub_prompts"),
            ]
            
            # Find the first path that exists
            prompts_dir = None
            for path in possible_paths:
                if os.path.exists(path) and os.path.isdir(path):
                    prompts_dir = path
                    break
            
            if prompts_dir is None:
                # Fallback to current_dir/sub_prompts
                prompts_dir = os.path.join(current_dir, "sub_prompts")
                print(f"Warning: Using fallback prompts directory: {prompts_dir}")
        
        self.prompts_dir = prompts_dir
        
        # Initialize Perplexity for online research
        perplexity_api_key = os.environ.get("PERPLEXITY_API_KEY")
        if perplexity_api_key:
            self.perplexity = ChatPerplexity(
                model="sonar",
                temperature=0.7,
                api_key=perplexity_api_key
            )
        else:
            self.perplexity = None
            print("Warning: PERPLEXITY_API_KEY not found. Skipping online research.")
        
        # Initialize the GPT-4o model for prompt modification
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            max_tokens=4000
        )
        
        # Create the prompt template for analysis
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at analyzing AI text humanization attempts and improving prompts.
Analyze the attempt data (including both successes and failures) and determine which system prompt needs modification and how to improve it.
You must identify the specific prompt file to modify and provide the complete new content for that prompt.

Your goal is to improve the humanization effectiveness so that humanized text achieves 0% AI detection.
Look for patterns in what works and what doesn't work across all attempts."""),
            ("human", """Analyze the following attempt data and determine which prompt should be modified:

ATTEMPT DATA AND ONLINE RESEARCH:
{failure_history}

CURRENT PROMPTS:
{current_prompts}

The attempt data includes:
- Statistics about recent attempts (success rates, AI detection percentages)
- Detailed information about each attempt
- Online research results from Perplexity with latest humanization tips and techniques

Based on the attempt patterns AND the online research findings, determine:
1. Which prompt file should be modified (one of: {prompt_names})
2. The complete new content for that prompt that should improve humanization effectiveness
3. Your detailed reasoning for the modification, including:
   - What patterns you observed in the attempts
   - Which tips from the online research are most relevant
   - Why this specific prompt needs modification
   - How the new content incorporates the research findings
   - How the new content will improve results

Focus on improving the prompt to better avoid AI detection and create more human-like text that scores 0% on AI detection tools.
Consider both successful and failed attempts to understand what works and what doesn't.
Incorporate the latest techniques and best practices from the online research.""")
        ])
        
        # Create chain with structured output
        self.chain = self.analysis_prompt | self.llm.with_structured_output(PromptModification)
    
    def load_prompt(self, prompt_name: str) -> Dict[str, Any]:
        """
        Load a prompt from its JSON file.
        
        Args:
            prompt_name (str): Name of the prompt to load
            
        Returns:
            Dict with prompt data
        """
        if prompt_name not in self.PROMPT_FILES:
            raise ValueError(f"Unknown prompt name: {prompt_name}")
        
        json_file = os.path.join(self.prompts_dir, self.PROMPT_FILES[prompt_name])
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {json_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in prompt file {json_file}: {e}")
    
    def load_all_prompts(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all prompts.
        
        Returns:
            Dict mapping prompt names to their content
        """
        prompts = {}
        for prompt_name in self.PROMPT_FILES.keys():
            try:
                prompts[prompt_name] = self.load_prompt(prompt_name)
            except Exception as e:
                print(f"Warning: Could not load prompt {prompt_name}: {e}")
        return prompts
    
    def update_prompt(self, prompt_name: str, new_content: str) -> bool:
        """
        Update a prompt JSON file with new content.
        
        Args:
            prompt_name (str): Name of the prompt to update
            new_content (str): New content for the prompt
            
        Returns:
            bool: True if successful, False otherwise
        """
        if prompt_name not in self.PROMPT_FILES:
            print(f"Error: Unknown prompt name: {prompt_name}")
            return False
        
        json_file = os.path.join(self.prompts_dir, self.PROMPT_FILES[prompt_name])
        
        try:
            # Load existing prompt to preserve metadata
            existing_prompt = self.load_prompt(prompt_name)
            
            # Update content
            existing_prompt["content"] = new_content
            existing_prompt["last_modified"] = datetime.now().isoformat()
            
            # Create backup
            backup_file = json_file + ".backup"
            if os.path.exists(json_file):
                import shutil
                shutil.copy2(json_file, backup_file)
            
            # Write updated prompt
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(existing_prompt, f, indent=2, ensure_ascii=False)
            
            print(f"Updated prompt: {prompt_name}")
            print(f"Backup saved to: {backup_file}")
            return True
            
        except Exception as e:
            print(f"Error updating prompt {prompt_name}: {e}")
            return False
    
    def search_humanization_tips(self, attempts: List[Dict[str, Any]]) -> str:
        """
        Search Perplexity for humanization tips based on the attempts.
        
        Args:
            attempts: List of attempt records
            
        Returns:
            String with search results and tips
        """
        if not self.perplexity:
            return "Perplexity API not available. Skipping online research."
        
        try:
            # Format attempts summary for search query
            total_attempts = len(attempts)
            successful_attempts = sum(1 for a in attempts if a.get('success', False))
            avg_original_ai = sum(a.get('original_ai_percent', 0) for a in attempts) / total_attempts if total_attempts > 0 else 0
            avg_humanized_ai = sum(a.get('humanized_ai_percent', 0) for a in attempts) / total_attempts if total_attempts > 0 else 0
            
            # Create search query with iteration context
            iteration_info = ""
            if attempts and attempts[0].get('iteration'):
                iteration_info = f"Current iteration: {attempts[0].get('iteration')}"
            
            search_query = f"""I'm working on humanizing AI-generated text to avoid AI detection using ZeroGPT. {iteration_info}

Here are my recent attempt(s):
- Total attempts: {total_attempts}
- Successful attempts (0% AI detection): {successful_attempts}
- Average original AI%: {avg_original_ai:.2f}%
- Average humanized AI%: {avg_humanized_ai:.2f}%
- Average improvement: {avg_original_ai - avg_humanized_ai:.2f}% reduction

The goal is to achieve 0% AI detection on ZeroGPT. Please search for:
1. Latest techniques and tips for humanizing AI text to avoid ZeroGPT detection
2. Methods to avoid AI detection tools like ZeroGPT specifically
3. Best practices for making AI text sound more human
4. Common mistakes that cause high AI detection rates on ZeroGPT
5. Specific strategies that have proven effective for ZeroGPT
6. What patterns does ZeroGPT detect and how to avoid them

Focus on practical, actionable advice that can be implemented in system prompts for text humanization."""
            
            # Search using Perplexity
            print("Searching Perplexity for humanization tips...")
            response = self.perplexity.invoke(search_query)
            # Extract content from the response
            search_result = response.content if hasattr(response, 'content') else str(response)
            
            return f"""PERPLEXITY SEARCH RESULTS - HUMANIZATION TIPS:

{search_result}

---
These tips should be considered when modifying the prompts to improve humanization effectiveness."""
            
        except Exception as e:
            return f"Error searching Perplexity: {str(e)}. Continuing without online research."
    
    def analyze_and_modify(self, attempts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze attempts and modify prompts accordingly.
        First searches Perplexity for humanization tips, then uses OpenAI to modify prompts.
        
        Args:
            attempts: List of attempt records with topic, original_ai_percent, humanized_ai_percent, success, etc.
            
        Returns:
            Dict with modification results
        """
        try:
            # Step 1: Search Perplexity for humanization tips
            perplexity_results = self.search_humanization_tips(attempts)
            
            # Load all current prompts
            current_prompts = self.load_all_prompts()
            
            # Format prompts for analysis (show full content, not truncated)
            prompts_text = "\n\n".join([
                f"=== {name} ===\n{data.get('content', '')}"
                for name, data in current_prompts.items()
            ])
            
            # Format attempts with detailed information
            attempts_text = "\n\n".join([
                f"Iteration {a.get('iteration', i+1)}:\n"
                f"  Topic: {a.get('topic', 'Unknown')}\n"
                f"  Original AI%: {a.get('original_ai_percent', 0):.2f}%\n"
                f"  Humanized AI%: {a.get('humanized_ai_percent', 0):.2f}%\n"
                f"  Improvement: {a.get('original_ai_percent', 0) - a.get('humanized_ai_percent', 0):.2f}% reduction\n"
                f"  Success: {a.get('success', False)} (Required: 0.00%)\n"
                f"  Original Paragraph Preview: {a.get('original_paragraph', '')[:150]}...\n"
                f"  Humanized Paragraph Preview: {a.get('humanized_paragraph', '')[:150]}..."
                for i, a in enumerate(attempts)
            ])
            
            # Calculate statistics
            total_attempts = len(attempts)
            successful_attempts = sum(1 for a in attempts if a.get('success', False))
            avg_original_ai = sum(a.get('original_ai_percent', 0) for a in attempts) / total_attempts if total_attempts > 0 else 0
            avg_humanized_ai = sum(a.get('humanized_ai_percent', 0) for a in attempts) / total_attempts if total_attempts > 0 else 0
            
            # Get prompt names
            prompt_names = ", ".join(self.PROMPT_FILES.keys())
            
            # Analyze and get modification (now includes Perplexity results)
            modification = self.chain.invoke({
                "failure_history": f"""ATTEMPT ANALYSIS:
Total Attempts: {total_attempts}
Successful Attempts: {successful_attempts}
Success Rate: {(successful_attempts/total_attempts*100):.2f}%
Average Original AI%: {avg_original_ai:.2f}%
Average Humanized AI%: {avg_humanized_ai:.2f}%

DETAILED ATTEMPTS:
{attempts_text}

{perplexity_results}""",
                "current_prompts": prompts_text,
                "prompt_names": prompt_names
            })
            
            # Update the prompt
            success = self.update_prompt(
                modification.prompt_to_modify,
                modification.new_prompt_content
            )
            
            return {
                "success": success,
                "prompt_modified": modification.prompt_to_modify,
                "reasoning": modification.reasoning,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": f"{str(e)}\n{traceback.format_exc()}",
                "timestamp": datetime.now().isoformat()
            }

