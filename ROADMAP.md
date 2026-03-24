# DevOps Bot Roadmap

This document outlines the planned features and improvements for the devops-bot project, organized by category.

---

## 📋 Current State

The bot currently supports:
- ✅ Basic CLI entry point (`python app/main.py`)
- ✅ Azure DevOps API client (projects, work items)
- ✅ Health checks task (list projects)
- ⚠️ List bugs task (has a bug - queries non-Bugs)
- ✅ Basic LLM advisor (OpenAI integration)
- ✅ Pydantic schemas for type safety
- ✅ Logging infrastructure

---

## 🎯 Deterministic Tasks (Rule-Based Automation)

These tasks run without LLM involvement, following predefined rules.

### Board Management
- [ ] **Fix list_bugs task** - Correct the WIQL query to actually fetch Bug work items
- [ ] **List stale work items** - Find items not updated in X days (configurable threshold)
- [ ] **Auto-close duplicate bugs** - Detect and close duplicate bug reports
- [ ] **Move closed items to "Done"** - Batch transition closed items to final state
- [ ] **Tag cleanup** - Remove orphaned or misspelled tags
- [ ] **Priority audit** - Flag items missing priority assignment

### Pipeline & CI/CD
- [ ] **Broken pipeline detector** - Alert on failed pipeline runs
- [ ] **Pipeline duration trends** - Track and report slow builds
- [ ] **Failed test summarizer** - Aggregate test failures across runs
- [ ] **Orphaned agents cleanup** - Remove offline build agents

### Repository Maintenance
- [ ] **Stale branch cleanup** - Identify and optionally delete branches not touched in X days
- [ ] **Branch protection checker** - Verify critical branches have required policies
- [ ] **Missing README detector** - Flag repos without documentation
- [ ] **Dependency vulnerability scanner** - Check for outdated/vulnerable packages

### Team Health
- [ ] **Workload distribution report** - Show items assigned per team member
- [ ] **Sprint burndown helper** - Calculate remaining work vs time
- [ ] **Escalation detector** - Flag high-priority items open > N days

---

## 🤖 LLM Wrapper Tasks (AI-Enhanced)

These tasks wrap deterministic data with LLM intelligence for better insights.

### Summarization
- [ ] **Sprint summary generator** - Weekly digest of completed/in-progress/blocked items
- [ ] **Bug report summarizer** - Condense lengthy bug descriptions into actionable summaries
- [ ] **Pipeline failure analysis** - Explain why builds are failing in plain language
- [ ] **Meeting notes processor** - Extract action items from meeting transcripts

### Review & Rating
- [ ] **PR review assistant** - Analyze code changes and suggest improvements
- [ ] **Work item priority rating** - Score items by urgency/impact using LLM
- [ ] **Technical debt assessor** - Rate backlog items by refactoring priority
- [ ] **Risk assessment** - Evaluate feature complexity and failure probability

### Enhancement
- [ ] **Description improver** - Rewrite vague work items with clearer acceptance criteria
- [ ] **Test case suggestion** - Propose test cases for user stories
- [ ] **Root cause analyzer** - Help identify underlying causes of bugs
- [ ] **Title generator** - Create concise, descriptive titles for items

---

## 💡 Proactive Task Suggestions

These are ideas the bot could generate autonomously to help the team.

### Predictive Analytics
- [ ] **Trend detection** - Notice increasing bug rates and alert early
- [ ] **Velocity prediction** - Estimate sprint completion based on historical data
- [ ] **Bottleneck identification** - Find work items stuck waiting longest

### Automation Opportunities
- [ ] **Repetitive task detector** - Identify manual steps that could be scripted
- [ ] **Approval chain optimizer** - Suggest streamlined review workflows
- [ ] **Template generator** - Create work item templates for recurring work types

### Knowledge Management
- [ ] **Linked issue finder** - Discover related items that should be connected
- [ ] **Decision logger** - Track important project decisions with context
- [ ] **FAQ updater** - Suggest FAQ entries based on repeated questions

### Team Health Signals
- [ ] **Burnout risk indicator** - Flag individuals with excessive workload
- [ ] **Idle item detector** - Items assigned but no activity for extended periods
- [ ] **Silo breaker** - Suggest cross-training when certain people own too much

---

## 🔧 Infrastructure Improvements

### CLI & UX
- [ ] **Upgrade to Typer** - Rich CLI with subcommands and help
- [ ] **Interactive mode** - Guided task selection with menus
- [ ] **Output formatters** - Support JSON, YAML, Markdown output formats
- [ ] **Progress indicators** - Show progress for long-running tasks

### Scheduling & Automation
- [ ] **APScheduler integration** - Run tasks on cron-like schedules
- [ ] **Daemon mode** - Long-running service with webhook triggers
- [ ] **Kubernetes CronJob manifests** - Production deployment options

### Reporting & Notifications
- [ ] **Slack webhook integration** - Send alerts to channels
- [ ] **Email digest** - Scheduled summary emails
- [ ] **Dashboard generation** - Static HTML/JSON status pages
- [ ] **GitHub/GitLab issue creation** - File issues for detected problems

### Extensibility
- [ ] **Plugin system** - Auto-discover tasks from `tasks/` directory
- [ ] **Multi-org support** - Handle multiple Azure DevOps/GitHub orgs
- [ ] **Configuration file** - YAML/JSON config for organization settings
- [ ] **Dry-run mode** - Preview changes without applying them

---

## 📈 Implementation Priority

### Phase 1: Foundation (Quick Wins)
1. Fix the bugs task query
2. Add stale work item detector
3. Implement broken pipeline detector
4. Complete summarizer.py and reviewer.py
5. Add basic Slack notification support

### Phase 2: Core Features
6. Sprint summary generator (LLM)
7. Work item priority rating (LLM)
8. Stale branch cleanup
9. Workload distribution report
10. Scheduler integration

### Phase 3: Advanced
11. Typer CLI upgrade
12. Trend detection & predictions
13. Plugin system
14. Multi-org support
15. Dashboard generation

---

## 🐛 Known Issues

| Issue | Description | Status |
|-------|-------------|--------|
| list_bugs query bug | WIQL excludes Bug type instead of including it | TODO |
| Empty files | summarizer.py and reviewer.py need implementation | TODO |
| No error handling | Client lacks robust error handling for API failures | TODO |

---

## 💭 Future Possibilities

- **Multi-agent coordination** - Specialized bots for different concerns
- **Self-improving prompts** - Learn from team feedback on LLM outputs
- **Custom model fine-tuning** - Train on org-specific patterns
- **Natural language interface** - Chat with the bot about the board
- **Integration marketplace** - Shareable task plugins

---

*Last updated: 2026-03-24*
