// src/types.ts
// Typed representations of Azure DevOps service hook payloads

export type DevOpsEventType =
  | 'workitem.created'       // New bug
  | 'workitem.commented'     // New comment on task
  | 'workitem.updated'       // Work item field change (used for user story review)
  | 'ms.vss-work.sprint-start' // Sprint started (used for health checks)
  | 'build.complete'
  | 'git.pullrequest.created'
  | 'unknown';

export interface DevOpsResource {
  id: number;
  rev?: number;
  url?: string;
  fields?: Record<string, unknown>;
  workItemType?: string;
  title?: string;
  [key: string]: unknown;
}

export interface DevOpsWebhookPayload {
  subscriptionId: string;
  notificationId: number;
  id: string;
  eventType: string;
  publisherId: string;
  message?: { text: string; html: string; markdown: string };
  detailedMessage?: { text: string; html: string; markdown: string };
  resource: DevOpsResource;
  resourceVersion: string;
  resourceContainers: {
    collection?: { id: string; baseUrl?: string };
    account?: { id: string; baseUrl?: string };
    project?: { id: string; baseUrl?: string };
  };
  createdDate: string;
}

// Normalised internal event - what handlers receive
export interface NormalisedEvent {
  type: DevOpsEventType;
  title: string;
  description: string;
  url: string;
  assignedTo?: string;
  createdBy?: string;
  workItemType?: string;
  priority?: string;
  tags?: string[];
  sprintName?: string;
  raw: DevOpsWebhookPayload;
}

// What a formatter returns — ready to POST to Teams
export interface TeamsCard {
  type: 'message';
  attachments: Array<{
    contentType: 'application/vnd.microsoft.card.adaptive';
    content: Record<string, unknown>;
  }>;
}
