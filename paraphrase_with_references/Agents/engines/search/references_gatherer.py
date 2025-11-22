"""
References Gatherer Agent
Generates multiple search queries from a title and problem statement, then searches OpenAlex for academic references.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class ReferenceResult:
    """Data class for reference results."""
    id: str
    title: str
    authors: List[str]
    publication_year: Optional[int]
    citation_count: int
    abstract: Optional[str]
    doi: Optional[str]
    url: Optional[str]
    pdf_url: Optional[str]
    source: Optional[str]
    is_open_access: bool
    topics: List[str]
    type: str
    query_used: str  # Which query found this reference

class ReferencesGathererAgent:
    """
    Agent that generates multiple search queries from a title and problem statement,
    then searches OpenAlex to gather academic references.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, openalex_email: Optional[str] = None):
        """
        Initialize the References Gatherer Agent.
        
        Args:
            openai_api_key: OpenAI API key for query generation
            openalex_email: Email for OpenAlex polite pool
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.openalex_email = openalex_email or os.getenv("OPENALEX_EMAIL")
        
        # Initialize OpenAI client
        self.openai_client = None
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        # Initialize OpenAlex service
        from Agents.engines.search.openalex import OpenAlexSearchService
        self.openalex_service = OpenAlexSearchService(email=self.openalex_email)
        
        # Rate limiting for OpenAI
        self.last_openai_request = 0
        self.openai_min_interval = 1.0  # 1 second between requests
    
    def _rate_limit_openai(self):
        """Implement rate limiting for OpenAI requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_openai_request
        
        if time_since_last < self.openai_min_interval:
            time.sleep(self.openai_min_interval - time_since_last)
        
        self.last_openai_request = time.time()
    
    def generate_search_queries(self, title: str, problem_statement: str, num_references: int) -> List[str]:
        """
        Generate structured search queries for different sections of a research paper.
        
        Args:
            title: Research paper title
            problem_statement: Problem statement or research question
            num_references: Number of references needed
            
        Returns:
            List of search queries organized by research paper sections
        """
        try:
            self._rate_limit_openai()
            
            prompt = f"""
You are an expert academic researcher. Generate 9 diverse search queries for academic papers related to:

Title: {title}
Problem Statement: {problem_statement}

Generate exactly 9 search queries that cover different aspects:

1. General topic overview
2. Recent developments and trends
3. Methodological approaches
4. Applications and case studies
5. Challenges and limitations
6. Theoretical foundations
7. Comparative studies
8. Future directions
9. Cross-disciplinary connections

Requirements:
1. Use simple, effective keywords
2. Avoid overly complex Boolean operators
3. Keep queries concise (under 80 characters each)
4. Make each query distinct and focused
5. Use terms that are likely to appear in academic papers

Return only the 9 search queries, one per line, without numbering.
"""

            if not self.openai_client:
                raise ValueError("OpenAI client not initialized. Please provide OPENAI_API_KEY.")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert academic researcher who generates structured search queries for different sections of research papers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            queries_text = response.choices[0].message.content.strip()
            queries = [q.strip() for q in queries_text.split('\n') if q.strip()]
            
            # Ensure we have exactly 9 queries
            if len(queries) < 9:
                # Add fallback queries if we don't have enough
                fallback_queries = [
                    f"{title} overview",
                    f"{title} applications",
                    f"{title} methods",
                    f"{title} challenges",
                    f"{title} future directions"
                ]
                for fallback in fallback_queries:
                    if len(queries) < 9:
                        queries.append(fallback)
            
            # Limit to exactly 9 queries
            queries = queries[:9]
            
            return queries
            
        except Exception as e:
            print(f"Error generating search queries: {e}")
            # Fallback queries
            return [
                title,
                problem_statement,
                f"{title} methodology",
                f"{title} applications",
                f"{title} case study"
            ][:9]  # Return up to 9 fallback queries
    
    def search_references(self, queries: List[str], num_references: int, q_rating: str = "q1") -> List[ReferenceResult]:
        """
        Search for references using the generated queries.
        
        Args:
            queries: List of search queries
            num_references: Number of references needed
            q_rating: Quality rating filter (q1, q2, q3, q4)
            
        Returns:
            List of reference results
        """
        all_references = []
        seen_ids = set()
        
        # Map Q rating to citation thresholds (reduced for better results)
        q_rating_citations = {
            "q1": 20,  # Reduced from 100
            "q2": 10,  # Reduced from 50
            "q3": 5,   # Reduced from 20
            "q4": 0
        }
        
        min_citations = q_rating_citations.get(q_rating, 0)
        
        # Calculate references per query type (distribute across research sections)
        references_per_query = max(1, num_references // len(queries))
        
        for i, query in enumerate(queries):
            try:
                # For the last query, get remaining references
                target_count = references_per_query
                if i == len(queries) - 1:
                    target_count = num_references - len(all_references)
                
                if target_count <= 0:
                    break
                
                # Search OpenAlex
                search_results = self.openalex_service.search_works(
                    query=query,
                    sort_by="cited_by_count:desc",
                    per_page=min(100, target_count * 3)  # Get more results to filter
                )
                
                # Filter by citation count and add to results
                query_references = 0
                for result in search_results:
                    if (result.citation_count >= min_citations and 
                        result.id not in seen_ids and 
                        query_references < target_count):
                        
                        reference = ReferenceResult(
                            id=result.id,
                            title=result.title,
                            authors=result.authors,
                            publication_year=result.publication_year,
                            citation_count=result.citation_count,
                            abstract=result.abstract,
                            doi=result.doi,
                            url=result.url,
                            pdf_url=result.pdf_url,
                            source=result.source,
                            is_open_access=result.is_open_access,
                            topics=result.topics,
                            type=result.type,
                            query_used=query
                        )
                        
                        all_references.append(reference)
                        seen_ids.add(result.id)
                        query_references += 1
                
                print(f"Query {i+1} ({query[:50]}...): Found {query_references} references")
                
                # Stop if we have enough references
                if len(all_references) >= num_references:
                    break
                    
            except Exception as e:
                print(f"Error searching with query '{query}': {e}")
                continue
        
        return all_references[:num_references]
    
    def gather_references(self, title: str, problem_statement: str, num_references: int, q_rating: str = "q1") -> Dict[str, Any]:
        """
        Main method to gather references for a research paper.
        
        Args:
            title: Research paper title
            problem_statement: Problem statement or research question
            num_references: Number of references needed
            q_rating: Quality rating filter (q1, q2, q3, q4)
            
        Returns:
            Dictionary with references and metadata
        """
        try:
            start_time = datetime.now()
            
            # Generate search queries
            print(f"Generating search queries for: {title}")
            queries = self.generate_search_queries(title, problem_statement, num_references)
            print(f"Generated {len(queries)} search queries")
            
            # Search for references
            print(f"Searching for {num_references} references...")
            references = self.search_references(queries, num_references, q_rating)
            print(f"Found {len(references)} references")
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Convert references to dictionary format
            references_data = []
            for ref in references:
                references_data.append({
                    "id": ref.id,
                    "title": ref.title,
                    "authors": ref.authors,
                    "publication_year": ref.publication_year,
                    "citation_count": ref.citation_count,
                    "abstract": ref.abstract,
                    "doi": ref.doi,
                    "url": ref.url,
                    "pdf_url": ref.pdf_url,
                    "source": ref.source,
                    "is_open_access": ref.is_open_access,
                    "topics": ref.topics,
                    "type": ref.type,
                    "query_used": ref.query_used
                })
            
            return {
                "success": True,
                "references": references_data,
                "total_found": len(references),
                "queries_used": queries,
                "metadata": {
                    "title": title,
                    "problem_statement": problem_statement,
                    "num_references_requested": num_references,
                    "q_rating": q_rating,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"References gathering failed: {str(e)}",
                "references": [],
                "total_found": 0,
                "queries_used": [],
                "metadata": {
                    "title": title,
                    "problem_statement": problem_statement,
                    "num_references_requested": num_references,
                    "q_rating": q_rating,
                    "execution_time": 0,
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the system status of the References Gatherer Agent.
        
        Returns:
            Dict with system status information
        """
        return {
            "agent_enabled": True,
            "openai_configured": bool(self.openai_api_key),
            "openalex_configured": bool(self.openalex_email),
            "rate_limits": {
                "openai": "1 req/sec",
                "openalex": "10 req/sec with email, 1 req/sec without"
            },
            "capabilities": [
                "Query generation using GPT-3.5-turbo",
                "OpenAlex academic search",
                "Reference deduplication",
                "Quality filtering by citation count"
            ]
        }
