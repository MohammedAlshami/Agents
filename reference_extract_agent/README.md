# Reference Extract Agent Server

A specialized Flask server for extracting and structuring references from text using AI. This server provides a simple API for intelligently parsing academic and non-academic text to extract references in various formats (APA, MLA, Chicago, URLs, etc.) and return structured JSON.

## Features

- **Reference Extraction**: Intelligently extract all types of references from text
- **Citation Format Detection**: Automatically detect APA, MLA, Chicago, and other formats
- **Academic Reference Parsing**: Specialized for academic citations and references
- **URL and Web Link Extraction**: Extract web links and URLs from text
- **Book and Journal Reference Extraction**: Handle various publication types
- **Simple API**: Clean REST API with GET/POST endpoints
- **Health Monitoring**: Built-in health check endpoints
- **Session Management**: Per-session workflow instances

## API Endpoints

### Health Check
- **GET** `/api/v1/reference-extract/` - Health check endpoint

### Reference Extraction
- **POST** `/api/v1/reference-extract/` - Extract references from text

#### Request Format
```json
{
    "text": "According to Smith (2024), the impact of AI on healthcare is significant. Recent studies (Johnson et al., 2023) have shown promising results. For more information, visit https://example.com/research.",
    "session_id": "optional_session_id",
    "api_key": "optional_openai_api_key",
    "project_id": "optional_project_id",
    "user_id": "optional_user_id",
    "context": "optional_context"
}
```

#### Response Format
```json
{
    "success": true,
    "text": "Original text content",
    "references": [
        {
            "id": "ref_001",
            "full_citation": "Smith, J. (2024). The Impact of AI on Healthcare. Journal of Medical Technology, 15(3), 45-67.",
            "short_form": "Smith, 2024",
            "type": "academic",
            "order": 1,
            "original_text": "Smith (2024)"
        },
        {
            "id": "ref_002",
            "full_citation": "Johnson, A., Brown, B., & Wilson, C. (2023). Recent Studies on AI Applications. Nature Medicine, 29(2), 123-145.",
            "short_form": "Johnson et al., 2023",
            "type": "academic",
            "order": 2,
            "original_text": "Johnson et al., 2023"
        },
        {
            "id": "ref_003",
            "full_citation": "https://example.com/research",
            "short_form": "example.com/research",
            "type": "url",
            "order": 3,
            "original_text": "https://example.com/research"
        }
    ],
    "extraction_metadata": {
        "total_references": 3,
        "extraction_confidence": 0.95,
        "detected_formats": ["APA", "URL"],
        "processing_time": "2024-01-01T00:00:00Z",
        "agent_version": "1.0.0"
    },
    "execution_time": 2.34,
    "timestamp": "2024-01-01T00:00:00Z",
    "workflow_id": "simple_reference_extract_20240101_000000",
    "model": "gpt-4o-mini",
    "agent": "reference_extract"
}
```

## Installation

1. **Clone and navigate to the directory**:
   ```bash
   cd servers/reference_extract_agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

4. **Run the server**:
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5003` by default.

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `PORT`: Server port (default: 5003)
- `HOST`: Server host (default: 0.0.0.0)

### Model Configuration
- **Model**: GPT-4o-mini
- **Temperature**: 0.1 (for consistent extraction)
- **Max Tokens**: 2000

## Usage Examples

### Basic Reference Extraction
```bash
curl -X POST http://localhost:5003/api/v1/reference-extract/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "According to Smith (2024), the impact of AI on healthcare is significant. Recent studies (Johnson et al., 2023) have shown promising results."
  }'
```

### With Session Management
```bash
curl -X POST http://localhost:5003/api/v1/reference-extract/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The research methodology follows APA guidelines (American Psychological Association, 2020). Additional references include Brown, A. (2023). Machine Learning Applications. New York: Academic Press.",
    "session_id": "research_session_123",
    "project_id": "reference_extraction_456"
  }'
```

## Architecture

### Components
- **ReferenceExtractAgent**: Core AI agent for reference extraction
- **ReferenceExtractAgentNode**: Node interface wrapper
- **SimpleReferenceExtractWorkflow**: Workflow orchestration
- **Flask Routes**: API endpoint handlers

### Workflow
1. Receive text content via POST request
2. Initialize or retrieve session-specific workflow
3. Process text through reference extract agent
4. Return structured references with metadata

## Supported Reference Types

- **Academic Citations**: APA, MLA, Chicago formats
- **URLs and Web Links**: HTTP/HTTPS links
- **Books**: Author, title, publisher references
- **Journal Articles**: Volume, issue, page numbers
- **Conference Papers**: Proceedings and conference references
- **Reports and Documents**: Technical and research reports
- **Other References**: Any other identifiable reference format

## Error Handling

The server provides comprehensive error handling:
- **400**: Invalid JSON or missing required fields
- **500**: Server errors or AI processing failures

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Structure
```
reference_extract_agent/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── Agents/
│   ├── nodes/
│   │   ├── interface/             # Node interfaces
│   │   │   └── reference_extract_agent_node.py
│   │   ├── nodes/
│   │   │   └── ai/
│   │   │       └── reference_extract_agent/ # Core reference extract agent
│   │   └── workflows/             # Workflow orchestration
│   │       └── reference_extract_workflow.py
│   └── schema/                    # Data schemas
└── server/
    └── routes/                    # API routes
        └── api/
            └── v1/
                └── reference_extract_routes.py
```

## License

This project is part of the Presly AI Document Editor system.