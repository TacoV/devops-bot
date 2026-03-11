// src/utils/teams.ts
// Posts Adaptive Cards to Teams via the Workflows webhook URL.

import axios from 'axios';
import { TeamsCard } from '../types';

export async function postToTeams(card: TeamsCard): Promise<void> {
  const webhookUrl = process.env.TEAMS_WEBHOOK_URL;
  if (!webhookUrl) {
    console.warn('[Teams] TEAMS_WEBHOOK_URL not set — skipping post');
    return;
  }

  try {
    const response = await axios.post(webhookUrl, card, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 10_000,
    });
    console.log(`[Teams] Posted successfully — HTTP ${response.status}`);
  } catch (err) {
    if (axios.isAxiosError(err)) {
      console.error('[Teams] Failed to post:', err.response?.status, err.response?.data);
    } else {
      console.error('[Teams] Unexpected error:', err);
    }
    throw err;
  }
}
