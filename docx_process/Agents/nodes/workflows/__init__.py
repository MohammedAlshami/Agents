"""
Workflows Package
Contains workflow orchestration components for reference extract agent.
"""

# Import the available workflows
try:
    from .reference_extract_workflow import SimpleReferenceExtractWorkflow
    __all__ = [
        'SimpleReferenceExtractWorkflow'
    ]
except ImportError as e:
    print(f"Warning: Could not import workflows: {e}")
    __all__ = []
