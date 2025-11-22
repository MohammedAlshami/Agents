# Write Agent Server

Simple general-purpose writing agent that generates text content from topics/prompts with multiple writing style options.

## Overview

The Write Agent Server provides an API for generating text content based on topics or prompts. It supports multiple writing styles (academic, technical, analytical, comparative, descriptive, argumentative) with dedicated sub-prompts for each style.

## Features

- **Text Generation**: Generate comprehensive text content from topics/prompts
- **Multiple Writing Styles**: Six different writing styles with specialized prompts
  - Academic (default)
  - Technical
  - Analytical
  - Comparative
  - Descriptive
  - Argumentative
- **Word Count Targeting**: Optional word count specification for generated content
- **Context-Aware**: Support for additional context to guide generation
- **Session Management**: Session-based workflow management

## API Endpoints

### Health Check
- `GET /api/v1/write` - Health check endpoint

### Generate Text
- `POST /api/v1/write` - Generate text from topic/prompt

#### Request Body
```json
{
  "topic": "string (required)",
  "writing_style": "string (optional, default: 'academic')",
  "word_count": "integer (optional)",
  "context": "string (optional)",
  "session_id": "string (optional)",
  "api_key": "string (optional)"
}
```

#### Response
```json
{
  "success": true,
  "topic": "string",
  "generated_text": "string",
  "writing_style": "string",
  "word_count": "integer",
  "execution_time": "number",
  "timestamp": "string",
  "workflow_id": "string",
  "model": "string",
  "agent": "string"
}
```

## Writing Styles

### Academic (Default)
Formal, scholarly, research-oriented writing style suitable for academic papers and research documents.

### Technical
Technical documentation and specifications writing style for technical documents and procedural content.

### Analytical
Analysis-focused, data-driven writing style for analytical reports and data analysis.

### Comparative
Comparison-based writing style for comparing different subjects, products, or concepts.

### Descriptive
Detailed description-focused writing style for describing processes, objects, or concepts.

### Argumentative
Persuasive, evidence-based argument writing style for making cases and presenting arguments.

## Configuration

- **Port**: 5010 (default)
- **Model**: GPT-4o-mini
- **Temperature**: 0.3 (for consistent writing)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export OPENAI_API_KEY=your_api_key_here
```

3. Run the server:
```bash
python app.py
```

## Project Structure

```
servers/write_agent/
├── Agents/
│   ├── nodes/
│   │   ├── interface/
│   │   │   ├── base_node.py
│   │   │   └── write_agent_node.py
│   │   ├── nodes/
│   │   │   └── ai/
│   │   │       ├── base_ai_model.py
│   │   │       └── write_agent/
│   │   │           ├── write_agent.py
│   │   │           └── prompts/
│   │   │               ├── main_system_prompt.py
│   │   │               └── sub_prompts/
│   │   │                   ├── academic.py
│   │   │                   ├── technical.py
│   │   │                   ├── analytical.py
│   │   │                   ├── comparative.py
│   │   │                   ├── descriptive.py
│   │   │                   └── argumentative.py
│   │   └── workflows/
│   │       └── write_workflow.py
│   └── schema/
│       └── base_schemas.py
├── server/
│   └── routes/
│       └── api/
│           └── v1/
│               └── write_routes.py
├── app.py
├── requirements.txt
└── README.md
```

## Example Usage

### Generate Academic Text
```bash
curl -X POST http://localhost:5010/api/v1/write \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "The impact of climate change on agricultural productivity",
    "writing_style": "academic",
    "word_count": 500
  }'
```

### Generate Technical Documentation
```bash
curl -X POST http://localhost:5010/api/v1/write \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "How to configure a REST API with authentication",
    "writing_style": "technical",
    "word_count": 1000
  }'
```

### Generate Analytical Content
```bash
curl -X POST http://localhost:5010/api/v1/write \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Analyzing the correlation between education and economic growth",
    "writing_style": "analytical",
    "context": "Focus on developing countries"
  }'
```

## Development

The server follows the same structure as other agent servers in the project:
- Base node interface for consistency
- Workflow-based processing
- Session management
- Error handling and logging

## License

Part of the Presly project.

