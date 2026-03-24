# DevOps Bot Roadmap

A local Azure DevOps assistant bot for work item maintenance. Python + API clients + LLM layer.

## Current Features

- **CLI tasks**: `health`, `bugs`, `stale`, `summarize`, `rate`, `advice`
- **LLM integration**: Ollama (free, local) with OpenAI fallback
- **Work item queries**: WIQL-based retrieval and filtering

## Roadmap

### Core Maintenance Tasks
- [ ] **Auto-fix work items** - Close duplicates, update states, remove stale tags
- [ ] **Hierarchy validation** - Ensure proper parent-child relationships
- [ ] **Sprint hygiene** - Flag items outside sprints, check sprint capacity

### LLM Enhancements
- [ ] **Self-improvement** - Bot advises on improving its own prompts and behavior
- [ ] **Markdown reports** - Generate shareable summary reports

### UX Improvements
- [ ] **Typer CLI** - Replace argparse with Typer for better CLI experience
- [ ] **Auto-discover tasks** - Load tasks from `tasks/` folder dynamically
- [ ] **Scheduler** - APScheduler for cron-like execution

### Agentic Capabilities
- [ ] **Idea → Query → Conclusion → Feedback** - Fully autonomous task flow

## Non-Goals

Per the README, this bot intentionally does NOT:
- Connect to Teams, mail, or Slack
- Handle builds or pipelines
- Manage repositories
- Support multiple projects
