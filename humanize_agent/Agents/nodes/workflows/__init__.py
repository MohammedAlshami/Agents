"""
Workflows Package
Contains workflow orchestration components for humanize agent.
"""

# Import the available workflows
try:
    from .humanize_workflow import SimpleHumanizeWorkflow
    __all__ = [
        'SimpleHumanizeWorkflow'
    ]
except ImportError as e:
    print(f"Warning: Could not import workflows: {e}")
    __all__ = []
