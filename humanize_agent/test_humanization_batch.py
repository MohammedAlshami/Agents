#!/usr/bin/env python3
"""
Script to humanize test paragraphs and test with ZeroGPT
"""

import requests
import json
import sys
import os

# Add current directory to path for zerogpt_detector
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from zerogpt_detector import ZeroGPTDetector

def humanize_text(text):
    """Humanize text using the server"""
    try:
        response = requests.post(
            "http://localhost:5000/api/v1/humanize/",
            json={"text": text},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('humanized_text', '')
        else:
            print(f"Error: HTTP {response.status_code}")
            return ""
    except Exception as e:
        print(f"Error humanizing text: {e}")
        return ""

def test_with_zerogpt(text, description):
    """Test text with ZeroGPT detector"""
    detector = ZeroGPTDetector()
    result = detector.detect_text(text)
    
    print(f"\n=== {description} ===")
    print(f"AI Probability: {result.get('ai_probability', 0)}%")
    print(f"Human Probability: {result.get('human_probability', 0)}%")
    print(f"Detection Result: {result.get('detection_result', 'Unknown')}")
    print(f"Text Length: {len(text)} characters")
    print(f"Word Count: {result.get('text_words', 0)}")
    print(f"AI Words Detected: {result.get('ai_words', 0)}")
    
    return result.get('ai_probability', 0)

def main():
    # Test paragraphs
    paragraphs = [
        ("test_paragraph_1.txt", "Paragraph 1 - Technical Implementation"),
        ("test_paragraph_2.txt", "Paragraph 2 - Research Analysis"),
        ("test_paragraph_3.txt", "Paragraph 3 - Technology Infrastructure"),
        ("test_paragraph_4.txt", "Paragraph 4 - Empirical Evidence"),
        ("test_paragraph_5.txt", "Paragraph 5 - AI Strategy")
    ]
    
    print("🚀 Testing Humanize Agent with ZeroGPT Detection")
    print("=" * 60)
    
    results = []
    
    for filename, description in paragraphs:
        # Read original text
        with open(filename, 'r', encoding='utf-8') as f:
            original_text = f.read().strip()
        
        # Test original
        print(f"\n📄 {description}")
        print("-" * 40)
        original_ai_prob = test_with_zerogpt(original_text, "ORIGINAL")
        
        # Humanize text
        print("\n🔄 Humanizing text...")
        humanized_text = humanize_text(original_text)
        
        if humanized_text:
            # Test humanized
            humanized_ai_prob = test_with_zerogpt(humanized_text, "HUMANIZED")
            
            # Save humanized text
            humanized_filename = filename.replace('.txt', '_humanized.txt')
            with open(humanized_filename, 'w', encoding='utf-8') as f:
                f.write(humanized_text)
            
            results.append({
                'description': description,
                'original_ai_prob': original_ai_prob,
                'humanized_ai_prob': humanized_ai_prob,
                'improvement': original_ai_prob - humanized_ai_prob
            })
        else:
            print("❌ Failed to humanize text")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY RESULTS")
    print("=" * 60)
    
    for result in results:
        print(f"\n{result['description']}:")
        print(f"  Original AI Detection: {result['original_ai_prob']}%")
        print(f"  Humanized AI Detection: {result['humanized_ai_prob']}%")
        print(f"  Improvement: -{result['improvement']:.1f}%")
    
    # Overall stats
    avg_original = sum(r['original_ai_prob'] for r in results) / len(results)
    avg_humanized = sum(r['humanized_ai_prob'] for r in results) / len(results)
    avg_improvement = avg_original - avg_humanized
    
    print(f"\n🎯 OVERALL STATISTICS:")
    print(f"  Average Original AI Detection: {avg_original:.1f}%")
    print(f"  Average Humanized AI Detection: {avg_humanized:.1f}%")
    print(f"  Average Improvement: -{avg_improvement:.1f}%")
    
    # Count how many achieved <30%
    under_30 = sum(1 for r in results if r['humanized_ai_prob'] < 30)
    print(f"  Paragraphs under 30% AI detection: {under_30}/{len(results)}")

if __name__ == "__main__":
    main()

