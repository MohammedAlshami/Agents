#!/usr/bin/env python3
"""
Fetch business journal papers from ScienceDirect before 2020 using OpenAlex
and save abstracts for analysis of real academic writing patterns.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Any

# Add the reference search agent path to import OpenAlex
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'reference_search_agent'))

from Agents.engines.search.openalex import OpenAlexSearchService

def fetch_business_papers():
    """Fetch business journal papers from ScienceDirect before 2020."""
    
    # Initialize OpenAlex service
    service = OpenAlexSearchService()
    
    # Business journal sources on ScienceDirect (common ones)
    business_sources = [
        "Journal of Business Research",
        "Journal of Business Ethics", 
        "Strategic Management Journal",
        "Academy of Management Journal",
        "Academy of Management Review",
        "Organization Science",
        "Administrative Science Quarterly",
        "Journal of Management",
        "Journal of Management Studies",
        "Management Science",
        "Harvard Business Review",
        "MIT Sloan Management Review",
        "California Management Review",
        "Long Range Planning",
        "Journal of International Business Studies"
    ]
    
    all_abstracts = []
    total_papers = 0
    
    print("Fetching business journal papers from ScienceDirect before 2020...")
    print("=" * 60)
    
    for source in business_sources:
        print(f"\nSearching in: {source}")
        
        try:
            # Search for papers from this source before 2020
            results = service.search_works(
                query=f'source:"{source}"',
                publication_year="2015-2019",  # Papers before 2020
                has_fulltext=True,  # Only papers with abstracts
                sort_by="cited_by_count:desc",
                per_page=50  # Get top 50 most cited papers
            )
            
            source_count = 0
            for result in results:
                if result.abstract and len(result.abstract.strip()) > 100:  # Only abstracts with substantial content
                    abstract_data = {
                        "title": result.title,
                        "authors": result.authors,
                        "year": result.publication_year,
                        "citations": result.citation_count,
                        "source": result.source,
                        "abstract": result.abstract,
                        "doi": result.doi
                    }
                    all_abstracts.append(abstract_data)
                    source_count += 1
                    total_papers += 1
                    
                    print(f"  ✓ {result.title[:60]}... ({result.publication_year}) - {result.citation_count} citations")
            
            print(f"  Found {source_count} papers with abstracts from {source}")
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"  Error searching {source}: {e}")
            continue
    
    print(f"\n" + "=" * 60)
    print(f"TOTAL PAPERS FETCHED: {total_papers}")
    print(f"TOTAL SOURCES SEARCHED: {len(business_sources)}")
    
    # Save abstracts to text file
    output_file = "business_papers_abstracts.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("BUSINESS JOURNAL PAPERS ABSTRACTS (2015-2019)\n")
        f.write("=" * 60 + "\n\n")
        
        for i, paper in enumerate(all_abstracts, 1):
            f.write(f"PAPER {i}:\n")
            f.write(f"Title: {paper['title']}\n")
            f.write(f"Authors: {', '.join(paper['authors'][:3])}\n")
            f.write(f"Year: {paper['year']}\n")
            f.write(f"Citations: {paper['citations']}\n")
            f.write(f"Source: {paper['source']}\n")
            f.write(f"DOI: {paper['doi']}\n")
            f.write(f"Abstract: {paper['abstract']}\n")
            f.write("-" * 60 + "\n\n")
    
    print(f"\nAbstracts saved to: {output_file}")
    
    # Also save as JSON for easier processing
    json_file = "business_papers_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_abstracts, f, indent=2, ensure_ascii=False)
    
    print(f"Data saved to: {json_file}")
    
    return all_abstracts

def analyze_writing_patterns(abstracts: List[Dict[str, Any]]):
    """Analyze writing patterns from the fetched abstracts."""
    
    print("\n" + "=" * 60)
    print("ANALYZING WRITING PATTERNS")
    print("=" * 60)
    
    # Extract all abstracts
    all_abstract_texts = [paper['abstract'] for paper in abstracts if paper['abstract']]
    
    # Analyze sentence patterns
    sentence_starters = {}
    transition_words = {}
    common_phrases = {}
    
    for abstract in all_abstract_texts:
        sentences = abstract.split('. ')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue
                
            # Get first few words
            words = sentence.split()
            if len(words) >= 2:
                starter = f"{words[0]} {words[1]}".lower()
                sentence_starters[starter] = sentence_starters.get(starter, 0) + 1
            
            # Look for transition words
            for word in words:
                word_lower = word.lower().rstrip('.,;:')
                if word_lower in ['however', 'moreover', 'furthermore', 'additionally', 'consequently', 'therefore', 'thus', 'hence', 'meanwhile', 'nevertheless', 'nonetheless']:
                    transition_words[word_lower] = transition_words.get(word_lower, 0) + 1
    
    # Print analysis
    print(f"\nAnalyzed {len(all_abstract_texts)} abstracts")
    
    print("\nTOP SENTENCE STARTERS:")
    sorted_starters = sorted(sentence_starters.items(), key=lambda x: x[1], reverse=True)
    for starter, count in sorted_starters[:10]:
        print(f"  {starter}: {count} times")
    
    print("\nTOP TRANSITION WORDS:")
    sorted_transitions = sorted(transition_words.items(), key=lambda x: x[1], reverse=True)
    for word, count in sorted_transitions[:10]:
        print(f"  {word}: {count} times")
    
    # Save analysis
    analysis_file = "writing_patterns_analysis.txt"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        f.write("ACADEMIC WRITING PATTERNS ANALYSIS\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Analyzed {len(all_abstract_texts)} abstracts from business journals (2015-2019)\n\n")
        
        f.write("TOP SENTENCE STARTERS:\n")
        for starter, count in sorted_starters[:20]:
            f.write(f"  {starter}: {count} times\n")
        
        f.write("\nTOP TRANSITION WORDS:\n")
        for word, count in sorted_transitions[:20]:
            f.write(f"  {word}: {count} times\n")
        
        f.write("\nSAMPLE ABSTRACTS FOR REFERENCE:\n")
        f.write("-" * 40 + "\n")
        for i, paper in enumerate(abstracts[:5], 1):
            f.write(f"\nSample {i}:\n")
            f.write(f"Title: {paper['title']}\n")
            f.write(f"Source: {paper['source']}\n")
            f.write(f"Abstract: {paper['abstract']}\n")
    
    print(f"\nAnalysis saved to: {analysis_file}")
    
    return {
        "sentence_starters": sorted_starters,
        "transition_words": sorted_transitions,
        "total_abstracts": len(all_abstract_texts)
    }

if __name__ == "__main__":
    try:
        # Fetch papers
        abstracts = fetch_business_papers()
        
        if abstracts:
            # Analyze patterns
            patterns = analyze_writing_patterns(abstracts)
            
            print(f"\n✅ SUCCESS!")
            print(f"Fetched {len(abstracts)} business journal papers")
            print(f"Analyzed writing patterns from {patterns['total_abstracts']} abstracts")
            print(f"Files created:")
            print(f"  - business_papers_abstracts.txt")
            print(f"  - business_papers_data.json") 
            print(f"  - writing_patterns_analysis.txt")
        else:
            print("❌ No papers found!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
