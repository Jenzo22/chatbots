/**
 * AI Client - Abstracts Vertex AI with mock fallback for local development.
 * Decision: Use abstraction layer so we can switch between Vertex AI (prod) and mock (dev)
 * without changing UI code. Enables reproducible local runs without GCP credentials.
 */

export interface AIResponse {
  text: string
  confidence: number
  latencyMs: number
  modelUsed: string
  hedgingPhrases?: string[]
}

export interface PromptTemplate {
  id: string
  name: string
  systemPrompt: string
  userPromptTemplate: string
  bestPractice: string
}

export const PROMPT_TEMPLATES: PromptTemplate[] = [
  {
    id: 'role-context',
    name: 'Role + Context',
    systemPrompt: 'You are a helpful assistant with expertise in [domain].',
    userPromptTemplate: 'Given [context], help me with [task].',
    bestPractice: 'Setting role and context improves relevance and reduces hallucination.',
  },
  {
    id: 'few-shot',
    name: 'Few-Shot Examples',
    systemPrompt: 'Classify sentiment. Examples: "Great product!" → positive, "Terrible" → negative.',
    userPromptTemplate: 'Classify: "[user input]"',
    bestPractice: 'Examples teach the model the exact format you want.',
  },
  {
    id: 'chain-of-thought',
    name: 'Chain of Thought',
    systemPrompt: 'Think step by step. Show your reasoning before giving the final answer.',
    userPromptTemplate: '[complex problem]',
    bestPractice: 'Explicit reasoning improves accuracy on multi-step tasks.',
  },
  {
    id: 'constraints',
    name: 'Output Constraints',
    systemPrompt: 'Respond in JSON only. Keys: summary (string), confidence (0-1).',
    userPromptTemplate: 'Summarize: [text]',
    bestPractice: 'Constraints ensure parseable, structured output.',
  },
]

// Hedging phrases that indicate model uncertainty (for UX display)
const HEDGING_PHRASES = [
  'it depends', 'might', 'could', 'possibly', 'perhaps', 'generally',
  'usually', 'typically', 'I think', 'I believe', 'in my opinion',
  'not entirely sure', 'uncertain', 'may vary', 'could be',
]

function detectHedging(text: string): string[] {
  const lower = text.toLowerCase()
  return HEDGING_PHRASES.filter((phrase) => lower.includes(phrase))
}

/**
 * Mock AI for local development - simulates latency and confidence.
 * Enables full UX testing without GCP credentials.
 */
async function mockGenerate(
  prompt: string,
  systemPrompt?: string
): Promise<AIResponse> {
  const start = Date.now()
  await new Promise((r) => setTimeout(r, 800 + Math.random() * 400))

  const hedging = detectHedging(prompt)
  const baseConfidence = 0.6 + Math.random() * 0.35
  const confidence = hedging.length > 0 ? Math.min(baseConfidence - 0.1, 0.85) : baseConfidence

  const mockResponses = [
    `Based on your input, here's a thoughtful response. ${hedging.length ? 'The answer may vary depending on context.' : ''}`,
    `I've analyzed your request. Here are my findings with the considerations you mentioned.`,
    `Taking into account the details provided, I recommend the following approach.`,
  ]

  const text = mockResponses[Math.floor(Math.random() * mockResponses.length)]
  const hedgingFound = detectHedging(text)

  return {
    text,
    confidence,
    latencyMs: Date.now() - start,
    modelUsed: 'mock-local',
    hedgingPhrases: hedgingFound.length > 0 ? hedgingFound : undefined,
  }
}

/**
 * Vertex AI integration - uses @google-cloud/vertexai when GCP is configured.
 * Set GOOGLE_CLOUD_PROJECT and GOOGLE_APPLICATION_CREDENTIALS for production.
 */
async function vertexGenerate(
  prompt: string,
  systemPrompt?: string
): Promise<AIResponse> {
  const start = Date.now()
  const { VertexAI } = await import('@google-cloud/vertexai')

  const projectId = process.env.GOOGLE_CLOUD_PROJECT
  const location = process.env.VERTEX_AI_LOCATION || 'us-central1'
  const model = process.env.VERTEX_AI_MODEL || 'gemini-1.5-flash-001'

  const vertex = new VertexAI({ project: projectId, location })
  const generativeModel = vertex.getGenerativeModel({
    model,
    generationConfig: { maxOutputTokens: 1024, temperature: 0.7 },
    systemInstruction: systemPrompt
      ? { role: 'system', parts: [{ text: systemPrompt }] }
      : undefined,
  })

  const result = await generativeModel.generateContent({
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
  })

  const response = result.response
  const text = response.candidates?.[0]?.content?.parts?.[0]?.text ?? 'No response generated.'
  const latencyMs = Date.now() - start

  // Vertex AI doesn't provide confidence; estimate from response length and hedging
  const hedgingFound = detectHedging(text)
  const confidence = hedgingFound.length > 0 ? 0.65 : 0.85

  return {
    text,
    confidence,
    latencyMs,
    modelUsed: model,
    hedgingPhrases: hedgingFound.length > 0 ? hedgingFound : undefined,
  }
}

export async function generateResponse(
  prompt: string,
  systemPrompt?: string
): Promise<AIResponse> {
  const useVertex = !!(
    process.env.GOOGLE_CLOUD_PROJECT &&
    process.env.GOOGLE_APPLICATION_CREDENTIALS
  )

  if (useVertex) {
    return vertexGenerate(prompt, systemPrompt)
  }
  return mockGenerate(prompt, systemPrompt)
}
