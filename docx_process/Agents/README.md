# Takeover Document Generation Workflow

## Overview

This workflow is designed to automatically generate takeover documents by intelligently gathering information from multiple sources, processing it through AI agents, and generating structured documents. The system uses a multi-agent approach where each agent specializes in specific tasks.

## Workflow Architecture

### Core Objective
Generate complete takeover documents by:
1. **Data Collection**: Gathering variable values from documents, web search, and user input
2. **Dependency Management**: Tracking which variables are needed for each section
3. **Document Generation**: Creating sections with AI-generated content based on templates and collected data
4. **Quality Assurance**: Ensuring all dependencies are met before section generation

## Existing Nodes Analysis

### ✅ **Already Implemented Nodes**

#### 1. **Project Details Node** (`project_details_node.py`)
- **Purpose**: Manages project data, session management, and file references
- **Capabilities**: 
  - Project CRUD operations
  - Session management (project_id as session_id)
  - File reference tracking
  - Template and variable storage
- **Status**: ✅ Ready for use

#### 2. **Document Loader Node** (`document_loader_node.py`)
- **Purpose**: Loads documents using LangChain document loaders
- **Capabilities**:
  - PDF, Word, Excel, PowerPoint, CSV, JSON loading
  - Directory loading with pattern matching
  - Web content loading
  - Multiple file format support
- **Status**: ✅ Ready for use

#### 3. **Chat Agent Node** (`chat_agent_node.py`)
- **Purpose**: Handles user conversations and general knowledge questions
- **Capabilities**:
  - RAG-enabled responses
  - Streaming support
  - Context-aware conversations
  - Database integration
- **Status**: ✅ Ready for use

#### 4. **Search Agent Node** (`search_agent_node.py`)
- **Purpose**: Performs web search and current information queries
- **Capabilities**:
  - Perplexity API integration
  - Multiple search types (web, news, academic)
  - Source tracking
  - Result filtering
- **Status**: ✅ Ready for use

#### 5. **Template Parser Node** (`template_parser_node.py`)
- **Purpose**: Parses HTML templates and variable lists from markdown
- **Capabilities**:
  - Template variable extraction
  - Variable validation
  - Template-variable matching
  - Markdown parsing
- **Status**: ✅ Ready for use

#### 6. **HTML to Markdown Node** (`html_to_markdown_node.py`)
- **Purpose**: Converts HTML content to Markdown format
- **Capabilities**:
  - HTML cleaning and conversion
  - Link and image conversion
  - Format customization
  - Conversion statistics
- **Status**: ✅ Ready for use

### ❌ **Missing Nodes (Need to be Created)**

#### 1. **Document Generation Agent Node** 
- **Purpose**: Generate document sections using AI with templates and variables
- **Input**: Template, variables, context
- **Output**: Generated document section
- **Status**: ❌ **NEEDS TO BE CREATED**

#### 2. **Dependency Manager Node**
- **Purpose**: Track and manage variable dependencies across sections
- **Input**: Section requirements, current variables
- **Output**: Missing dependencies, dependency status
- **Status**: ❌ **NEEDS TO BE CREATED**

#### 3. **Variable Extractor Node**
- **Purpose**: Extract variable values from loaded documents
- **Input**: Documents, variable list
- **Output**: Extracted variable values
- **Status**: ❌ **NEEDS TO BE CREATED**

#### 4. **Markdown to File Node**
- **Purpose**: Convert generated markdown to .md files
- **Input**: Markdown content, file path
- **Output**: Saved .md file
- **Status**: ❌ **NEEDS TO BE CREATED**

## Workflow Design

### Phase 1: Project Initialization
```
Project Agent Node
├── Load project details
├── Get document templates and variables
├── Initialize session (project_id as session_id)
└── Load file references
```

### Phase 2: Document Processing (if files exist)
```
Document Loader Node
├── Load PDFs, Word docs, etc.
├── Extract text content
└── Pass to Variable Extractor Node

Variable Extractor Node
├── Analyze documents for variable values
├── Extract relevant information
└── Store in Project Agent Node
```

### Phase 3: Dependency Resolution Loop
```
For each section:
├── Dependency Manager Node
│   ├── Check section dependencies
│   ├── Identify missing variables
│   └── Determine next action
│
├── If dependencies met:
│   └── Document Generation Agent Node
│       ├── Take template + variables
│       ├── Generate section content
│       └── Store in Project Agent Node
│
├── If dependencies not met:
│   ├── Search Agent Node (try web search)
│   │   ├── Search for missing information
│   │   ├── If found: Store in Project Agent Node
│   │   └── If not found: Ask user
│   │
│   └── Chat Agent Node (ask user)
│       ├── Present missing variables to user
│       ├── Extract user responses
│       └── Store in Project Agent Node
```

### Phase 4: Document Assembly
```
Markdown to File Node
├── Combine all generated sections
├── Create final document structure
└── Save as .md file
```

## Detailed Workflow Steps

### Step 1: Project Setup
1. **Project Agent Node** loads project details
2. Retrieves document templates and variable lists
3. Initializes session using project_id
4. Loads any uploaded file references

### Step 2: Document Analysis (if files exist)
1. **Document Loader Node** processes uploaded files
2. **Variable Extractor Node** analyzes documents for variable values
3. Extracted values stored in **Project Agent Node**

### Step 3: Section-by-Section Processing
For each document section:

#### 3.1: Dependency Check
1. **Dependency Manager Node** checks section requirements
2. Identifies missing variables
3. Determines if section can be generated

#### 3.2: Information Gathering (if dependencies not met)
1. **Search Agent Node** searches web for missing information
2. If found: Store results in **Project Agent Node**
3. If not found: **Chat Agent Node** asks user for missing data
4. User responses extracted and stored

#### 3.3: Section Generation (when dependencies met)
1. **Document Generation Agent Node** receives:
   - Section template
   - All required variables
   - Context from previous sections
2. AI generates section content
3. Generated content stored in **Project Agent Node**

### Step 4: Document Finalization
1. **Markdown to File Node** combines all sections
2. Creates final document structure
3. Saves as .md file

## Node Communication Flow

```
Project Agent Node (Central Hub)
    ↕️
Document Loader Node → Variable Extractor Node
    ↕️
Dependency Manager Node
    ↕️
Search Agent Node ← Chat Agent Node
    ↕️
Document Generation Agent Node
    ↕️
Markdown to File Node
```

## Key Features

### 1. **Dependency Management**
- Tracks which variables are needed for each section
- Avoids duplicate information gathering
- Ensures all dependencies are met before generation

### 2. **Multi-Source Information Gathering**
- Document analysis (if files uploaded)
- Web search (for current information)
- User input (for specific details)

### 3. **AI-Powered Generation**
- Natural language generation (not programmatic)
- Context-aware content creation
- Template-based structure with AI flexibility

### 4. **Session Management**
- Project ID as session ID for chat history
- Persistent storage of gathered information
- Context preservation across sections

## Implementation Priority

### Phase 1: Core Missing Nodes
1. **Document Generation Agent Node** - High priority
2. **Dependency Manager Node** - High priority
3. **Variable Extractor Node** - Medium priority
4. **Markdown to File Node** - Low priority

### Phase 2: Workflow Integration
1. Create workflow orchestration
2. Implement node communication
3. Add error handling and retry logic
4. Add progress tracking

### Phase 3: Optimization
1. Add caching for repeated searches
2. Implement parallel processing where possible
3. Add quality validation
4. Add user feedback loops

## Technical Considerations

### 1. **State Management**
- Project Agent Node serves as central state store
- All other nodes read/write to this central state
- Session persistence for long-running workflows

### 2. **Error Handling**
- Graceful degradation when nodes fail
- Retry mechanisms for transient failures
- User notification for critical errors

### 3. **Performance**
- Parallel processing where possible
- Caching for repeated operations
- Progress tracking for long operations

### 4. **Scalability**
- Node-based architecture allows horizontal scaling
- Stateless nodes for better resource utilization
- Queue-based processing for high-volume operations

## Next Steps

1. **Create Missing Nodes**: Implement the 4 missing nodes identified above
2. **Workflow Orchestration**: Create the main workflow controller
3. **Integration Testing**: Test the complete workflow with sample data
4. **User Interface**: Create frontend interface for workflow management
5. **Documentation**: Add detailed API documentation for each node

This architecture provides a robust, scalable solution for automated takeover document generation while maintaining flexibility and user control over the process.
