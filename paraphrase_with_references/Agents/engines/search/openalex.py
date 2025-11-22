"""
OpenAlex search service for academic paper search and ranking.
"""

import os
import json
import time
import requests
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from urllib.parse import urlencode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class SearchResult:
    """Data class for search results."""
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

class OpenAlexSearchService:
    """Service class for OpenAlex academic search operations."""
    
    def __init__(self, email: Optional[str] = None):
        """
        Initialize OpenAlex service.
        
        Args:
            email: Email for polite pool (10 req/sec vs 1 req/sec)
        """
        self.base_url = "https://api.openalex.org"
        self.email = email or os.getenv("OPENALEX_EMAIL")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1 if self.email else 1.0  # 10 req/sec with email, 1 req/sec without
        
    def _rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request to OpenAlex API with rate limiting and error handling.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response data
        """
        self._rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        if params is None:
            params = {}
            
        # Add email for polite pool if available
        if self.email:
            params['mailto'] = self.email
            
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 403:
                print(f"OpenAlex API rate limited or forbidden. Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return {}
            elif response.status_code != 200:
                print(f"OpenAlex API request failed with status {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return {}
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"OpenAlex API request failed: {e}")
            return {}
    
    def search_works(self, 
                    query: str = None,
                    author_id: str = None,
                    institution_id: str = None,
                    source_id: str = None,
                    topic_id: str = None,
                    publication_year: Union[int, str] = None,
                    is_open_access: bool = None,
                    has_doi: bool = None,
                    has_fulltext: bool = None,
                    work_type: str = None,
                    sort_by: str = "cited_by_count:desc",
                    per_page: int = 25,
                    page: int = 1,
                    sample: int = None,
                    seed: int = None) -> List[SearchResult]:
        """
        Search for academic works with various filters.
        
        Args:
            query: Search query string
            author_id: Filter by author ID
            institution_id: Filter by institution ID
            source_id: Filter by source (journal) ID
            topic_id: Filter by topic ID
            publication_year: Filter by publication year (int or range string like "2020-2023")
            is_open_access: Filter by open access status
            has_doi: Filter by DOI availability
            has_fulltext: Filter by fulltext availability
            work_type: Filter by work type (article, book, dataset, etc.)
            sort_by: Sort order (cited_by_count:desc, publication_date:desc, etc.)
            per_page: Results per page (max 200)
            page: Page number
            sample: Random sample size
            seed: Seed for reproducible sampling
            
        Returns:
            List of SearchResult objects
        """
        params = {
            'per-page': min(per_page, 200),
            'page': page
        }
        
        # Only add sort if specified (can't use with sample)
        if sort_by:
            params['sort'] = sort_by
        
        # Add search query
        if query:
            params['search'] = query
            
        # Add filters
        filters = []
        if author_id:
            filters.append(f"authorships.author.id:{author_id}")
        if institution_id:
            filters.append(f"authorships.institutions.id:{institution_id}")
        if source_id:
            filters.append(f"primary_location.source.id:{source_id}")
        if topic_id:
            filters.append(f"topics.id:{topic_id}")
        if publication_year is not None:
            if isinstance(publication_year, int):
                filters.append(f"publication_year:{publication_year}")
            else:
                filters.append(f"publication_year:{publication_year}")
        if is_open_access is not None:
            filters.append(f"is_oa:{str(is_open_access).lower()}")
        if has_doi is not None:
            filters.append(f"has_doi:{str(has_doi).lower()}")
        if has_fulltext is not None:
            filters.append(f"has_fulltext:{str(has_fulltext).lower()}")
        if work_type:
            filters.append(f"type:{work_type}")
        
        # Optional: Filter for works that have abstracts (can be disabled if too restrictive)
        # filters.append("has_abstract:true")
            
        if filters:
            params['filter'] = ','.join(filters)
            
        # Add sampling parameters
        if sample:
            params['sample'] = sample
            if seed:
                params['seed'] = seed
        
        # Select only needed fields for performance
        params['select'] = 'id,title,publication_year,cited_by_count,doi,open_access,type,primary_location,locations,topics,authorships,abstract_inverted_index'
        
        response = self._make_request('/works', params)
        
        if not response or 'results' not in response:
            return []
            
        results = []
        for work in response['results']:
            try:
                # Extract authors
                authors = []
                if 'authorships' in work and work['authorships']:
                    for authorship in work['authorships']:
                        if authorship and 'author' in authorship and authorship['author'] and 'display_name' in authorship['author']:
                            authors.append(authorship['author']['display_name'])
                
                # Extract topics
                topics = []
                if 'topics' in work and work['topics']:
                    for topic in work['topics']:
                        if topic and 'display_name' in topic:
                            topics.append(topic['display_name'])
                
                # Extract source
                source = None
                if 'primary_location' in work and work['primary_location']:
                    if 'source' in work['primary_location'] and work['primary_location']['source']:
                        source = work['primary_location']['source'].get('display_name')
                
                # Extract URL and PDF URL
                url = None
                pdf_url = None
                if 'primary_location' in work and work['primary_location']:
                    url = work['primary_location'].get('landing_page_url')
                    pdf_url = work['primary_location'].get('pdf_url')
                
                # If no PDF URL in primary location, check all locations for best PDF
                if not pdf_url and 'locations' in work and work['locations']:
                    for location in work['locations']:
                        if location and location.get('pdf_url'):
                            pdf_url = location.get('pdf_url')
                            break
                
                # Extract and convert abstract from inverted index format
                abstract = None
                abstract_inverted = work.get('abstract_inverted_index')
                if abstract_inverted:
                    abstract = self._convert_inverted_index_to_text(abstract_inverted)
                
                result = SearchResult(
                    id=work.get('id', ''),
                    title=work.get('title', ''),
                    authors=authors,
                    publication_year=work.get('publication_year'),
                    citation_count=work.get('cited_by_count', 0),
                    abstract=abstract,
                    doi=work.get('doi'),
                    url=url,
                    pdf_url=pdf_url,
                    source=source,
                    is_open_access=work.get('open_access', {}).get('is_oa', False) if work.get('open_access') else False,
                    topics=topics,
                    type=work.get('type', '')
                )
                results.append(result)
            except Exception as e:
                print(f"Error parsing work result: {e}")
                continue
                
        return results
    
    def search_by_ranking(self, 
                         topic: str = None,
                         year_range: str = None,
                         min_citations: int = 0,
                         limit: int = 50) -> List[SearchResult]:
        """
        Search for highly ranked papers by citations.
        
        Args:
            topic: Topic to search within
            year_range: Year range (e.g., "2020-2023")
            min_citations: Minimum citation count
            limit: Maximum number of results
            
        Returns:
            List of highly ranked SearchResult objects
        """
        filters = []
        if min_citations > 0:
            filters.append(f"cited_by_count:>={min_citations}")
        if year_range:
            filters.append(f"publication_year:{year_range}")
            
        return self.search_works(
            query=topic,
            sort_by="cited_by_count:desc",
            per_page=min(limit, 200),
            page=1
        )
    
    def search_by_author(self, author_name: str, limit: int = 25) -> List[SearchResult]:
        """
        Search for works by a specific author.
        
        Args:
            author_name: Name of the author
            limit: Maximum number of results
            
        Returns:
            List of SearchResult objects by the author
        """
        # First, find the author ID
        author_id = self._find_author_id(author_name)
        if not author_id:
            return []
            
        return self.search_works(
            author_id=author_id,
            sort_by="cited_by_count:desc",
            per_page=min(limit, 200)
        )
    
    def search_by_institution(self, institution_name: str, limit: int = 25) -> List[SearchResult]:
        """
        Search for works from a specific institution.
        
        Args:
            institution_name: Name of the institution
            limit: Maximum number of results
            
        Returns:
            List of SearchResult objects from the institution
        """
        # First, find the institution ID
        institution_id = self._find_institution_id(institution_name)
        if not institution_id:
            return []
            
        return self.search_works(
            institution_id=institution_id,
            sort_by="cited_by_count:desc",
            per_page=min(limit, 200)
        )
    
    def search_by_topic(self, topic: str, limit: int = 25) -> List[SearchResult]:
        """
        Search for works by topic.
        
        Args:
            topic: Topic name
            limit: Maximum number of results
            
        Returns:
            List of SearchResult objects on the topic
        """
        # First, find the topic ID
        topic_id = self._find_topic_id(topic)
        if not topic_id:
            return []
            
        return self.search_works(
            topic_id=topic_id,
            sort_by="cited_by_count:desc",
            per_page=min(limit, 200)
        )
    
    def get_work_details(self, work_id: str) -> Optional[SearchResult]:
        """
        Get detailed information about a specific work.
        
        Args:
            work_id: OpenAlex work ID or DOI
            
        Returns:
            SearchResult object or None if not found
        """
        # Handle DOI format
        if work_id.startswith('10.'):
            work_id = f"https://doi.org/{work_id}"
        elif not work_id.startswith('https://'):
            work_id = f"https://openalex.org/{work_id}"
            
        response = self._make_request(f'/works/{work_id}')
        
        if not response:
            return None
            
        try:
            # Extract authors
            authors = []
            if 'authorships' in response:
                for authorship in response['authorships']:
                    if 'author' in authorship and 'display_name' in authorship['author']:
                        authors.append(authorship['author']['display_name'])
            
            # Extract topics
            topics = []
            if 'topics' in response:
                for topic in response['topics']:
                    if 'display_name' in topic:
                        topics.append(topic['display_name'])
            
            # Extract source
            source = None
            if 'primary_location' in response and response['primary_location']:
                if 'source' in response['primary_location'] and response['primary_location']['source']:
                    source = response['primary_location']['source'].get('display_name')
            
            # Extract URL and PDF URL
            url = None
            pdf_url = None
            if 'primary_location' in response and response['primary_location']:
                url = response['primary_location'].get('landing_page_url')
                pdf_url = response['primary_location'].get('pdf_url')
            
            # If no PDF URL in primary location, check all locations for best PDF
            if not pdf_url and 'locations' in response and response['locations']:
                for location in response['locations']:
                    if location and location.get('pdf_url'):
                        pdf_url = location.get('pdf_url')
                        break
            
            # Extract and convert abstract from inverted index format
            abstract = None
            abstract_inverted = response.get('abstract_inverted_index')
            if abstract_inverted:
                abstract = self._convert_inverted_index_to_text(abstract_inverted)
            
            return SearchResult(
                id=response.get('id', ''),
                title=response.get('title', ''),
                authors=authors,
                publication_year=response.get('publication_year'),
                citation_count=response.get('cited_by_count', 0),
                abstract=abstract,
                doi=response.get('doi'),
                url=url,
                pdf_url=pdf_url,
                source=source,
                is_open_access=response.get('open_access', {}).get('is_oa', False),
                topics=topics,
                type=response.get('type', '')
            )
        except Exception as e:
            print(f"Error parsing work details: {e}")
            return None
    
    def _convert_inverted_index_to_text(self, inverted_index: Dict[str, List[int]]) -> str:
        """
        Convert OpenAlex inverted index format to readable text.
        
        Args:
            inverted_index: Dictionary mapping words to their positions
            
        Returns:
            Reconstructed text string
        """
        try:
            # Create a list to hold all words with their positions
            word_positions = []
            
            for word, positions in inverted_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            
            # Sort by position
            word_positions.sort(key=lambda x: x[0])
            
            # Extract just the words and join them
            words = [word for pos, word in word_positions]
            
            # Join words with spaces
            text = ' '.join(words)
            
            # Clean up common artifacts
            text = text.replace('  ', ' ')  # Remove double spaces
            text = text.strip()
            
            return text
            
        except Exception as e:
            print(f"Error converting inverted index to text: {e}")
            return None
    
    def _find_author_id(self, author_name: str) -> Optional[str]:
        """Find author ID by name."""
        response = self._make_request('/authors', {
            'search': author_name,
            'per-page': 1
        })
        
        if response and 'results' in response and response['results']:
            return response['results'][0]['id']
        return None
    
    def _find_institution_id(self, institution_name: str) -> Optional[str]:
        """Find institution ID by name."""
        response = self._make_request('/institutions', {
            'search': institution_name,
            'per-page': 1
        })
        
        if response and 'results' in response and response['results']:
            return response['results'][0]['id']
        return None
    
    def _find_topic_id(self, topic_name: str) -> Optional[str]:
        """Find topic ID by name."""
        response = self._make_request('/topics', {
            'search': topic_name,
            'per-page': 1
        })
        
        if response and 'results' in response and response['results']:
            return response['results'][0]['id']
        return None
    
    def get_random_sample(self, topic: str = None, sample_size: int = 100, seed: int = None) -> List[SearchResult]:
        """
        Get a random sample of works.
        
        Args:
            topic: Optional topic filter
            sample_size: Number of samples
            seed: Seed for reproducible sampling
            
        Returns:
            List of randomly sampled SearchResult objects
        """
        return self.search_works(
            query=topic,
            sample=sample_size,
            seed=seed,
            sort_by=None  # Can't use sort with sample
        )
    
    def get_trending_papers(self, days: int = 30, limit: int = 50) -> List[SearchResult]:
        """
        Get recently published papers (trending).
        
        Args:
            days: Number of days back to look
            limit: Maximum number of results
            
        Returns:
            List of recent SearchResult objects
        """
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return self.search_works(
            publication_year=f"{start_date.year}-{end_date.year}",
            sort_by="publication_date:desc",
            per_page=min(limit, 200)
        )

# Global instance
openalex_service = OpenAlexSearchService()

# Example usage function
def example_usage():
    """Example of how to use the OpenAlex service."""
    try:
        # Initialize the service
        service = OpenAlexSearchService(email="your-email@example.com")
        
        # Example 1: Search by topic
        print("=== Search by Topic ===")
        results = service.search_by_topic("artificial intelligence", limit=5)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.title}")
            print(f"   Authors: {', '.join(result.authors[:3])}")
            print(f"   Citations: {result.citation_count}")
            print(f"   Year: {result.publication_year}")
            print(f"   Open Access: {result.is_open_access}")
            print()
        
        # Example 2: Search by ranking
        print("=== Highly Ranked Papers ===")
        results = service.search_by_ranking(
            topic="machine learning",
            min_citations=100,
            limit=5
        )
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.title}")
            print(f"   Citations: {result.citation_count}")
            print(f"   Year: {result.publication_year}")
            print()
        
        # Example 3: Search by author
        print("=== Search by Author ===")
        results = service.search_by_author("Geoffrey Hinton", limit=3)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.title}")
            print(f"   Citations: {result.citation_count}")
            print(f"   Year: {result.publication_year}")
            print()
        
        # Example 4: Get work details
        print("=== Work Details ===")
        # Using a known DOI
        work = service.get_work_details("10.1038/nature14539")
        if work:
            print(f"Title: {work.title}")
            print(f"Authors: {', '.join(work.authors)}")
            print(f"Citations: {work.citation_count}")
            print(f"DOI: {work.doi}")
            print(f"Open Access: {work.is_open_access}")
        
        # Example 5: Random sample
        print("\n=== Random Sample ===")
        results = service.get_random_sample("neural networks", sample_size=3, seed=42)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.title}")
            print(f"   Citations: {result.citation_count}")
            print()
        
        # Example 6: Trending papers
        print("=== Trending Papers (Last 30 days) ===")
        results = service.get_trending_papers(days=30, limit=3)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.title}")
            print(f"   Year: {result.publication_year}")
            print(f"   Citations: {result.citation_count}")
            print()
        
    except Exception as e:
        print(f"Error in example usage: {e}")

if __name__ == "__main__":
    example_usage()
