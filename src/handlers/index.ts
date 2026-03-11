// src/handlers/index.ts
// One handler per DevOps event type.
// Each handler: normalises → optionally enriches via LLM → formats card → posts to Teams.

import { DevOpsWebhookPayload, NormalisedEvent } from '../types';
import { normalise } from '../utils/normalise';
import { postToTeams } from '../utils/teams';
import { getLLMClient } from '../llm';
import {
  bugCreatedCard,
  commentAddedCard,
  userStoryReviewCard,
  sprintHealthCard,
  SprintHealthData,
} from '../formatters/adaptiveCards';

// ─── Bug Created ─────────────────────────────────────────────────────────────

export async function handleBugCreated(payload: DevOpsWebhookPayload): Promise<void> {
  const event = normalise(payload);
  const llm = await getLLMClient();
  const aiSummary = await llm.summarise(event).catch(() => '');
  const card = bugCreatedCard(event, aiSummary);
  await postToTeams(card);
  console.log(`[Handler] Bug created: ${event.title}`);
}

// ─── Comment Added ────────────────────────────────────────────────────────────

export async function handleCommentAdded(payload: DevOpsWebhookPayload): Promise<void> {
  const event = normalise(payload);
  const llm = await getLLMClient();
  const aiSummary = await llm.summarise(event).catch(() => '');
  const card = commentAddedCard(event, aiSummary);
  await postToTeams(card);
  console.log(`[Handler] Comment added on: ${event.title}`);
}

// ─── User Story Review ────────────────────────────────────────────────────────
// Triggered when a work item of type "User Story" moves to state "In Review"

export async function handleUserStoryReview(payload: DevOpsWebhookPayload): Promise<void> {
  const event = normalise(payload);

  // Only fire for User Stories entering a review state
  const fields = (event.raw.resource.fields ?? {}) as Record<string, unknown>;
  const workItemType = String(fields['System.WorkItemType'] ?? '');
  const newState = String(
    (fields['System.State'] as { newValue?: string } | undefined)?.newValue ??
    fields['System.State'] ?? '',
  );

  const isUserStory = workItemType === 'User Story';
  const isReviewState = ['In Review', 'Ready for Review', 'Review'].includes(newState);

  if (!isUserStory || !isReviewState) {
    console.log(`[Handler] Skipping workitem.updated — not a user story review (${workItemType} / ${newState})`);
    return;
  }

  const llm = await getLLMClient();
  const aiSummary = await llm.reviewUserStory(event).catch(() => '');
  const card = userStoryReviewCard(event, aiSummary);
  await postToTeams(card);
  console.log(`[Handler] User story review: ${event.title}`);
}

// ─── Sprint Health ────────────────────────────────────────────────────────────
// Called on a schedule (see index.ts) or triggered by sprint-start hook

export async function handleSprintHealth(payload?: DevOpsWebhookPayload): Promise<void> {
  // In a real implementation you'd query the ADO REST API here to get live sprint stats.
  // The payload (if present) just tells us a sprint started.
  // For now we post a placeholder — replace fetchSprintData() with a real ADO query.

  const sprintName = payload
    ? String((payload.resource as { name?: string }).name ?? 'Current Sprint')
    : 'Current Sprint';

  const data = await fetchSprintData(sprintName);
  const llm = await getLLMClient();
  const aiSummary = await llm
    .sprintInsight(JSON.stringify(data))
    .catch(() => '');

  const card = sprintHealthCard(data, aiSummary);
  await postToTeams(card);
  console.log(`[Handler] Sprint health posted for: ${sprintName}`);
}

// ─── Sprint Data Fetcher (stub — replace with real ADO REST calls) ────────────

async function fetchSprintData(sprintName: string): Promise<SprintHealthData> {
  // TODO: Replace with Azure DevOps REST API calls:
  //   GET {org}/{project}/_apis/work/teamsettings/iterations?$timeframe=current
  //   GET {org}/{project}/_apis/wit/wiql  (query work items in sprint)
  //
  // See: https://learn.microsoft.com/en-us/rest/api/azure/devops/work/iterations

  return {
    sprintName,
    totalItems: 0,
    done: 0,
    inProgress: 0,
    notStarted: 0,
    bugs: 0,
    velocityPercent: 0,
    daysRemaining: 0,
  };
}

// ─── Router ───────────────────────────────────────────────────────────────────

export async function routeEvent(payload: DevOpsWebhookPayload): Promise<void> {
  switch (payload.eventType) {
    case 'workitem.created': {
      const fields = (payload.resource.fields ?? {}) as Record<string, unknown>;
      const type = String(fields['System.WorkItemType'] ?? '');
      if (type === 'Bug') {
        await handleBugCreated(payload);
      }
      // Add other work item types here as needed
      break;
    }
    case 'workitem.commented':
      await handleCommentAdded(payload);
      break;
    case 'workitem.updated':
      await handleUserStoryReview(payload);
      break;
    case 'ms.vss-work.sprint-start':
      await handleSprintHealth(payload);
      break;
    default:
      console.log(`[Router] Unhandled event type: ${payload.eventType}`);
  }
}
