"""
Test script to verify parallel processing performance and timeout functionality.
"""

import sys
import os
import time
import json
from pathlib import Path

# Add the server directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.services.section_extraction_service import SectionExtractionService
from server.services.section_mapper import SectionMapper
from server.services.document_extractor import DocumentExtractor

def test_parallel_processing(file_path: str):
    """Test parallel processing performance."""
    print("=" * 80)
    print("Testing Parallel Processing Performance")
    print("=" * 80)
    
    # Read the file
    print(f"\nReading file: {file_path}")
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    filename = os.path.basename(file_path)
    file_size = len(file_content)
    print(f"File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
    print()
    
    # Test 1: Document extraction
    print("=" * 80)
    print("TEST 1: Document Extraction")
    print("=" * 80)
    start_time = time.time()
    
    extractor = DocumentExtractor()
    chunks = extractor.extract_chunks_from_docx(file_content)
    
    extraction_time = time.time() - start_time
    print(f"Extraction time: {extraction_time:.2f} seconds")
    
    if chunks:
        chunk = chunks[0]
        total_segments = len(chunk.id_to_content) if chunk.id_to_content else 0
        print(f"Total segments extracted: {total_segments}")
        print(f"Has tables: {chunk.has_table}")
        print(f"Has images: {chunk.has_image}")
    else:
        print("ERROR: No chunks extracted!")
        return
    
    print()
    
    # Test 2: Parallel chunking
    print("=" * 80)
    print("TEST 2: Parallel Chunking (6 chunks)")
    print("=" * 80)
    
    mapper = SectionMapper()
    sections = ["introduction", "methodology", "data_analysis", "discussion", "conclusion", "references"]
    
    # Test parallel processing
    print("Testing parallel processing with 6 chunks...")
    start_time = time.time()
    
    try:
        mapping = mapper.map_chunks(chunks, sections=sections, parallel=True, num_parallel_chunks=6)
        parallel_time = time.time() - start_time
        
        print(f"Parallel processing time: {parallel_time:.2f} seconds")
        print(f"Total mappings: {len(mapping.mappings)}")
        
        # Show mapping summary
        section_counts = {}
        for m in mapping.mappings:
            section = m.section.lower()
            section_counts[section] = section_counts.get(section, 0) + 1
        
        print("\nMappings by section:")
        for section, count in sorted(section_counts.items()):
            print(f"  {section}: {count} mapping(s)")
        
    except Exception as e:
        print(f"ERROR in parallel processing: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    
    # Test 3: Full section extraction with timing
    print("=" * 80)
    print("TEST 3: Full Section Extraction (with parallel processing)")
    print("=" * 80)
    
    service = SectionExtractionService()
    
    print("Starting section extraction...")
    start_time = time.time()
    
    try:
        result = service.extract_sections_from_docx(
            file_content, 
            filename, 
            sections=["introduction", "methodology", "data_analysis", "discussion", "conclusion"]
        )
        
        total_time = time.time() - start_time
        
        print(f"\nTotal processing time: {total_time:.2f} seconds")
        print(f"Target: < 30 seconds")
        print(f"Status: {'PASSED' if total_time < 30 else 'FAILED'} (exceeded 30s target)")
        print(f"Timeout limit: 60 seconds")
        print(f"Status: {'Within limit' if total_time < 60 else 'TIMEOUT'} (exceeded 60s limit)")
        
        # Show results summary
        sections = result.get("sections", [])
        print(f"\nSections extracted: {len(sections)}")
        for section in sections:
            title = section.get("title", "Unknown")
            is_complete = section.get("is_complete", False)
            content = section.get("content", {})
            content_nodes = len(content.get("content", [])) if isinstance(content, dict) else 0
            print(f"  - {title}: {content_nodes} nodes, complete={is_complete}")
        
        # First page metadata
        first_page_metadata = result.get("first_page_metadata", {})
        if first_page_metadata:
            print(f"\nFirst page metadata:")
            if first_page_metadata.get("abstract"):
                print(f"  Abstract: {len(first_page_metadata['abstract'])} chars")
            if first_page_metadata.get("authors"):
                print(f"  Authors: {len(first_page_metadata['authors'])} found")
            if first_page_metadata.get("keywords"):
                print(f"  Keywords: {first_page_metadata['keywords']}")
        
        # Performance breakdown
        print("\n" + "=" * 80)
        print("Performance Breakdown")
        print("=" * 80)
        print(f"Document extraction: {extraction_time:.2f}s")
        print(f"AI classification (parallel): {parallel_time:.2f}s")
        print(f"Total processing: {total_time:.2f}s")
        print(f"\nParallel speedup: {parallel_time:.2f}s (processing 6 chunks simultaneously)")
        
        # Save results (summary)
        output_file = "test_parallel_performance_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "performance": {
                    "extraction_time": extraction_time,
                    "parallel_time": parallel_time,
                    "total_time": total_time,
                    "within_30s_target": total_time < 30,
                    "within_60s_limit": total_time < 60
                },
                "results": {
                    "sections_count": len(sections),
                    "mappings_count": len(mapping.mappings),
                    "total_segments": total_segments
                }
            }, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
        
        # Save FULL result with all sections and content
        full_output_file = "test_parallel_performance_full_output.json"
        with open(full_output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"Full output saved to: {full_output_file}")
        
    except Exception as e:
        print(f"ERROR in section extraction: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80)

if __name__ == "__main__":
    # Test file path - update this to your test file
    test_file = r"C:\Users\USER\Downloads\f7a969ee-6e82-4626-8669-b35e675fb36a-Manuscriptwithauthor (1).docx"
    
    # Alternative test file
    if not os.path.exists(test_file):
        test_file = r"C:\Users\USER\Downloads\Specimen-Copy-of-Article-5-3.docx"
    
    if not os.path.exists(test_file):
        print(f"Error: Test file not found")
        print("Please update the test_file path in the script")
        print(f"Looking for: {test_file}")
        sys.exit(1)
    
    test_parallel_processing(test_file)

