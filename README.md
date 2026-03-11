# DevOps Teams Bot

Azure DevOps → Microsoft Teams notification bot.  
**No Azure AD app registration required. No infrastructure in the client's tenant.**

---

## Architecture

```
Azure DevOps          Your Server           Microsoft Teams
  Service Hooks  →→→  Express.js  →→→  Workflows Webhook URL
                       (+ LLM)
```

Your server lives on **your own infra** (Railway, Fly.io, VPS, etc.).  
The client only configures two things in their tenant — both are self-service.

---

## What the Client Needs to Do (~10 min total)

### 1. Create a Teams Workflows Webhook (2 min)

1. Open the target Teams channel
2. Click **+** (Apps) → search **Workflows**
3. Choose template: _"Post to a channel when a webhook request is received"_
4. Follow the wizard → copy the generated **webhook URL**
5. Paste it into your `.env` as `TEAMS_WEBHOOK_URL`

> ⚠️ This replaces the deprecated Office 365 Connectors. Do **not** use the old "Incoming Webhook" connector.

### 2. Add Azure DevOps Service Hooks (8 min)

In **Azure DevOps → Project Settings → Service hooks → + Create subscription**:

| Event | Filters | URL |
|---|---|---|
| Work item created | Work item type = Bug | `https://your-server/webhook/devops` |
| Work item commented on | (none) | `https://your-server/webhook/devops` |
| Work item updated | Work item type = User Story, State = In Review | `https://your-server/webhook/devops` |
| _(Sprint health is on a schedule — see below)_ | | |

For each hook, under **HTTP headers** add:
```
Authorization: Bearer <WEBHOOK_AUTH_TOKEN>
```

---

## Local Setup

```bash
cp .env.example .env
# Fill in TEAMS_WEBHOOK_URL, DEVOPS_WEBHOOK_SECRET, WEBHOOK_AUTH_TOKEN

npm install
npm run dev
```

Expose locally with [ngrok](https://ngrok.com) for testing:
```bash
ngrok http 3000
# Use the https URL as your ADO service hook endpoint
```

---

## Deployment Options (your infra, no client involvement)

### Railway (recommended — easiest)
```bash
railway login
railway init
railway up
```

### Fly.io
```bash
fly launch
fly deploy
```

### Docker (any VPS)
```bash
docker build -t devops-bot .
docker run -p 3000:3000 --env-file .env devops-bot
```

---

## Sprint Health Reports

Sprint health isn't event-driven — it's scheduled. Set up a daily/weekly trigger using:

- **GitHub Actions** (cron schedule → `curl -X POST https://your-server/webhook/sprint-health`)
- **Any cron job** on your server
- **Azure Logic App** in the client's tenant (optional, no special permissions needed)

To wire up real sprint data, implement `fetchSprintData()` in `src/handlers/index.ts`  
using the [ADO REST API](https://learn.microsoft.com/en-us/rest/api/azure/devops/work/iterations).

---

## Enabling LLM Enrichment

Edit `.env` to add AI-generated summaries to every notification.

**Option A — Anthropic Claude:**
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

**Option B — Azure OpenAI:**
```env
LLM_PROVIDER=azure-openai
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

No code changes needed — the provider is swapped at startup.

---

## Project Structure

```
src/
├── index.ts                  # Express server + routes
├── types.ts                  # Shared TypeScript types
├── handlers/
│   └── index.ts              # One handler per event type + router
├── formatters/
│   └── adaptiveCards.ts      # Adaptive Card builders
├── llm/
│   └── index.ts              # LLM abstraction (Anthropic / Azure OpenAI / noop)
└── utils/
    ├── normalise.ts           # ADO payload → NormalisedEvent
    └── teams.ts               # POST to Teams Workflows webhook
```

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Uptime check |
| `POST` | `/webhook/devops` | Receives all ADO service hook events |
| `POST` | `/webhook/sprint-health` | Manually trigger a sprint health post |
