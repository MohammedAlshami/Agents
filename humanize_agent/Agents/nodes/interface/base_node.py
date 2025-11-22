"""
Base Node class that all nodes inherit from.
Defines the common interface and structure for all nodes.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class NodeStatus(str, Enum):
    """Node execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class NodeResult:
    """Standard result structure for all nodes."""
    status: NodeStatus
    output: Dict[str, Any]
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseNode(ABC):
    """
    Base class for all nodes in the system.
    Each node must define its inputs, outputs, and execute method.
    """
    
    def __init__(self, node_id: str, name: str, description: str = ""):
        """
        Initialize the base node.
        
        Args:
            node_id: Unique identifier for this node
            name: Human-readable name
            description: Description of what this node does
        """
        self.node_id = node_id
        self.name = name
        self.description = description
        self.status = NodeStatus.PENDING
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Define the input schema for this node.
        
        Returns:
            Dict describing the expected input structure
        """
        pass
    
    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Define the output schema for this node.
        
        Returns:
            Dict describing the output structure
        """
        pass
    
    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> NodeResult:
        """
        Execute the node with given inputs.
        
        Args:
            inputs: Input data matching the input schema
            
        Returns:
            NodeResult with status, output, and any errors
        """
        pass
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """
        Validate that inputs match the expected schema.
        
        Args:
            inputs: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation - can be extended by subclasses
        required_fields = self.get_input_schema().get("required", [])
        for field in required_fields:
            if field not in inputs:
                return False
        return True
    
    def get_node_info(self) -> Dict[str, Any]:
        """
        Get information about this node.
        
        Returns:
            Dict with node metadata
        """
        return {
            "node_id": self.node_id,
            "name": self.name,
            "description": self.description,
            "input_schema": self.get_input_schema(),
            "output_schema": self.get_output_schema(),
            "status": self.status
        }