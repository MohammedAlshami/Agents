"""
Test script to check what's at the end of the document.
"""

import sys
import os
from pathlib import Path

# Add the server directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.services.document_extractor import DocumentExtractor

def test_document_end(file_path: str):
    """Test what's at the end of the document."""
    print("=" * 60)
    print("Checking Document End Content")
    print("=" * 60)
    
    # Read the file
    print(f"Reading file: {file_path}")
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    filename = os.path.basename(file_path)
    print(f"File size: {len(file_content)} bytes")
    print()
    
    # Initialize document extractor
    extractor = DocumentExtractor()
    
    # Extract chunks
    print("Extracting chunks from document...")
    chunks = extractor.extract_chunks_from_docx(file_content)
    
    if not chunks:
        print("No chunks extracted!")
        return
    
    chunk = chunks[0]
    print(f"Total segments: {len(chunk.id_to_content)}")
    print()
    
    # Show last 50 segments
    print("=" * 60)
    print("Last 50 Segments of Document")
    print("=" * 60)
    
    all_ids = sorted(chunk.id_to_content.keys(), key=lambda x: int(x[2:]) if x.startswith('id') else 0)
    last_50_ids = all_ids[-50:] if len(all_ids) > 50 else all_ids
    
    for i, id_key in enumerate(last_50_ids, 1):
        content = chunk.id_to_content[id_key]
        print(f"\n[{id_key}] ({len(content)} chars)")
        print(content[:200] + "..." if len(content) > 200 else content)
        
        # Check if this looks like references
        if any(keyword in content.lower() for keyword in ["references", "bibliography", "works cited"]):
            print("  *** MIGHT BE REFERENCES HEADING ***")
        if any(keyword in content.lower() for keyword in ["author", "journal", "doi", "volume", "pages", "published", "et al"]):
            print("  *** MIGHT BE A REFERENCE/CITATION ***")
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total segments: {len(all_ids)}")
    print(f"Last segment ID: {all_ids[-1] if all_ids else 'N/A'}")
    print(f"Last segment content preview: {chunk.id_to_content.get(all_ids[-1], '')[:200] if all_ids else 'N/A'}...")

if __name__ == "__main__":
    # Test file path
    test_file = r"C:\Users\USER\Downloads\f7a969ee-6e82-4626-8669-b35e675fb36a-Manuscriptwithauthor (1).docx"
    
    if not os.path.exists(test_file):
        print(f"Error: File not found: {test_file}")
        print("Please check the file path.")
        sys.exit(1)
    
    test_document_end(test_file)

