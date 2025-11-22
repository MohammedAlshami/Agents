# DocX Process Server

A simple Flask server for processing Word documents (.docx) and converting them to TipTap JSON format.

## Features

- **Single Route Design**: One endpoint handles both health checks and document processing
- **Word Document Processing**: Extracts content, images, tables, and metadata from .docx files
- **TipTap JSON Conversion**: Converts processed content to TipTap editor format
- **Cloudflare R2 Integration**: Downloads files from Cloudflare R2 URLs
- **Image Extraction**: Extracts and converts images to base64 format
- **Table Processing**: Handles complex table structures
- **Document Structure Analysis**: Provides document metadata and structure information

## API Endpoints

### GET `/api/v1/docx/` or `/api/v1/docx/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "DocX Process API",
  "version": "1.0.0",
  "message": "DocX processing service is running"
}
```

### POST `/api/v1/docx/`
Process a Word document and convert to TipTap JSON.

**Request Body:**
```json
{
  "file_url": "https://your-cloudflare-r2-url/document.docx"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "processed_content": {
      "filename": "document.docx",
      "title": "Document Title",
      "ordered_content": [...],
      "headers": [...],
      "footers": [...],
      "metadata": {...},
      "structure": {...}
    },
    "tiptap_content": {
      "type": "doc",
      "content": [...]
    },
    "filename": "document.docx"
  },
  "message": "Word document processed successfully"
}
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (optional):
```bash
export CLOUDFLARE_PUBLIC_DOMAIN="your-domain.com"
```

3. Run the server:
```bash
python app.py
```

The server will start on port 5007 by default.

## Usage

### Health Check
```bash
curl http://localhost:5007/api/v1/docx/
```

### Process Document
```bash
curl -X POST http://localhost:5007/api/v1/docx/ \
  -H "Content-Type: application/json" \
  -d '{"file_url": "https://your-file-url/document.docx"}'
```

## Dependencies

- **Flask**: Web framework
- **flask-cors**: CORS support
- **python-docx**: Word document processing
- **requests**: HTTP client for file downloads
- **python-dotenv**: Environment variable management

## Error Handling

The server includes comprehensive error handling for:
- Invalid file URLs
- Download failures
- Document processing errors
- Malformed requests
- Network timeouts

All errors return appropriate HTTP status codes and descriptive error messages.
