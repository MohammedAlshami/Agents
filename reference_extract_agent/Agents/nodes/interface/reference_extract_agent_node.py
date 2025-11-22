"""
Reference Extract Agent Node
Extracts and structures references from text using AI.
"""

from typing import Dict, Any, List, Optional
from .base_node import BaseNode, NodeResult, NodeStatus
from ..nodes.ai.reference_extract_agent import ReferenceExtractAgent


class ReferenceExtractAgentNode(BaseNode):
    """
    Node for extracting and structuring references from text.
    
    Input: Text content to extract references from
    Output: Structured references with metadata
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Reference Extract Agent Node.
        
        Args:
            api_key: OpenAI API key
        """
        super().__init__(
            node_id="reference_extract_agent",
            name="Reference Extract Agent",
            description="Extracts and structures references from text using AI"
        )
        
        # Initialize the underlying ReferenceExtractAgent
        self.reference_extract_agent = ReferenceExtractAgent(
            api_key=api_key
        )
    
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Define the input schema for Reference Extract Agent Node.
        
        Returns:
            Dict describing the expected input structure
        """
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text content to extract references from"
                },
                "context": {
                    "type": "string",
                    "description": "Optional context for the text",
                    "default": ""
                }
            },
            "required": ["text"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Define the output schema for Reference Extract Agent Node.
        
        Returns:
            Dict describing the output structure
        """
        return {
            "type": "object",
            "properties": {
                "references": {
                    "type": "array",
                    "description": "Array of extracted references",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "Unique reference ID"
                            },
                            "full_citation": {
                                "type": "string",
                                "description": "Complete reference in proper format"
                            },
                            "short_form": {
                                "type": "string",
                                "description": "Author, Year format citation"
                            },
                            "type": {
                                "type": "string",
                                "description": "Reference type (academic, url, book, journal, other)",
                                "enum": ["academic", "url", "book", "journal", "other"]
                            },
                            "order": {
                                "type": "integer",
                                "description": "Order of appearance in text"
                            },
                            "original_text": {
                                "type": "string",
                                "description": "Original text that was identified as reference"
                            }
                        }
                    }
                },
                "extraction_metadata": {
                    "type": "object",
                    "description": "Metadata about the extraction process",
                    "properties": {
                        "total_references": {
                            "type": "integer",
                            "description": "Total number of references found"
                        },
                        "extraction_confidence": {
                            "type": "number",
                            "description": "Confidence score for the extraction"
                        },
                        "detected_formats": {
                            "type": "array",
                            "description": "Citation formats detected",
                            "items": {"type": "string"}
                        },
                        "processing_time": {
                            "type": "string",
                            "description": "Timestamp of processing"
                        },
                        "agent_version": {
                            "type": "string",
                            "description": "Version of the agent"
                        }
                    }
                },
                "success": {
                    "type": "boolean",
                    "description": "Whether the extraction was successful"
                },
                "error": {
                    "type": "string",
                    "description": "Error message if extraction failed",
                    "nullable": True
                }
            },
            "required": ["references", "extraction_metadata", "success"]
        }
    
    def execute(self, inputs: Dict[str, Any]) -> NodeResult:
        """
        Execute the Reference Extract Agent Node.
        
        Args:
            inputs: Input data matching the input schema
            
        Returns:
            NodeResult with status, output, and any errors
        """
        try:
            # Validate inputs
            if not self.validate_inputs(inputs):
                return NodeResult(
                    status=NodeStatus.FAILED,
                    output={},
                    error="Invalid input schema"
                )
            
            # Extract inputs
            text = inputs["text"]
            context = inputs.get("context", "")
            
            # Update status
            self.status = NodeStatus.RUNNING
            
            # Process the text
            result = self.reference_extract_agent.extract_references(text)
            
            # Update status
            self.status = NodeStatus.COMPLETED
            
            return NodeResult(
                status=NodeStatus.COMPLETED,
                output=result,
                metadata={
                    "node_id": self.node_id,
                    "text_length": len(text),
                    "references_found": len(result.get("references", [])),
                    "success": result.get("extraction_metadata", {}).get("total_references", 0) > 0
                }
            )
            
        except Exception as e:
            self.status = NodeStatus.FAILED
            return NodeResult(
                status=NodeStatus.FAILED,
                output={},
                error=f"Reference Extract Agent execution failed: {str(e)}"
            )
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the system status of the Reference Extract Agent.
        
        Returns:
            Dict with system status information
        """
        return self.reference_extract_agent.get_system_status()
    
    def get_supported_features(self) -> List[str]:
        """
        Get the list of supported features.
        
        Returns:
            List of supported feature names
        """
        return [
            "reference_extraction",
            "citation_format_detection",
            "academic_reference_parsing",
            "url_extraction",
            "book_reference_extraction",
            "journal_reference_extraction"
        ]
    
    def get_supported_formats(self) -> List[str]:
        """
        Get the list of supported citation formats.
        
        Returns:
            List of supported citation formats
        """
        return ["APA", "MLA", "Chicago", "URL", "Book", "Journal", "Other"]
    
    def get_example_texts(self) -> List[str]:
        """
        Get example texts for testing reference extraction.
        
        Returns:
            List of example texts with references
        """
        return [
            "According to Smith (2024), the impact of AI on healthcare is significant. Recent studies (Johnson et al., 2023) have shown promising results. For more information, visit https://example.com/research.",
            "The research methodology follows APA guidelines (American Psychological Association, 2020). Additional references include Brown, A. (2023). Machine Learning Applications. New York: Academic Press.",
            "Multiple sources support this finding: Wilson, B. (2022). 'Digital Transformation in Healthcare.' Journal of Medical Technology, 15(3), 45-67. DOI: 10.1234/jmt.2022.001"
        ]
