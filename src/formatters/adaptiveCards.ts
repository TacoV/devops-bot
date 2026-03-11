// src/formatters/adaptiveCards.ts
// Builds Adaptive Card payloads for each DevOps event type.
// These are posted to Teams via the Workflows webhook URL.

import { NormalisedEvent, TeamsCard } from '../types';

// ─── Helpers ────────────────────────────────────────────────────────────────

const COLOURS = {
  bug: 'attention',       // red
  comment: 'accent',      // blue
  userStory: 'good',      // green
  sprint: 'warning',      // yellow
  default: 'default',
} as const;

function priorityBadge(priority: string): string {
  const map: Record<string, string> = { '1': '🔴 P1', '2': '🟠 P2', '3': '🟡 P3', '4': '🟢 P4' };
  return map[priority] ?? `P${priority}`;
}

function wrapCard(body: unknown[], actions: unknown[] = []): TeamsCard {
  return {
    type: 'message',
    attachments: [
      {
        contentType: 'application/vnd.microsoft.card.adaptive',
        content: {
          $schema: 'http://adaptivecards.io/schemas/adaptive-card.json',
          type: 'AdaptiveCard',
          version: '1.4',
          body,
          actions,
        },
      },
    ],
  };
}

function openUrlAction(title: string, url: string) {
  return { type: 'Action.OpenUrl', title, url };
}

// ─── Bug Created ────────────────────────────────────────────────────────────

export function bugCreatedCard(event: NormalisedEvent, aiSummary?: string): TeamsCard {
  const body: unknown[] = [
    {
      type: 'TextBlock',
      text: '🐛 New Bug Reported',
      weight: 'Bolder',
      size: 'Medium',
      color: COLOURS.bug,
    },
    {
      type: 'TextBlock',
      text: event.title,
      weight: 'Bolder',
      wrap: true,
    },
    {
      type: 'FactSet',
      facts: [
        { title: 'Priority', value: event.priority ? priorityBadge(event.priority) : 'Not set' },
        { title: 'Assigned to', value: event.assignedTo || 'Unassigned' },
        { title: 'Sprint', value: event.sprintName || 'Backlog' },
        ...(event.tags?.length ? [{ title: 'Tags', value: event.tags.join(', ') }] : []),
      ],
    },
  ];

  if (aiSummary) {
    body.push({
      type: 'TextBlock',
      text: `💡 ${aiSummary}`,
      wrap: true,
      isSubtle: true,
      spacing: 'Medium',
    });
  }

  return wrapCard(body, event.url ? [openUrlAction('View Bug', event.url)] : []);
}

// ─── Comment Added ───────────────────────────────────────────────────────────

export function commentAddedCard(event: NormalisedEvent, aiSummary?: string): TeamsCard {
  const commentText =
    (event.raw.resource as { comment?: { text?: string } }).comment?.text ?? event.description;

  const body: unknown[] = [
    {
      type: 'TextBlock',
      text: '💬 New Comment on Task',
      weight: 'Bolder',
      size: 'Medium',
      color: COLOURS.comment,
    },
    { type: 'TextBlock', text: event.title, weight: 'Bolder', wrap: true },
    {
      type: 'FactSet',
      facts: [
        { title: 'By', value: event.createdBy || 'Unknown' },
        { title: 'Sprint', value: event.sprintName || 'Backlog' },
      ],
    },
    {
      type: 'TextBlock',
      text: commentText || '(no text)',
      wrap: true,
      spacing: 'Medium',
      isSubtle: true,
    },
  ];

  if (aiSummary) {
    body.push({
      type: 'TextBlock',
      text: `💡 ${aiSummary}`,
      wrap: true,
      isSubtle: true,
      spacing: 'Small',
    });
  }

  return wrapCard(body, event.url ? [openUrlAction('View Task', event.url)] : []);
}

// ─── User Story Needs Review ─────────────────────────────────────────────────

export function userStoryReviewCard(event: NormalisedEvent, aiSummary?: string): TeamsCard {
  const state = getField(event.raw.resource.fields, 'System.State');
  const acceptanceCriteria = getField(
    event.raw.resource.fields,
    'Microsoft.VSTS.Common.AcceptanceCriteria',
  );

  const body: unknown[] = [
    {
      type: 'TextBlock',
      text: '📋 User Story Ready for Review',
      weight: 'Bolder',
      size: 'Medium',
      color: COLOURS.userStory,
    },
    { type: 'TextBlock', text: event.title, weight: 'Bolder', wrap: true },
    {
      type: 'FactSet',
      facts: [
        { title: 'State', value: state || 'Unknown' },
        { title: 'Assigned to', value: event.assignedTo || 'Unassigned' },
        { title: 'Sprint', value: event.sprintName || 'Backlog' },
        { title: 'Priority', value: event.priority ? priorityBadge(event.priority) : 'Not set' },
      ],
    },
  ];

  if (acceptanceCriteria) {
    body.push(
      { type: 'TextBlock', text: '**Acceptance Criteria**', wrap: true, spacing: 'Medium' },
      { type: 'TextBlock', text: acceptanceCriteria, wrap: true, isSubtle: true },
    );
  }

  if (aiSummary) {
    body.push({
      type: 'TextBlock',
      text: `💡 AI Review Notes: ${aiSummary}`,
      wrap: true,
      color: 'accent',
      spacing: 'Medium',
    });
  }

  return wrapCard(body, event.url ? [openUrlAction('Review Story', event.url)] : []);
}

// ─── Sprint Health ────────────────────────────────────────────────────────────

export interface SprintHealthData {
  sprintName: string;
  totalItems: number;
  done: number;
  inProgress: number;
  notStarted: number;
  bugs: number;
  velocityPercent: number;
  daysRemaining: number;
}

export function sprintHealthCard(data: SprintHealthData, aiSummary?: string): TeamsCard {
  const healthColor =
    data.velocityPercent >= 70 ? COLOURS.userStory :
    data.velocityPercent >= 40 ? COLOURS.sprint :
    COLOURS.bug;

  const progressBar = buildProgressBar(data.velocityPercent);

  const body: unknown[] = [
    {
      type: 'TextBlock',
      text: `📊 Sprint Health — ${data.sprintName}`,
      weight: 'Bolder',
      size: 'Medium',
      color: healthColor,
    },
    {
      type: 'TextBlock',
      text: progressBar,
      fontType: 'Monospace',
      spacing: 'Small',
    },
    {
      type: 'FactSet',
      facts: [
        { title: '✅ Done', value: String(data.done) },
        { title: '🔄 In Progress', value: String(data.inProgress) },
        { title: '⏳ Not Started', value: String(data.notStarted) },
        { title: '🐛 Open Bugs', value: String(data.bugs) },
        { title: '📅 Days Remaining', value: String(data.daysRemaining) },
        { title: '🚀 Velocity', value: `${data.velocityPercent}%` },
      ],
    },
  ];

  if (aiSummary) {
    body.push({
      type: 'TextBlock',
      text: `💡 ${aiSummary}`,
      wrap: true,
      color: 'accent',
      spacing: 'Medium',
    });
  }

  return wrapCard(body);
}

// ─── Utils ───────────────────────────────────────────────────────────────────

function buildProgressBar(percent: number): string {
  const filled = Math.round(percent / 10);
  const empty = 10 - filled;
  return `${'█'.repeat(filled)}${'░'.repeat(empty)} ${percent}%`;
}

function getField(fields: unknown, key: string): string {
  if (!fields || typeof fields !== 'object') return '';
  const val = (fields as Record<string, unknown>)[key];
  if (typeof val === 'string') return val;
  if (val && typeof val === 'object' && 'displayName' in val) {
    return (val as { displayName: string }).displayName;
  }
  return '';
}
