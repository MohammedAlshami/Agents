"""
Test script to verify humanize agent returns only one paragraph.
"""

import requests
import json

def test_humanize_single_paragraph():
    """Test that humanize endpoint returns only one paragraph."""
    
    # Test with text that might produce multiple paragraphs
    test_text = """
    Artificial intelligence has become increasingly important in modern business operations. 
    Many companies are adopting AI technologies to improve efficiency and reduce costs. 
    Machine learning algorithms can analyze large datasets to identify patterns and trends.
    """
    
    url = "http://localhost:5004/api/v1/humanize"
    
    payload = {
        "text": test_text.strip(),
        "session_id": "test-single-paragraph",
        "context": "test"
    }
    
    print("Testing humanize endpoint...")
    print(f"URL: {url}")
    print(f"Input text: {test_text.strip()}")
    print("\nSending request...")
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "="*60)
            print("RESPONSE:")
            print("="*60)
            print(f"Success: {result.get('success')}")
            print(f"\nOriginal text length: {len(result.get('original_text', ''))}")
            print(f"Humanized text length: {len(result.get('humanized_text', ''))}")
            
            humanized_text = result.get('humanized_text', '')
            
            # Count newlines
            newline_count = humanized_text.count('\n')
            double_newline_count = humanized_text.count('\n\n')
            
            print(f"\nNewline count: {newline_count}")
            print(f"Double newline count: {double_newline_count}")
            
            print("\n" + "="*60)
            print("HUMANIZED TEXT:")
            print("="*60)
            print(humanized_text)
            print("="*60)
            
            # Check if it's a single paragraph
            if newline_count == 0:
                print("\n[SUCCESS] Output is a single paragraph (no newlines)")
            elif double_newline_count == 0 and newline_count <= 2:
                print(f"\n[WARNING] Output has {newline_count} newline(s) but no paragraph breaks")
            else:
                print(f"\n[FAIL] Output has multiple paragraphs (found {double_newline_count} paragraph breaks)")
            
            # Verify no multiple consecutive newlines
            if '\n\n' in humanized_text or '\r\n\r\n' in humanized_text:
                print("[FAIL] Multiple consecutive newlines found (paragraph breaks)")
            else:
                print("[SUCCESS] No paragraph breaks found")
            
            return result.get('success', False) and newline_count == 0
            
        else:
            print(f"\n[ERROR] HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to server at http://localhost:5004")
        print("Make sure the humanize server is running on port 5004")
        return False
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("HUMANIZE AGENT - SINGLE PARAGRAPH TEST")
    print("="*60)
    print()
    
    success = test_humanize_single_paragraph()
    
    print("\n" + "="*60)
    if success:
        print("[PASS] TEST PASSED: Single paragraph output verified")
    else:
        print("[FAIL] TEST FAILED: Multiple paragraphs or errors detected")
    print("="*60)

