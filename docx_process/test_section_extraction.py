"""
Test script for section extraction from a Word document.
"""

import sys
import os
import json
from pathlib import Path

# Add the server directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.services.section_extraction_service import SectionExtractionService

def test_section_extraction(file_path: str, sections: list = None):
    """Test section extraction from a local file."""
    print("=" * 60)
    print("Testing Section Extraction")
    print("=" * 60)
    
    # Read the file
    print(f"Reading file: {file_path}")
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    filename = os.path.basename(file_path)
    print(f"File size: {len(file_content)} bytes")
    print(f"Filename: {filename}")
    print()
    
    # Initialize section extraction service
    print("Initializing section extraction service...")
    try:
        service = SectionExtractionService()
        print("Service initialized successfully")
        print()
    except Exception as e:
        print(f"Error initializing service: {e}")
        return
    
    # Extract sections
    print("Extracting sections from document...")
    if sections:
        print(f"Using custom sections: {sections}")
    else:
        print("Using default sections (will include references)")
    print()
    
    try:
        result = service.extract_sections_from_docx(file_content, filename, sections=sections)
        
        print("=" * 60)
        print("Section Extraction Results")
        print("=" * 60)
        
        # Print sections summary
        sections = result.get("sections", [])
        print(f"\nTotal sections extracted: {len(sections)}")
        print("\nSections:")
        for section in sections:
            content = section.get("content", {})
            content_type = type(content).__name__
            content_length = len(str(content))
            has_content = bool(section.get("content", {}).get("content", []))
            
            print(f"  - {section.get('title', 'Unknown')} (ID: {section.get('id', 'unknown')})")
            print(f"    Order: {section.get('order', 0)}")
            print(f"    Content type: {content_type}")
            print(f"    Has content: {has_content}")
            print(f"    Content length: {content_length} characters")
            print(f"    Is complete: {section.get('is_complete', False)}")
            print()
        
        # Print extracted sections (raw)
        print("=" * 60)
        print("Extracted Sections (Raw Text)")
        print("=" * 60)
        extracted_sections = result.get("extracted_sections", {})
        for section_key, section_content in extracted_sections.items():
            if section_content:
                print(f"\n{section_key.upper()}:")
                if isinstance(section_content, str):
                    print(f"  Length: {len(section_content)} characters")
                    print(f"  Preview: {section_content[:200]}...")
                else:
                    print(f"  Type: {type(section_content).__name__}")
        
        # Print first page metadata
        first_page_metadata = result.get("first_page_metadata", {})
        if first_page_metadata:
            print("\n" + "=" * 60)
            print("First Page Metadata")
            print("=" * 60)
            if first_page_metadata.get("abstract"):
                print(f"\nAbstract: {len(first_page_metadata['abstract'])} characters")
                print(f"  Preview: {first_page_metadata['abstract'][:200]}...")
            if first_page_metadata.get("authors"):
                print(f"\nAuthors: {len(first_page_metadata['authors'])} found")
                for i, author in enumerate(first_page_metadata['authors'][:3], 1):
                    if isinstance(author, dict):
                        print(f"  {i}. Name: {author.get('name', 'N/A')}")
                        print(f"      Department: {author.get('department', 'N/A')}")
                        print(f"      University: {author.get('university', 'N/A')}")
                        print(f"      Country: {author.get('country', 'N/A')}")
                        print(f"      Email: {author.get('email', 'N/A')}")
                    else:
                        print(f"  {i}. {str(author)[:100]}...")
            if first_page_metadata.get("keywords"):
                print(f"\nKeywords: {first_page_metadata['keywords']}")
        
        # Save results to JSON file
        output_file = "test_section_extraction_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
        
        print("=" * 60)
        print("Test completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error extracting sections: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test file path
    test_file = r"C:\Users\USER\Downloads\f7a969ee-6e82-4626-8669-b35e675fb36a-Manuscriptwithauthor (1).docx"
    
    if not os.path.exists(test_file):
        print(f"Error: File not found: {test_file}")
        print("Please check the file path.")
        sys.exit(1)
    
    # Test with custom sections
    print("TEST 1: Testing with custom sections")
    print("-" * 60)
    custom_sections = ["introduction", "methodology", "data_analysis", "conclusion"]
    test_section_extraction(test_file, sections=custom_sections)
    
    print("\n\n")
    
    # Test with default sections (no sections provided)
    print("TEST 2: Testing with default sections (no sections provided)")
    print("-" * 60)
    test_section_extraction(test_file, sections=None)

