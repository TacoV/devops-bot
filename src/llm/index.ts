// src/llm/index.ts
// LLM enrichment layer. Disabled when no provider is configured.
// Supports Anthropic Claude and Azure OpenAI — swap via .env.

import { NormalisedEvent } from '../types';

export type LLMProvider = 'anthropic' | 'azure-openai' | 'none';

interface LLMClient {
  summarise(event: NormalisedEvent): Promise<string>;
  reviewUserStory(event: NormalisedEvent): Promise<string>;
  sprintInsight(context: string): Promise<string>;
}

// ─── Anthropic Client ────────────────────────────────────────────────────────

async function createAnthropicClient(): Promise<LLMClient> {
  const Anthropic = (await import('@anthropic-ai/sdk')).default;
  const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

  async function ask(prompt: string): Promise<string> {
    const msg = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 200,
      system:
        'You are a concise engineering assistant embedded in a Teams notification bot. ' +
        'Reply in 1-2 sentences maximum. Be direct and actionable. No bullet points.',
      messages: [{ role: 'user', content: prompt }],
    });
    return msg.content[0].type === 'text' ? msg.content[0].text : '';
  }

  return {
    summarise: (e) =>
      ask(`Summarise this DevOps event for a developer: "${e.title}". ${e.description}`),
    reviewUserStory: (e) =>
      ask(
        `Review this user story title and flag any obvious gaps or ambiguities: "${e.title}". ` +
        `Description: ${e.description}`,
      ),
    sprintInsight: (context) =>
      ask(`Based on this sprint data, give one actionable insight: ${context}`),
  };
}

// ─── Azure OpenAI Client ─────────────────────────────────────────────────────

async function createAzureOpenAIClient(): Promise<LLMClient> {
  const { AzureOpenAI } = await import('openai');
  const client = new AzureOpenAI({
    endpoint: process.env.AZURE_OPENAI_ENDPOINT!,
    apiKey: process.env.AZURE_OPENAI_API_KEY!,
    deployment: process.env.AZURE_OPENAI_DEPLOYMENT ?? 'gpt-4o',
    apiVersion: '2024-02-01',
  });

  async function ask(prompt: string): Promise<string> {
    const res = await client.chat.completions.create({
      model: process.env.AZURE_OPENAI_DEPLOYMENT ?? 'gpt-4o',
      max_tokens: 200,
      messages: [
        {
          role: 'system',
          content:
            'You are a concise engineering assistant embedded in a Teams notification bot. ' +
            'Reply in 1-2 sentences maximum. Be direct and actionable. No bullet points.',
        },
        { role: 'user', content: prompt },
      ],
    });
    return res.choices[0]?.message?.content ?? '';
  }

  return {
    summarise: (e) =>
      ask(`Summarise this DevOps event for a developer: "${e.title}". ${e.description}`),
    reviewUserStory: (e) =>
      ask(
        `Review this user story title and flag any obvious gaps or ambiguities: "${e.title}". ` +
        `Description: ${e.description}`,
      ),
    sprintInsight: (context) =>
      ask(`Based on this sprint data, give one actionable insight: ${context}`),
  };
}

// ─── No-op Client ────────────────────────────────────────────────────────────

const noopClient: LLMClient = {
  summarise: async () => '',
  reviewUserStory: async () => '',
  sprintInsight: async () => '',
};

// ─── Factory ─────────────────────────────────────────────────────────────────

let _client: LLMClient | null = null;

export async function getLLMClient(): Promise<LLMClient> {
  if (_client) return _client;

  const provider = (process.env.LLM_PROVIDER ?? 'none') as LLMProvider;

  if (provider === 'anthropic' && process.env.ANTHROPIC_API_KEY) {
    console.log('[LLM] Using Anthropic Claude');
    _client = await createAnthropicClient();
  } else if (provider === 'azure-openai' && process.env.AZURE_OPENAI_API_KEY) {
    console.log('[LLM] Using Azure OpenAI');
    _client = await createAzureOpenAIClient();
  } else {
    console.log('[LLM] No provider configured — AI enrichment disabled');
    _client = noopClient;
  }

  return _client;
}
