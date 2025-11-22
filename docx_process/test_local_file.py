"""
Test script for processing a local Word document file.
Uploads the file directly to the docx processing service and saves the output.
"""

import sys
import os
import json
import requests
from pathlib import Path
from datetime import datetime

def test_local_file(file_path: str, output_file: str = None, base_url: str = "http://localhost:5007"):
    """
    Test the docx processing service with a local file.
    
    Args:
        file_path: Path to the local .docx file
        output_file: Path to save the JSON output (default: test_output_<timestamp>.json)
        base_url: Base URL of the docx processing service
    """
    print("=" * 60)
    print("Testing DocX Processing Service with Local File")
    print("=" * 60)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    # Get file info
    file_size = os.path.getsize(file_path)
    filename = os.path.basename(file_path)
    print(f"\nFile: {filename}")
    print(f"Size: {file_size:,} bytes")
    print(f"Path: {file_path}")
    
    # Check file extension
    if not filename.lower().endswith('.docx'):
        print(f"Warning: File does not have .docx extension: {filename}")
    
    # Prepare output filename
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"test_output_{timestamp}.json"
    
    print(f"\nOutput will be saved to: {output_file}")
    print()
    
    # Prepare the request
    url = f"{base_url}/api/v1/docx/"
    
    print(f"Uploading file to: {url}")
    print("Processing...")
    
    try:
        # Define sections to extract
        # Note: abstract is automatically extracted to first_page_metadata
        # Note: references is always extracted automatically
        sections_to_extract = [
            'introduction',
            'literature_review',
            'methodology',
            'data_analysis',
            'discussion',
            'conclusion'
        ]
        
        print(f"Sections to extract: {', '.join(sections_to_extract)}")
        print("Note: abstract will be extracted to first_page_metadata")
        print("Note: references will always be extracted automatically")
        print()
        
        # Open and upload the file
        with open(file_path, 'rb') as f:
            files = {
                'file': (filename, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Pass sections as form data (JSON string)
            data = {
                'sections': json.dumps(sections_to_extract)
            }
            
            response = requests.post(url, files=files, data=data, timeout=300)  # 5 minute timeout
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Save the full response to JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\nSuccess! Results saved to: {output_file}")
            print("\n" + "=" * 60)
            print("Response Summary")
            print("=" * 60)
            
            # Print summary
            if result.get('status') == 'success':
                data = result.get('data', {})
                
                # Sections summary
                sections = data.get('sections', [])
                if sections:
                    print(f"\nSections extracted: {len(sections)}")
                    for section in sections:
                        title = section.get('title', 'Unknown')
                        is_complete = section.get('is_complete', False)
                        content_type = section.get('content_type', 'unknown')
                        content = section.get('content', {})
                        content_length = len(str(content))
                        
                        print(f"  - {title} ({content_type})")
                        print(f"    Complete: {is_complete}")
                        print(f"    Content size: {content_length:,} characters")
                
                # References summary
                references = data.get('references', [])
                if references:
                    print(f"\nReferences extracted: {len(references)}")
                    for i, ref in enumerate(references[:3], 1):
                        citation = ref.get('full_citation', 'N/A')
                        print(f"  {i}. {citation[:100]}...")
                    if len(references) > 3:
                        print(f"  ... and {len(references) - 3} more references")
                
                # First page metadata
                first_page_metadata = data.get('first_page_metadata', {})
                if first_page_metadata:
                    print(f"\nFirst Page Metadata:")
                    if first_page_metadata.get('abstract'):
                        abstract_len = len(first_page_metadata['abstract'])
                        print(f"  Abstract: {abstract_len} characters")
                    if first_page_metadata.get('authors'):
                        print(f"  Authors: {len(first_page_metadata['authors'])} found")
                    if first_page_metadata.get('keywords'):
                        print(f"  Keywords: {first_page_metadata['keywords']}")
                
                # Filename
                print(f"\nProcessed filename: {data.get('filename', 'N/A')}")
                
            else:
                print(f"\nStatus: {result.get('status', 'unknown')}")
                if result.get('error'):
                    print(f"Error: {result.get('error')}")
            
            print("\n" + "=" * 60)
            print("Test completed successfully!")
            print("=" * 60)
            return True
            
        else:
            print(f"\nError: Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error response: {response.text}")
            
            # Save error response
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'status': 'error',
                    'status_code': response.status_code,
                    'error': response.text,
                    'headers': dict(response.headers)
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\nError response saved to: {output_file}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\nError: Could not connect to {base_url}")
        print("Make sure the docx processing service is running on port 5007")
        return False
    except requests.exceptions.Timeout:
        print(f"\nError: Request timed out (exceeded 5 minutes)")
        print("The document might be very large or the service is slow")
        return False
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test file path
    test_file = r"C:\Users\USER\Downloads\Specimen-Copy-of-Article-5-3.docx"
    
    # Check if file exists
    if not os.path.exists(test_file):
        print(f"Error: File not found: {test_file}")
        print("Please check the file path.")
        sys.exit(1)
    
    # Run the test
    success = test_local_file(test_file)
    
    if not success:
        sys.exit(1)

