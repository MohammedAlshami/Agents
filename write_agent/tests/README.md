# Write Agent Server Tests

This directory contains pytest tests for the write agent server.

## Test Structure

- `test_api_endpoints.py` - Tests for API endpoints (health check, text generation, error handling)
- `test_write_agent.py` - Tests for WriteAgent core functionality
- `test_write_workflow.py` - Tests for SimpleWriteWorkflow
- `conftest.py` - Pytest fixtures and configuration

## Running Tests

### Prerequisites

1. Make sure the write agent server is running on port 5010:
```bash
cd servers/write_agent
python app.py
```

2. Install pytest if not already installed:
```bash
pip install pytest pytest-requests
```

### Run All Tests

```bash
cd servers/write_agent
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_api_endpoints.py -v
pytest tests/test_write_agent.py -v
pytest tests/test_write_workflow.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_api_endpoints.py::TestHealthCheck -v
pytest tests/test_api_endpoints.py::TestTextGeneration -v
pytest tests/test_api_endpoints.py::TestErrorHandling -v
```

### Run Specific Test

```bash
pytest tests/test_api_endpoints.py::TestHealthCheck::test_health_check_endpoint -v
```

## Test Coverage

### API Endpoint Tests
- Health check endpoint
- Root endpoint
- API info endpoint
- Test endpoint
- Text generation with all writing styles
- Error handling (missing topic, invalid style, etc.)
- Word count functionality
- Context handling
- Session management

### Write Agent Tests
- Agent initialization
- Text generation with all styles
- Default style handling
- Context support
- Error handling

### Workflow Tests
- Workflow initialization
- Topic processing with all styles
- Context handling
- System status

## Environment Variables

You can set these environment variables to customize test behavior:

- `TEST_BASE_URL` - Base URL for the server (default: `http://localhost:5010`)
- `OPENAI_API_KEY` - OpenAI API key for testing (required for agent tests)

## Test Fixtures

The `conftest.py` file provides:
- `base_url` - Base URL for the write agent server
- `sample_topics` - Sample topics for each writing style
- `invalid_topics` - Invalid test data

## Notes

- Some tests require an active OpenAI API key
- API endpoint tests require the server to be running
- Agent and workflow tests can run without the server
- All tests use pytest fixtures for consistency

