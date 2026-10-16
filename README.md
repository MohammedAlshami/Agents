# Agents

A collection of small, focused AI agents and supporting servers for academic
document writing and reference research. Each directory is a standalone Flask/FastAPI-style
service with its own requirements and supporting modules; you can run one or compose several.

## Agents included

- `conversation_agent` — chat-style assistant server
- `document_generator_agent` — document generation pipeline
- `docx_process` — DOCX handling / processing
- `humanize_agent` — paraphrasing / humanization + improvements
- `paraphrase_with_references` — paraphrasing with reference search (OpenAlex)
- `reference_extract_agent` — extract references from content
- `write_agent` — writing assistant
- `reference_search` (under paraphrase) — search ranked references
- `Agents` subpackages (nodes, engines, helpers)

## Quick start

```bash
# per agent
cd <agent_dir>
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py   # or server app entry
```

Set env vars in your shell (never commit `.env`):

```bash
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...
```

Each agent may have its own README for endpoints and configuration.

## License

Personal research utility; use at your own risk.
