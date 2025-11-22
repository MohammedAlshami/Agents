"""
AI Detection Service using ZeroGPT API for text analysis.
"""

import requests
import json
import logging
from typing import Dict, Any, List, Optional
import time

logger = logging.getLogger(__name__)


class AIDetectionService:
    """Service for detecting AI-generated text using ZeroGPT API."""
    
    def __init__(self):
        """Initialize AI detection service."""
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
        logger.info("AI Detection Service initialized")
    
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
            logger.debug(f"Analyzing text ({len(text)} characters)...")
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
            
            # Ensure we only show AI percentage, human is just 100 - ai
            ai_percentage = round(ai_probability, 2)
            human_percentage = round(100 - ai_probability, 2)
            
            return {
                "ai_probability": ai_percentage,
                "human_probability": human_percentage,
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
    
    def analyze_content_items(self, content_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple content items for AI detection.
        
        Args:
            content_items: List of content items to analyze
            
        Returns:
            List of content items with AI detection results added
        """
        analyzed_items = []
        
        for i, item in enumerate(content_items):
            try:
                # Skip images
                if item.get("type") == "image":
                    item["ai_detection"] = {
                        "status": "skipped",
                        "reason": "Image content - AI detection not applicable"
                    }
                    analyzed_items.append(item)
                    continue
                
                # Extract text content for analysis
                text_content = self._extract_text_from_item(item)
                
                if not text_content.strip():
                    item["ai_detection"] = {
                        "status": "skipped",
                        "reason": "No text content to analyze"
                    }
                    analyzed_items.append(item)
                    continue
                
                # Perform AI detection
                logger.info(f"Analyzing content item {i+1}/{len(content_items)}: {item.get('type', 'unknown')}")
                detection_result = self.detect_text(text_content)
                
                # Add detection result to item
                item["ai_detection"] = detection_result
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.5)
                
                analyzed_items.append(item)
                
            except Exception as e:
                logger.error(f"Error analyzing content item {i}: {str(e)}")
                item["ai_detection"] = {
                    "status": "error",
                    "error": str(e)
                }
                analyzed_items.append(item)
        
        return analyzed_items
    
    def _extract_text_from_item(self, item: Dict[str, Any]) -> str:
        """Extract text content from a content item."""
        text_content = ""
        
        try:
            item_type = item.get("type", "")
            
            if item_type == "paragraph":
                text_content = item.get("text", "")
            elif item_type == "heading":
                text_content = item.get("text", "")
            elif item_type == "table":
                # Extract text from table cells
                table_data = item.get("data", {})
                if "cells" in table_data:
                    for row in table_data["cells"]:
                        for cell in row:
                            if cell.get("text"):
                                text_content += cell["text"] + " "
                        text_content += "\n"
            elif item_type == "bulletList":
                # Extract text from list items
                if "content" in item:
                    for list_item in item["content"]:
                        if list_item.get("text"):
                            text_content += list_item["text"] + "\n"
            else:
                # Generic text extraction
                text_content = item.get("text", "")
        
        except Exception as e:
            logger.warning(f"Error extracting text from item: {str(e)}")
        
        return text_content.strip()
