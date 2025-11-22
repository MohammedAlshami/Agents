"""
Schema package for AcademicAI document elements.
"""

from .base_schemas import TableSchema, ListItemSchema, QuerySchema, ReferenceSchema, ReferencesSchema
from .document_schema import DocumentSchema
from .chat_schema import (
    ChatResponse, MCPOperation, MCPOperationType, DataSource, DocumentType, ChatMode,
    DataSourceInfo, FollowUpQuestion, MCPCapabilities, ConversationContext, 
    SearchEngineStats, SystemStatus
)
from .router_schema import RouterResponse

__all__ = [
    'TableSchema',
    'ListItemSchema',
    'QuerySchema',
    'ReferenceSchema',
    'ReferencesSchema',
    'DocumentSchema',
    'ChatResponse',
    'MCPOperation',
    'MCPOperationType',
    'DataSource',
    'DocumentType',
    'ChatMode',
    'DataSourceInfo',
    'FollowUpQuestion',
    'MCPCapabilities',
    'ConversationContext',
    'SearchEngineStats',
    'SystemStatus',
    'RouterResponse'
]
