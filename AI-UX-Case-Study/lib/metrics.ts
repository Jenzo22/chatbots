/**
 * Metrics - BigQuery integration for latency, accuracy, cost tracking.
 * Decision: Centralize metrics so we can analyze UX patterns and model performance.
 * Falls back to console.log when BigQuery is not configured (local dev).
 */

export interface InteractionMetric {
  timestamp: string
  promptLength: number
  responseLength: number
  latencyMs: number
  confidence: number
  modelUsed: string
  templateId?: string
  hasHedging: boolean
  sessionId: string
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let bigQueryClient: any = null

async function initBigQuery() {
  if (bigQueryClient) return bigQueryClient
  try {
    const { BigQuery } = await import('@google-cloud/bigquery')
    bigQueryClient = new BigQuery({
      projectId: process.env.GOOGLE_CLOUD_PROJECT,
    })
    return bigQueryClient
  } catch {
    return null
  }
}

export async function recordInteraction(metric: InteractionMetric): Promise<void> {
  const dataset = process.env.BIGQUERY_DATASET || 'ai_ux_metrics'
  const table = process.env.BIGQUERY_TABLE || 'interactions'

  const client = await initBigQuery()
  if (client && process.env.GOOGLE_CLOUD_PROJECT) {
    try {
      const row = {
        insertId: `${metric.sessionId}-${metric.timestamp}-${Math.random().toString(36).slice(2)}`,
        json: {
          timestamp: metric.timestamp,
          prompt_length: metric.promptLength,
          response_length: metric.responseLength,
          latency_ms: metric.latencyMs,
          confidence: metric.confidence,
          model_used: metric.modelUsed,
          template_id: metric.templateId ?? null,
          has_hedging: metric.hasHedging,
          session_id: metric.sessionId,
        },
      }
      await client.dataset(dataset).table(table).insert([row])
    } catch (err) {
      console.error('[Metrics] BigQuery insert failed:', err)
    }
  } else {
    console.log('[Metrics]', JSON.stringify(metric))
  }
}
