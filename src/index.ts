// src/index.ts
// Express server — receives Azure DevOps service hook webhooks and routes them.

import 'dotenv/config';
import express, { Request, Response, NextFunction } from 'express';
import { DevOpsWebhookPayload } from './types';
import { routeEvent } from './handlers';
import { handleSprintHealth } from './handlers';

const app = express();
app.use(express.json());

// ─── Auth Middleware ──────────────────────────────────────────────────────────
// Azure DevOps service hooks let you add a custom HTTP header.
// Set Header: Authorization, Value: Bearer <WEBHOOK_AUTH_TOKEN>

function requireAuth(req: Request, res: Response, next: NextFunction): void {
  const token = process.env.WEBHOOK_AUTH_TOKEN;
  if (!token) {
    // Auth not configured — allow all (development only)
    next();
    return;
  }

  const header = req.headers['authorization'];
  if (header !== `Bearer ${token}`) {
    console.warn('[Auth] Rejected request — invalid token');
    res.status(401).json({ error: 'Unauthorized' });
    return;
  }
  next();
}

// ─── Routes ───────────────────────────────────────────────────────────────────

// Health check — useful for uptime monitors and deployment checks
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Main webhook endpoint — point all Azure DevOps service hooks here
app.post('/webhook/devops', requireAuth, async (req: Request, res: Response) => {
  const payload = req.body as DevOpsWebhookPayload;

  if (!payload?.eventType) {
    res.status(400).json({ error: 'Missing eventType' });
    return;
  }

  // Respond immediately — ADO expects a fast 200 or it will retry
  res.status(200).json({ received: true, eventType: payload.eventType });

  // Process asynchronously so we don't block the response
  routeEvent(payload).catch((err) => {
    console.error('[Webhook] Handler error:', err);
  });
});

// Manual sprint health trigger — useful for scheduled calls (e.g. cron job or Azure Logic App)
// POST /webhook/sprint-health   (no body required)
app.post('/webhook/sprint-health', requireAuth, async (_req: Request, res: Response) => {
  res.status(200).json({ received: true });
  handleSprintHealth().catch((err) => {
    console.error('[SprintHealth] Error:', err);
  });
});

// ─── Start ────────────────────────────────────────────────────────────────────

const PORT = parseInt(process.env.PORT ?? '3000', 10);
app.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════╗
║   DevOps Teams Bot                       ║
╠══════════════════════════════════════════╣
║  POST /webhook/devops    ← ADO hooks     ║
║  POST /webhook/sprint-health ← schedule  ║
║  GET  /health            ← uptime check  ║
╚══════════════════════════════════════════╝
  Listening on port ${PORT}
  `);
});
