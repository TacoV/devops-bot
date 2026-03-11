// src/utils/normalise.ts
// Converts raw Azure DevOps webhook payloads into a clean NormalisedEvent

import {
  DevOpsWebhookPayload,
  DevOpsEventType,
  NormalisedEvent,
} from '../types';

function getField(fields: Record<string, unknown>, key: string): string {
  const val = fields[key];
  if (typeof val === 'string') return val;
  if (val && typeof val === 'object' && 'displayName' in val) {
    return (val as { displayName: string }).displayName;
  }
  return '';
}

function resolveEventType(raw: string): DevOpsEventType {
  const map: Record<string, DevOpsEventType> = {
    'workitem.created': 'workitem.created',
    'workitem.commented': 'workitem.commented',
    'workitem.updated': 'workitem.updated',
    'ms.vss-work.sprint-start': 'ms.vss-work.sprint-start',
    'build.complete': 'build.complete',
    'git.pullrequest.created': 'git.pullrequest.created',
  };
  return map[raw] ?? 'unknown';
}

export function normalise(payload: DevOpsWebhookPayload): NormalisedEvent {
  const { resource, eventType, resourceContainers } = payload;
  const fields = (resource.fields ?? {}) as Record<string, unknown>;

  const projectBaseUrl =
    resourceContainers.project?.baseUrl ??
    resourceContainers.account?.baseUrl ??
    '';

  const workItemId = resource.id;
  const workItemUrl = resource.url
    ? `${projectBaseUrl}_workitems/edit/${workItemId}`
    : '';

  const title =
    getField(fields, 'System.Title') ||
    (resource.title as string) ||
    payload.message?.text ||
    'No title';

  const description =
    getField(fields, 'System.Description') ||
    payload.detailedMessage?.text ||
    '';

  const tags = getField(fields, 'System.Tags')
    ? getField(fields, 'System.Tags').split(';').map((t) => t.trim())
    : [];

  return {
    type: resolveEventType(eventType),
    title,
    description,
    url: workItemUrl,
    assignedTo: getField(fields, 'System.AssignedTo'),
    createdBy: getField(fields, 'System.CreatedBy'),
    workItemType: getField(fields, 'System.WorkItemType'),
    priority: getField(fields, 'Microsoft.VSTS.Common.Priority'),
    tags,
    sprintName: getField(fields, 'System.IterationPath'),
    raw: payload,
  };
}
