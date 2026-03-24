# DevOps Bot Roadmap

This document outlines the planned features and improvements for the devops-bot project, organized by category.

---

## 📋 Current State

The bot currently supports:
- ✅ Basic CLI entry point (`python app/main.py`)
- ✅ Azure DevOps API client (projects, work items)
- ✅ Health checks task (list projects)
- ✅ List bugs task (queries actual Bugs)
- ✅ LLM advisor (Ollama default, OpenAI fallback)
- ✅ LLM summarizer (bug summaries, sprint summaries)
- ✅ LLM reviewer (priority rating, code review, technical debt assessment)
- ✅ Pydantic schemas for type safety
- ✅ Logging infrastructure
- ✅ Stale work item detector

---

## 🎯 Deterministic Tasks (Rule-Based Automation)

These tasks run without LLM involvement, following predefined rules.

### Board Management
- [x] **Fix list_bugs task** - Correct the WIQL query to actually fetch Bug work items
- [x] **List stale work items** - Find items not updated in X days (configurable threshold)
- [ ] **Auto-close duplicate bugs** - Detect and close duplicate bug reports
- [ ] **Move closed items to "Done"** - Batch transition closed items to final state
- [ ] **Tag cleanup** - Remove orphaned or misspelled tags
- [ ] **Priority audit** - Flag items missing priority assignment

### Repository Maintenance
- [ ] **Stale branch cleanup** - Identify and optionally delete branches not touched in X days
- [ ] **Branch protection checker** - Verify critical branches have required policies
- [ ] **Missing README detector** - Flag repos without documentation

### Team Health
- [ ] **Workload distribution report** - Show items assigned per team member
- [ ] **Sprint burndown helper** - Calculate remaining work vs time
- [ ] **Escalation detector** - Flag high-priority items open > N days

---

## 🤖 LLM Wrapper Tasks (AI-Enhanced)

These tasks wrap deterministic data with LLM intelligence for better insights.

### Summarization
- [x] **Bug report summarizer** - Condense lengthy bug descriptions into actionable summaries
- [x] **Sprint summary generator** - Weekly digest of completed/in-progress/blocked items
- [ ] **Description condensor** - Shorten verbose work item descriptions

### Review & Rating
- [x] **Work item priority rating** - Score items by urgency/impact using LLM
- [ ] **PR review assistant** - Analyze code changes and suggest improvements
- [x] **Technical debt assessor** - Rate backlog items by refactoring priority
- [x] **Root cause analyzer** - Help identify underlying causes of bugs

### Enhancement
- [ ] **Acceptance criteria generator** - Propose criteria for user stories
- [ ] **Description improver** - Rewrite vague work items with clearer text

---

## 💡 Proactive Task Suggestions

These are ideas the bot could generate autonomously to help the team.

### Predictive Analytics
- [ ] **Trend detection** - Notice increasing bug rates and alert early
- [ ] **Velocity prediction** - Estimate sprint completion based on historical data
- [ ] **Bottleneck identification** - Find work items stuck waiting longest

### Automation Opportunities
- [ ] **Repetitive task detector** - Identify manual steps that could be scripted
- [ ] **Template generator** - Create work item templates for recurring work types

### Team Health Signals
- [ ] **Burnout risk indicator** - Flag individuals with excessive workload
- [ ] **Idle item detector** - Items assigned but no activity for extended periods

---

## 🔧 Infrastructure Improvements

### CLI & UX
- [ ] **Upgrade to Typer** - Rich CLI with subcommands and help
- [ ] **Interactive mode** - Guided task selection with menus
- [ ] **Output formatters** - Support JSON, YAML, Markdown output formats

### Scheduling & Automation
- [ ] **APScheduler integration** - Run tasks on cron-like schedules
- [ ] **Daemon mode** - Long-running service with webhook triggers

### Extensibility
- [ ] **Plugin system** - Auto-discover tasks from `tasks/` directory
- [ ] **Configuration file** - YAML/JSON config for organization settings
- [ ] **Dry-run mode** - Preview changes without applying them

---

## 📈 Implementation Priority

### Phase 1: Foundation (Complete)
1. ✅ Fix the bugs task query
2. ✅ Add stale work item detector
3. ✅ Complete LLM modules (summarizer, reviewer, advisor)
4. ✅ Ollama integration (free, local models)

### Phase 2: Core Features
5. Workload distribution report
6. Duplicate bug detector
7. Sprint burndown calculator
8. Scheduler integration

### Phase 3: Advanced
9. Typer CLI upgrade
10. Plugin system
11. Trend detection & predictions
12. Dashboard generation

---

## 🐛 Known Issues

| Issue | Description | Status |
|-------|-------------|--------|
| No error handling | Client lacks robust error handling for API failures | TODO |

---

*Last updated: 2026-03-24*
