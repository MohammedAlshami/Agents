"""
Nodes package for modular AI node architecture.
Each node defines clear inputs and outputs for easy composition.
"""

from .base_node import BaseNode, NodeResult, NodeStatus


__all__ = [
    'BaseNode',
    'NodeResult', 
    'NodeStatus',
]