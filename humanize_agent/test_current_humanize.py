#!/usr/bin/env python3
"""
Test current humanize agent with the provided paragraph
"""

import requests
import json

# Test paragraph
test_text = """The International Conference on Artificial Intelligence in Medicine (AIMED), co-sponsored by leading medical universities and the Journal of Medical Innovation, was held on September 12 and 13, 2025, in Singapore. The theme of the conference was *Artificial Intelligence as a Game-Changer in Modern Healthcare*. Advances in machine learning algorithms, natural language processing, and computer vision have driven remarkable transformations in patient monitoring, diagnosis, treatment planning, and healthcare administration. The scale and scope of these technological developments challenge traditional approaches to medical research, clinical practice, and healthcare management. Naturally, these changes require that healthcare institutions, clinicians, and policymakers develop new capabilities and ethical frameworks to ensure the effective and responsible integration of AI in medicine. With the objective of deepening our understanding of how artificial intelligence is revolutionizing healthcare delivery, this article reflects on the theme of the conference and highlights the major applications, benefits, and ethical implications of AI that are shaping the future of clinical practice and patient care."""

# Test humanize agent
payload = {
    'text': test_text,
    'session_id': 'test_session_1',
    'api_key': None
}

try:
    response = requests.post('http://localhost:5000/api/v1/humanize/', json=payload, headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        result = response.json()
        print('HUMANIZED TEXT:')
        print('=' * 50)
        print(result.get('humanized_text', ''))
        print('=' * 50)
        print(f'Success: {result.get("success", False)}')
        print(f'Execution time: {result.get("execution_time", 0):.2f}s')
        
        # Save humanized text for ZeroGPT testing
        with open('humanized_output.txt', 'w', encoding='utf-8') as f:
            f.write(result.get('humanized_text', ''))
        print('\nHumanized text saved to humanized_output.txt')
        
    else:
        print(f'Error: HTTP {response.status_code}')
        print(response.text)
except Exception as e:
    print(f'Error: {e}')
