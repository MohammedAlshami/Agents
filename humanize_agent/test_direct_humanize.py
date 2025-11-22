#!/usr/bin/env python3
"""
Direct test of humanize agent without server
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Agents.nodes.nodes.ai.humanize_agent.humanize_agent import HumanizeAgent

# Test paragraph
test_text = """The International Conference on Artificial Intelligence in Medicine (AIMED), co-sponsored by leading medical universities and the Journal of Medical Innovation, was held on September 12 and 13, 2025, in Singapore. The theme of the conference was *Artificial Intelligence as a Game-Changer in Modern Healthcare*. Advances in machine learning algorithms, natural language processing, and computer vision have driven remarkable transformations in patient monitoring, diagnosis, treatment planning, and healthcare administration. The scale and scope of these technological developments challenge traditional approaches to medical research, clinical practice, and healthcare management. Naturally, these changes require that healthcare institutions, clinicians, and policymakers develop new capabilities and ethical frameworks to ensure the effective and responsible integration of AI in medicine. With the objective of deepening our understanding of how artificial intelligence is revolutionizing healthcare delivery, this article reflects on the theme of the conference and highlights the major applications, benefits, and ethical implications of AI that are shaping the future of clinical practice and patient care."""

def test_humanize_agent():
    try:
        # Initialize the humanize agent
        agent = HumanizeAgent()
        
        # Humanize the text
        result = agent.humanize_text(test_text)
        
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
        
        return result
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_humanize_agent()
