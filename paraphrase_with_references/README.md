# Reference Search Agent Server

A specialized Flask server for searching academic references using OpenAlex. This server provides a simple API for finding and gathering academic papers for research projects.

## Features

- **Academic Paper Search**: Search for academic papers using OpenAlex database
- **Multiple Search Queries**: Generate diverse search queries for comprehensive results
- **Quality Rating Filtering**: Filter results by journal quality (Q1, Q2, Q3, Q4)
- **Reference Deduplication**: Remove duplicate references and rank by relevance
- **Citation Analysis**: Analyze citation counts and impact metrics
- **Open Access Filtering**: Filter for open access papers
- **Simple API**: Clean REST API with GET/POST endpoints
- **Health Monitoring**: Built-in health check endpoints
- **Session Management**: Per-session workflow instances

## API Endpoints

### Health Check
- **GET** `/api/v1/reference-search/` - Health check endpoint

### Reference Search
- **POST** `/api/v1/reference-search/` - Search for academic references

#### Request Format
```json
{
    "title": "Research paper title",
    "problem_statement": "The research problem or question",
    "num_references": 20,
    "q_rating": "q1",
    "session_id": "optional_session_id",
    "api_key": "optional_openai_api_key",
    "openalex_email": "optional_openalex_email"
}
```

#### Response Format
```json
{
    "success": true,
    "references": [
        {
            "id": "paper_id",
            "title": "Paper Title",
            "authors": ["Author 1", "Author 2"],
            "publication_year": 2023,
            "citation_count": 150,
            "abstract": "Paper abstract...",
            "doi": "10.1000/example",
            "url": "https://example.com/paper",
            "source": "Journal Name",
            "is_open_access": true,
            "topics": ["topic1", "topic2"],
            "type": "journal-article",
            "query_used": "search query that found this paper"
        }
    ],
    "metadata": {
        "execution_time": 5.67,
        "timestamp": "2024-01-01T00:00:00Z",
        "num_references": 20,
        "queries_generated": 8,
        "references_found": 20
    },
    "workflow_id": "simple_reference_search_20240101_000000",
    "model": "gpt-4o-mini",
    "agent": "reference_search"
}
```

### Search Query Generation
- **POST** `/api/v1/reference-search/queries` - Generate search queries only

#### Request Format
```json
{
    "title": "Research paper title",
    "problem_statement": "The research problem or question",
    "num_references": 20,
    "session_id": "optional_session_id",
    "api_key": "optional_openai_api_key"
}
```

#### Response Format
```json
{
    "success": true,
    "queries": [
        "artificial intelligence healthcare applications",
        "machine learning medical diagnosis",
        "AI clinical decision support systems"
    ],
    "metadata": {
        "execution_time": 1.23,
        "timestamp": "2024-01-01T00:00:00Z",
        "num_queries": 8,
        "num_references": 20
    },
    "workflow_id": "simple_reference_search_20240101_000000",
    "model": "gpt-4o-mini",
    "agent": "reference_search"
}
```

## Installation

1. **Clone and navigate to the directory**:
   ```bash
   cd servers/reference_search_agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and OpenAlex email
   ```

4. **Run the server**:
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5003` by default.

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key for query generation
- `OPENALEX_EMAIL`: Your email for OpenAlex polite pool (optional but recommended)
- `PORT`: Server port (default: 5003)
- `HOST`: Server host (default: 0.0.0.0)

### Model Configuration
- **Model**: GPT-4o-mini for query generation
- **Temperature**: 0.7 (for diverse query generation)
- **Max Tokens**: 2000

## Usage Examples

### Basic Reference Search
```bash
curl -X POST http://localhost:5003/api/v1/reference-search/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Impact of AI on Healthcare",
    "problem_statement": "How does artificial intelligence improve healthcare outcomes?",
    "num_references": 20,
    "q_rating": "q1"
  }'
```

### Generate Search Queries Only
```bash
curl -X POST http://localhost:5003/api/v1/reference-search/queries \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Machine Learning in Education",
    "problem_statement": "What are the benefits of using machine learning in educational systems?",
    "num_references": 15
  }'
```

### With Custom Parameters
```bash
curl -X POST http://localhost:5003/api/v1/reference-search/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sustainable Energy Solutions",
    "problem_statement": "How can renewable energy technologies address climate change?",
    "num_references": 30,
    "q_rating": "q2",
    "session_id": "research_session_123",
    "api_key": "your_openai_api_key",
    "openalex_email": "your_email@example.com"
  }'
```

## Architecture

### Components
- **ReferencesGathererAgent**: Core agent for reference search and gathering
- **OpenAlexSearchService**: OpenAlex API integration
- **SimpleReferenceSearchWorkflow**: Workflow orchestration
- **Flask Routes**: API endpoint handlers

### Workflow
1. Receive search parameters via POST request
2. Generate multiple diverse search queries using AI
3. Search OpenAlex database for each query
4. Deduplicate and rank results by relevance
5. Return structured reference data with metadata

## Quality Ratings

The server supports filtering by journal quality ratings:
- **Q1**: Top 25% of journals by impact factor
- **Q2**: 25-50% of journals by impact factor
- **Q3**: 50-75% of journals by impact factor
- **Q4**: Bottom 25% of journals by impact factor

## Error Handling

The server provides comprehensive error handling:
- **400**: Invalid JSON or missing required fields
- **500**: Server errors or API processing failures

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Structure
```
reference_search_agent/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── Agents/
│   ├── engines/
│   │   └── search/                # Search engines
│   │       ├── references_gatherer.py
│   │       └── openalex.py
│   └── nodes/
│       └── workflows/              # Workflow orchestration
│           └── reference_search_workflow.py
└── server/
    └── routes/                    # API routes
        └── api/
            └── v1/
                └── reference_search_routes.py
```

## License

This project is part of the Presly AI Document Editor system.
