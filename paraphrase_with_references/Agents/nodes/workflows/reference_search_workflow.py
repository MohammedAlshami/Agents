"""
Simple Reference Search Workflow
A simplified workflow for searching academic references using the References Gatherer Agent.
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add the parent directory to the path to import Agents modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from Agents.engines.search.references_gatherer import ReferencesGathererAgent

class SimpleReferenceSearchWorkflow:
    """
    Simple workflow for reference search and gathering.
    """
    
    def __init__(self, api_key: str = None, openalex_email: str = None):
        """
        Initialize the Simple Reference Search Workflow.
        
        Args:
            api_key (str): OpenAI API key. If None, will use environment variable.
            openalex_email (str): OpenAlex email for polite pool. If None, will use environment variable.
        """
        self.api_key = api_key
        self.openalex_email = openalex_email
        self.agent = ReferencesGathererAgent(
            openai_api_key=api_key,
            openalex_email=openalex_email
        )
        self.workflow_id = f"simple_reference_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def search_references(self, 
                         title: str,
                         problem_statement: str,
                         num_references: int = 20,
                         q_rating: str = "q1") -> Dict[str, Any]:
        """
        Search for academic references using OpenAlex.
        
        Args:
            title: Research paper title
            problem_statement: Problem statement or research question
            num_references: Number of references needed
            q_rating: Quality rating filter (q1, q2, q3, q4)
            
        Returns:
            Dict containing the found references
        """
        try:
            start_time = time.time()
            
            # Search for references using the agent
            result = self.agent.gather_references(
                title=title,
                problem_statement=problem_statement,
                num_references=num_references,
                q_rating=q_rating
            )
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Add workflow metadata
            result.update({
                "workflow_id": self.workflow_id,
                "model": "gpt-4o-mini",
                "agent": "reference_search",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time if 'start_time' in locals() else 0
            return {
                "success": False,
                "error": f"Error in reference search workflow: {str(e)}",
                "references": [],
                "metadata": {
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat(),
                    "num_references": num_references,
                    "queries_generated": 0,
                    "references_found": 0
                },
                "workflow_id": self.workflow_id,
                "model": "gpt-4o-mini",
                "agent": "reference_search",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_search_queries(self, 
                               title: str,
                               problem_statement: str,
                               num_references: int = 20) -> Dict[str, Any]:
        """
        Generate search queries for academic references.
        
        Args:
            title: Research paper title
            problem_statement: Problem statement or research question
            num_references: Number of references needed
            
        Returns:
            Dict containing the generated queries
        """
        try:
            start_time = time.time()
            
            # Generate search queries using the agent
            queries = self.agent.generate_search_queries(
                title=title,
                problem_statement=problem_statement,
                num_references=num_references
            )
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "queries": queries,
                "metadata": {
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat(),
                    "num_queries": len(queries),
                    "num_references": num_references
                },
                "workflow_id": self.workflow_id,
                "model": "gpt-4o-mini",
                "agent": "reference_search",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            execution_time = time.time() - start_time if 'start_time' in locals() else 0
            return {
                "success": False,
                "error": f"Error generating search queries: {str(e)}",
                "queries": [],
                "metadata": {
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat(),
                    "num_queries": 0,
                    "num_references": num_references
                },
                "workflow_id": self.workflow_id,
                "model": "gpt-4o-mini",
                "agent": "reference_search",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get workflow status and capabilities."""
        return {
            "workflow_id": self.workflow_id,
            "status": "active",
            "capabilities": [
                "Academic paper search using OpenAlex",
                "Multiple search query generation",
                "Quality rating filtering (Q1, Q2, Q3, Q4)",
                "Reference deduplication and ranking",
                "Citation count analysis",
                "Open access filtering"
            ],
            "agent_status": {
                "agent_enabled": True,
                "openai_client": self.agent.openai_client is not None,
                "openalex_service": self.agent.openalex_service is not None,
                "capabilities": [
                    "Search query generation",
                    "OpenAlex integration",
                    "Reference deduplication",
                    "Quality filtering"
                ]
            }
        }
