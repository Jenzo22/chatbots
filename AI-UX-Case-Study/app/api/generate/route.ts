import { NextRequest, NextResponse } from 'next/server'
import { generateResponse } from '@/lib/ai-client'
import { recordInteraction } from '@/lib/metrics'

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const { prompt, systemPrompt, templateId, sessionId } = body

    if (!prompt || typeof prompt !== 'string') {
      return NextResponse.json(
        { error: 'prompt is required and must be a string' },
        { status: 400 }
      )
    }

    const response = await generateResponse(prompt, systemPrompt)

    await recordInteraction({
      timestamp: new Date().toISOString(),
      promptLength: prompt.length,
      responseLength: response.text.length,
      latencyMs: response.latencyMs,
      confidence: response.confidence,
      modelUsed: response.modelUsed,
      templateId,
      hasHedging: (response.hedgingPhrases?.length ?? 0) > 0,
      sessionId: sessionId || 'anonymous',
    })

    return NextResponse.json(response)
  } catch (err) {
    console.error('[API] generate error:', err)
    return NextResponse.json(
      { error: 'Failed to generate response' },
      { status: 500 }
    )
  }
}
