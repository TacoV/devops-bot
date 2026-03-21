Great idea — and yes, you don’t need MCP unless you’re building a reusable protocol server for many tools.
For a **local DevOps assistant bot**, a clean Python service + API clients + optional LLM layer is simpler and more maintainable.

Below is a solid, production-friendly **boilerplate architecture** you can build on and package as Docker.

---

# 🧱 Project Overview

Your bot will:

1. **Connect to your DevOps platform APIs**
   (boards, pipelines, repos, work items, etc.)

2. **Run maintenance tasks**

   * Health checks
   * Broken pipeline detection
   * Stale branch cleanup
   * Work item hygiene
   * Auto-fixes

3. **Optional LLM layer**

   * Summaries
   * Rewrite work items
   * PR review suggestions
   * Root-cause analysis hints

4. **Run locally or as a containerized worker**

---

# 🗂️ Suggested Project Structure

```
devops-bot/
│
├─ app/
│  ├─ main.py                # Entry point
│  ├─ config.py              # Settings & secrets
│  │
│  ├─ clients/               # API integrations
│  │  ├─ devops_client.py
│  │  ├─ git_client.py
│  │  └─ jira_client.py
│  │
│  ├─ tasks/                 # Maintenance jobs
│  │  ├─ health_checks.py
│  │  ├─ board_cleanup.py
│  │  ├─ pipeline_checks.py
│  │  └─ repo_maintenance.py
│  │
│  ├─ llm/                   # Optional AI helpers
│  │  ├─ advisor.py
│  │  ├─ summarizer.py
│  │  └─ reviewer.py
│  │
│  ├─ utils/
│  │  ├─ logger.py
│  │  └─ helpers.py
│  │
│  └─ models/
│     └─ schemas.py
│
├─ requirements.txt
├─ Dockerfile
├─ .env.example
└─ README.md
```

---

# 🧠 Core Design Pattern

Use a **Task Runner pattern**:

```
main.py → choose task → task uses clients → optional LLM → report
```

This keeps it modular and easy to expand.

---

# 🧩 Minimal Boilerplate Code

## `app/main.py`

```python
import argparse
from tasks.health_checks import run_health_checks
from tasks.board_cleanup import cleanup_board
from utils.logger import get_logger

log = get_logger()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task", help="Task to run")
    args = parser.parse_args()

    if args.task == "health":
        run_health_checks()
    elif args.task == "cleanup-board":
        cleanup_board()
    else:
        log.error(f"Unknown task: {args.task}")

if __name__ == "__main__":
    main()
```

---

## `app/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

DEVOPS_URL = os.getenv("DEVOPS_URL")
DEVOPS_TOKEN = os.getenv("DEVOPS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

---

## `app/clients/devops_client.py`

```python
import requests
from config import DEVOPS_URL, DEVOPS_TOKEN

class DevOpsClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {DEVOPS_TOKEN}",
            "Content-Type": "application/json"
        })

    def get_projects(self):
        r = self.session.get(f"{DEVOPS_URL}/_apis/projects")
        r.raise_for_status()
        return r.json()
```

---

## `app/tasks/health_checks.py`

```python
from clients.devops_client import DevOpsClient
from utils.logger import get_logger

log = get_logger()

def run_health_checks():
    client = DevOpsClient()
    projects = client.get_projects()
    log.info(f"Found {len(projects.get('value', []))} projects")
```

---

## Optional LLM Layer

## `app/llm/advisor.py`

```python
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def get_advice(text):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": text}]
    )
    return resp.choices[0].message.content
```

---

# 📦 requirements.txt

```
requests
python-dotenv
openai
pydantic
rich
```

---

# 🐳 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

ENV PYTHONPATH=/app

ENTRYPOINT ["python", "app/main.py"]
```

---

# 🔐 .env.example

```
DEVOPS_URL=https://dev.azure.com/your-org
DEVOPS_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here
```

---

# ▶️ Run Locally

```bash
pip install -r requirements.txt
python app/main.py health
```

---

# 🐳 Build & Run Docker

```bash
docker build -t devops-bot .
docker run --env-file .env devops-bot health
```

---

# 🧩 Nice Additions (Recommended)

## 1. Scheduler

Run periodic jobs:

* APScheduler
* Cron inside container
* Kubernetes CronJob

## 2. CLI Upgrade

Use:

```
typer
```

for beautiful CLI.

## 3. Reporting

* Slack webhook alerts
* Email summaries
* Markdown reports

## 4. Plugin System

Auto-discover tasks:

```python
# auto-load tasks from tasks/ folder
```

---

# 🧠 If You're Using Specific Platforms

You can add first-class clients for:

* **Azure DevOps**
* **GitHub**
* **GitLab**
* **Jira**
* **Jenkins**

---

# 🚀 If You Want, I Can Also Provide

* Async version (faster API calls)
* Web dashboard UI
* PR auto-review bot
* Board auto-grooming bot
* AI incident postmortem generator
* Multi-agent tool-using LLM
* Kubernetes deployment manifests

---

If you tell me:

1️⃣ Which DevOps platform(s)
2️⃣ Local script vs long-running service
3️⃣ Whether AI features are core or optional

I can tailor this into a ready-to-run starter repo.
