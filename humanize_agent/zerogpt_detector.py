#!/usr/bin/env python3
"""
ZeroGPT Detection CLI Tool

A command-line interface for detecting AI-generated text using the ZeroGPT API.
This tool takes humanized text as input and returns detection results as a percentage.

Usage:
    python zerogpt_detector.py "Your text here"
    python zerogpt_detector.py --file input.txt
    python zerogpt_detector.py --interactive
"""

import argparse
import json
import sys
import requests
from typing import Dict, Any, Optional
import time


class ZeroGPTDetector:
    """ZeroGPT API client for text detection."""
    
    def __init__(self):
        self.api_url = "https://api.zerogpt.com/api/detect/detectText"
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://www.zerogpt.com",
            "Referer": "https://www.zerogpt.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0",
            "sec-ch-ua": '"Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        }
    
    def detect_text(self, text: str) -> Dict[str, Any]:
        """
        Detect if text is AI-generated using ZeroGPT API.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary containing detection results
        """
        if not text.strip():
            return {
                "error": "Empty text provided",
                "ai_probability": 0,
                "human_probability": 0,
                "status": "error"
            }
        
        payload = {
            "input_text": text
        }
        
        try:
            # Removed print statement to avoid interfering with tqdm progress bars
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_response(result)
            else:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "ai_probability": 0,
                    "human_probability": 0,
                    "status": "error",
                    "response_text": response.text
                }
                
        except requests.exceptions.Timeout:
            return {
                "error": "Request timeout - API took too long to respond",
                "ai_probability": 0,
                "human_probability": 0,
                "status": "error"
            }
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Network error: {str(e)}",
                "ai_probability": 0,
                "human_probability": 0,
                "status": "error"
            }
        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON response from API",
                "ai_probability": 0,
                "human_probability": 0,
                "status": "error",
                "response_text": response.text
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}",
                "ai_probability": 0,
                "human_probability": 0,
                "status": "error"
            }
    
    def _parse_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the ZeroGPT API response.
        
        Args:
            response_data: Raw response from API
            
        Returns:
            Parsed detection results
        """
        try:
            # Extract AI probability from response
            ai_probability = 0
            human_probability = 0
            
            # Parse the actual ZeroGPT API response format
            if "data" in response_data and isinstance(response_data["data"], dict):
                data = response_data["data"]
                
                # ZeroGPT uses 'fakePercentage' for AI probability
                if "fakePercentage" in data:
                    ai_probability = float(data["fakePercentage"])
                elif "isHuman" in data:
                    # isHuman is the human percentage, so AI = 100 - isHuman
                    human_probability = float(data["isHuman"])
                    ai_probability = 100 - human_probability
                else:
                    # Fallback: look for other probability fields
                    for key in ["ai_probability", "fake_probability", "probability", "score"]:
                        if key in data:
                            ai_probability = float(data[key])
                            break
                    
                    # Calculate human probability
                    human_probability = 100 - ai_probability
            
            elif "result" in response_data:
                result = response_data["result"]
                if isinstance(result, (int, float)):
                    ai_probability = float(result)
                    human_probability = 100 - ai_probability
                elif isinstance(result, dict) and "probability" in result:
                    ai_probability = float(result["probability"])
                    human_probability = 100 - ai_probability
            
            # If we still don't have a probability, try to extract from any numeric field
            if ai_probability == 0 and human_probability == 0:
                for key, value in response_data.items():
                    if isinstance(value, (int, float)) and 0 <= value <= 100:
                        ai_probability = float(value)
                        human_probability = 100 - ai_probability
                        break
            
            return {
                "ai_probability": round(ai_probability, 2),
                "human_probability": round(human_probability, 2),
                "status": "success",
                "raw_response": response_data,
                "detection_result": "AI-generated" if ai_probability > 50 else "Human-written",
                "feedback": response_data.get("data", {}).get("feedback", ""),
                "text_words": response_data.get("data", {}).get("textWords", 0),
                "ai_words": response_data.get("data", {}).get("aiWords", 0)
            }
            
        except (ValueError, TypeError, KeyError) as e:
            return {
                "error": f"Failed to parse response: {str(e)}",
                "ai_probability": 0,
                "human_probability": 0,
                "status": "error",
                "raw_response": response_data
            }


def format_output(result: Dict[str, Any], verbose: bool = False) -> str:
    """
    Format the detection result for output.
    
    Args:
        result: Detection result dictionary
        verbose: Whether to include verbose output
        
    Returns:
        Formatted string
    """
    if result["status"] == "error":
        return f"Error: {result['error']}"
    
    output_lines = [
        f"AI Detection Result: {result['detection_result']}",
        f"AI Probability: {result['ai_probability']}%",
        f"Human Probability: {result['human_probability']}%"
    ]
    
    # Add additional information if available
    if "feedback" in result and result["feedback"]:
        output_lines.append(f"Feedback: {result['feedback']}")
    
    if "text_words" in result and result["text_words"] > 0:
        output_lines.append(f"Total Words: {result['text_words']}")
    
    if "ai_words" in result and result["ai_words"] > 0:
        output_lines.append(f"AI Words Detected: {result['ai_words']}")
    
    if verbose and "raw_response" in result:
        output_lines.append(f"\nRaw API Response: {json.dumps(result['raw_response'], indent=2)}")
    
    return "\n".join(output_lines)


def read_text_from_file(file_path: str) -> str:
    """
    Read text from a file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        File contents as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        sys.exit(1)


def interactive_mode():
    """Run the detector in interactive mode."""
    detector = ZeroGPTDetector()
    
    print("ZeroGPT Detection Tool - Interactive Mode")
    print("Enter text to analyze (type 'quit' to exit):")
    print("-" * 50)
    
    while True:
        try:
            text = input("\nText: ").strip()
            
            if text.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not text:
                print("Please enter some text to analyze.")
                continue
            
            result = detector.detect_text(text)
            print(format_output(result))
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="ZeroGPT Detection CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python zerogpt_detector.py "This is sample text to analyze"
  python zerogpt_detector.py --file sample.txt
  python zerogpt_detector.py --interactive
  python zerogpt_detector.py "Text here" --verbose
        """
    )
    
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to analyze for AI detection"
    )
    
    parser.add_argument(
        "--file", "-f",
        help="Read text from file"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output including raw API response"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Save result to file (JSON format)"
    )
    
    args = parser.parse_args()
    
    # Handle interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Determine text source
    text = None
    if args.file:
        text = read_text_from_file(args.file)
    elif args.text:
        text = args.text
    else:
        print("Error: Please provide text to analyze, specify a file, or use interactive mode.")
        parser.print_help()
        sys.exit(1)
    
    # Perform detection
    detector = ZeroGPTDetector()
    result = detector.detect_text(text)
    
    # Format and display output
    output = format_output(result, args.verbose)
    print(output)
    
    # Save to file if requested
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\nResult saved to: {args.output}")
        except Exception as e:
            print(f"Error saving to file: {str(e)}")
    
    # Exit with appropriate code
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
