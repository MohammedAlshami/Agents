# Enhanced Humanize Agent Server

A specialized Flask server for sophisticated text humanization using AI. This server provides an advanced API for transforming AI-generated text into natural, human-like academic prose, particularly optimized for research writing based on analysis of top-tier business journals.

## Enhanced Features

- **Sophisticated Academic Writing**: Transform AI-generated text into sophisticated, human-like academic prose
- **Journal-Quality Patterns**: Based on analysis of Journal of Business Research and other top-tier academic sources
- **Advanced Transitions**: Incorporates sophisticated academic linking phrases and methodological language
- **AI Detection Avoidance**: Optimized to avoid AI detection tools with natural variations
- **Academic Precision**: Maintains scholarly rigor while ensuring readability
- **Simple API**: Clean REST API with GET/POST endpoints
- **Health Monitoring**: Built-in health check endpoints
- **Session Management**: Per-session workflow instances

## API Endpoints

### Health Check
- **GET** `/api/v1/humanize/` - Health check endpoint

### Text Humanization
- **POST** `/api/v1/humanize/` - Humanize text

#### Request Format
```json
{
    "text": "The text to humanize",
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
    "original_text": "The original text",
    "humanized_text": "The humanized text",
    "execution_time": 1.23,
    "timestamp": "2024-01-01T00:00:00Z",
    "workflow_id": "simple_humanize_20240101_000000",
    "model": "gpt-4o-mini",
    "agent": "humanize"
}
```

## Installation

1. **Clone and navigate to the directory**:
   ```bash
   cd servers/humanize_agent
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

The server will start on `http://localhost:5001` by default.

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `PORT`: Server port (default: 5001)
- `HOST`: Server host (default: 0.0.0.0)

### Model Configuration
- **Model**: GPT-4o-mini
- **Temperature**: 0.2 (for consistent output)
- **Max Tokens**: 4000

### Enhanced Academic Writing Patterns
The humanize agent now incorporates sophisticated academic writing patterns based on analysis of top-tier business research journals:

- **Sophisticated Transitions**: "Furthermore," "Moreover," "Additionally," "Consequently," "Therefore," "However," "Nevertheless," "In contrast," "Specifically," "Particularly," "Notably," "Interestingly," "Surprisingly," "Unexpectedly"
- **Methodological Language**: "Drawing on," "Employing," "Utilizing," "Based on," "Using data from," "Employing survey data," "Combining different data sources"
- **Result-Oriented Language**: "Findings show," "Results demonstrate," "Evidence suggests," "The analysis reveals," "Data indicates," "The study finds"
- **Academic Linking Structures**: "This study examines," "The findings suggest," "Results indicate that," "The implications are," "This research contributes to," "The paper proposes that"

## Usage Examples

### Basic Text Humanization
```bash
curl -X POST http://localhost:5001/api/v1/humanize/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Furthermore, the results indicate that the hypothesis was supported by the data analysis."
  }'
```

### With Session Management
```bash
curl -X POST http://localhost:5001/api/v1/humanize/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Moreover, it is important to note that the findings demonstrate significant correlation.",
    "session_id": "user_session_123",
    "project_id": "research_project_456"
  }'
```

## Architecture

### Components
- **HumanizeAgent**: Core AI agent for text humanization
- **HumanizeAgentNode**: Node interface wrapper
- **SimpleHumanizeWorkflow**: Workflow orchestration
- **Flask Routes**: API endpoint handlers

### Workflow
1. Receive text input via POST request
2. Initialize or retrieve session-specific workflow
3. Process text through humanize agent
4. Return humanized text with metadata

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
humanize_agent/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── Agents/
│   ├── nodes/
│   │   ├── interface/             # Node interfaces
│   │   │   └── humanize_agent_node.py
│   │   ├── nodes/
│   │   │   └── ai/
│   │   │       └── humanize_agent/ # Core humanize agent
│   │   └── workflows/             # Workflow orchestration
│   │       └── humanize_workflow.py
│   └── schema/                    # Data schemas
└── server/
    └── routes/                    # API routes
        └── api/
            └── v1/
                └── humanize_routes.py
```

## License

This project is part of the Presly AI Document Editor system.