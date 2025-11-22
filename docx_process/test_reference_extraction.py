"""
Test script for reference extraction from a Word document.
Tests that all 26 references are extracted correctly.
"""

import sys
import os
import json
from pathlib import Path

# Add the server directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.services.section_extraction_service import SectionExtractionService
from Agents.nodes.workflows.reference_extract_workflow import SimpleReferenceExtractWorkflow

def test_reference_extraction(file_path: str):
    """Test reference extraction from a local file."""
    print("=" * 60)
    print("Testing Reference Extraction")
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
    print("Using sections: introduction, literature_review, research_model, methodology, data_analysis, discussion, conclusion, references")
    print()
    
    sections = ["introduction", "literature_review", "research_model", "methodology", "data_analysis", "discussion", "conclusion", "references"]
    
    try:
        result = service.extract_sections_from_docx(file_content, filename, sections=sections)
        
        print("=" * 60)
        print("Section Extraction Results")
        print("=" * 60)
        
        # Get references section content
        extracted_sections = result.get("extracted_sections", {})
        references_content = extracted_sections.get("references", "")
        
        # Also check what's in the "other" section - references might be there
        other_content = extracted_sections.get("other", "")
        print(f"\nOther section content length: {len(other_content)} characters")
        if other_content:
            print(f"\nOther section preview (first 500 chars):")
            print(other_content[:500])
            print(f"\nOther section preview (last 500 chars):")
            print(other_content[-500:] if len(other_content) > 500 else other_content)
        
        # Check all sections to see where references might be
        print("\n" + "=" * 60)
        print("All Extracted Sections Summary")
        print("=" * 60)
        for section_key, section_content in extracted_sections.items():
            if section_content and isinstance(section_content, str):
                print(f"\n{section_key.upper()}: {len(section_content)} characters")
                # Check if this section might contain references
                if "references" in section_key.lower() or "bibliography" in section_key.lower():
                    print(f"  Preview: {section_content[:300]}...")
                # Check if this section contains citation-like patterns
                if any(keyword in section_content.lower()[:500] for keyword in ["author", "journal", "doi", "volume", "pages", "published"]):
                    print(f"  MIGHT CONTAIN REFERENCES! Preview: {section_content[:300]}...")
        
        print(f"\nReferences section content length: {len(references_content)} characters")
        if references_content:
            print(f"\nReferences section preview (first 500 chars):")
            print(references_content[:500])
            print(f"\nReferences section preview (last 500 chars):")
            print(references_content[-500:] if len(references_content) > 500 else references_content)
        else:
            print("WARNING: References section is empty!")
        
        # Check if references section contains regression analysis (wrong content)
        if references_content:
            if "regression" in references_content.lower() or "4.3" in references_content:
                print("\n" + "!" * 60)
                print("WARNING: References section contains regression analysis content!")
                print("This is NOT the actual references list!")
                print("!" * 60)
        
        # Extract references using reference extraction workflow
        print("\n" + "=" * 60)
        print("Extracting References from References Section")
        print("=" * 60)
        
        if references_content and references_content.strip():
            print(f"Extracting references from {len(references_content)} characters of text...")
            
            # Initialize reference extraction workflow
            reference_workflow = SimpleReferenceExtractWorkflow()
            
            # Extract references
            reference_result = reference_workflow.process_text(
                references_content,
                context={"context": "Word document reference extraction"}
            )
            
            print(f"\nReference extraction result:")
            print(f"  Success: {reference_result.get('success')}")
            print(f"  References count: {len(reference_result.get('references', []))}")
            
            references = reference_result.get("references", [])
            
            if references:
                print(f"\nExtracted {len(references)} references:")
                for i, ref in enumerate(references[:5], 1):  # Show first 5
                    print(f"\n  {i}. {ref.get('full_citation', 'N/A')[:100]}...")
                    print(f"     Short form: {ref.get('short_form', 'N/A')}")
                    print(f"     Type: {ref.get('type', 'N/A')}")
                    print(f"     Order: {ref.get('order', 'N/A')}")
                
                if len(references) > 5:
                    print(f"\n  ... and {len(references) - 5} more references")
                
                print(f"\n" + "=" * 60)
                print(f"SUMMARY: Extracted {len(references)} references")
                print("=" * 60)
                
                if len(references) < 26:
                    print(f"\nWARNING: Expected 26 references but only extracted {len(references)}!")
                    print("This indicates the references section may not contain the actual references list.")
                elif len(references) == 26:
                    print("\nSUCCESS: Extracted all 26 references!")
                else:
                    print(f"\nINFO: Extracted {len(references)} references (expected 26)")
            else:
                print("\nERROR: No references extracted!")
                print(f"Reference extraction result: {reference_result}")
        else:
            print("\nERROR: References section is empty or contains no text!")
            print("Cannot extract references from empty section.")
        
        # Save results to JSON file
        output_file = "test_reference_extraction_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "section_extraction": result,
                "references_content_length": len(references_content),
                "references_content_preview": references_content[:1000] if references_content else "",
                "reference_extraction": reference_result if references_content else None
            }, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
        
        print("=" * 60)
        print("Test completed!")
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
    
    test_reference_extraction(test_file)

