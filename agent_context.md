# DevOps Bot - Agent Context

This document provides context for understanding the DevOps Bot project to help with future development.

## Project Overview

DevOps Bot is a local DevOps assistant that:
1. Connects to Azure DevOps APIs (boards, pipelines, repos, work items)
2. Runs maintenance tasks (health checks, bug listing, etc.)
3. Provides an optional LLM layer for summaries, reviews, and suggestions

## Architecture

```
devops-bot/
├── app/
│   ├── main.py           # Entry point - CLI task runner
│   ├── config.py        # Environment variables
│   ├── clients/
│   │   └── devops_client.py   # Azure DevOps API client
│   ├── tasks/
│   │   ├── health_checks.py   # Health check tasks
│   │   └── list_bugs.py       # Bug listing tasks
│   ├── llm/
│   │   ├── advisor.py         # LLM advice/guidance
│   │   ├── reviewer.py        # Code review (empty)
│   │   └── summarizer.py      # Summarization (empty)
│   ├── models/
│   │   └── schemas.py         # Pydantic schemas
│   └── utils/
│       ├── logger.py         # Rich logger
│       └── helpers.py         # Helpers (empty)
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Key Components

### Entry Point (`app/main.py`)
- Uses argparse for CLI task selection
- Currently supports: `health` task (runs list_bugs)
- Pattern: `python app/main.py <task>`

### Configuration (`app/config.py`)
Loads from environment variables:
- `DEVOPS_URL` - Azure DevOps organization URL
- `DEVOPS_TOKEN` - Azure DevOps personal access token
- `DEVOPS_PROJECT` - Project name
- `DEVOPS_PROJECTID` - Project ID
- `OPENAI_API_KEY` - OpenAI API key (for LLM features)
- `LOG_LEVEL` - Logging level (default: INFO)

### DevOps Client (`app/clients/devops_client.py`)
- Uses Bearer token authentication
- Methods:
  - `get_bugs()` - Query for active bugs
  - `get_work_items(ids)` - Get full work item details
  - `get_projects()` - List projects (referenced in health_checks.py)

### Tasks
- `run_health_checks()` - Calls get_projects() (note: may need implementation)
- `list_bugs()` - Gets and logs active bugs

### LLM Layer
- `get_advice(text)` - Get advice from GPT-4o-mini
- `reviewer.py` and `summarizer.py` are empty stubs

### Logging
- Uses `rich` library for colored output
- `get_logger()` returns configured logger

## Dependencies

- `requests` - HTTP client
- `python-dotenv` - Environment loading
- `openai` - OpenAI API
- `pydantic` - Data validation
- `rich` - Rich terminal output

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run tasks
python app/main.py health
python app/main.py list-bugs
```

## Notes for Development

1. The `DevOpsClient.get_bugs()` method has a bug in the WIQL query - it queries for non-Bugs instead of Bugs
2. `health_checks.py` calls `get_projects()` which may not be implemented in the client
3. LLM modules (`reviewer.py`, `summarizer.py`) are empty stubs
4. The schemas in `models/schemas.py` use Azure DevOps field naming conventions with Pydantic aliases

## Environment Variables Required

```
DEVOPS_URL=https://dev.azure.com/your-org
DEVOPS_TOKEN=your_pat_token
DEVOPS_PROJECT=your_project_name
DEVOPS_PROJECTID=your_project_id
OPENAI_API_KEY=sk-...
LOG_LEVEL=INFO
```
