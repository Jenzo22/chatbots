'use client'

import { motion } from 'framer-motion'
import { AlertTriangle, Clock, Cpu } from 'lucide-react'
import { cn, getConfidenceColor, getConfidenceLabel } from '@/lib/utils'

interface UncertaintyDisplayProps {
  text: string
  confidence: number
  latencyMs: number
  modelUsed: string
  hedgingPhrases?: string[]
}

export function UncertaintyDisplay({
  text,
  confidence,
  latencyMs,
  modelUsed,
  hedgingPhrases = [],
}: UncertaintyDisplayProps) {
  const confidenceLabel = getConfidenceLabel(confidence)
  const confidenceColor = getConfidenceColor(confidence)
  const showUncertaintyBanner = confidence < 0.8 || hedgingPhrases.length > 0

  return (
    <div className="space-y-4">
      {/* Main response */}
      <div
        className="p-4 rounded-lg bg-slate-800/50 border border-slate-700"
        role="article"
        aria-label="AI response"
      >
        <p className="text-slate-200 whitespace-pre-wrap">{text}</p>
      </div>

      {/* Uncertainty banner - shown when model expresses doubt */}
      {showUncertaintyBanner && (
        <motion.div
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          role="status"
          aria-live="polite"
          className={cn(
            'flex items-start gap-3 p-4 rounded-lg border',
            confidence < 0.5
              ? 'bg-amber-900/20 border-amber-800'
              : 'bg-slate-800/50 border-slate-700'
          )}
        >
          <AlertTriangle
            className={cn(
              'w-5 h-5 flex-shrink-0 mt-0.5',
              confidence < 0.5 ? 'text-amber-500' : 'text-slate-500'
            )}
            aria-hidden
          />
          <div>
            <p className="font-medium text-slate-200">
              {confidenceLabel}
            </p>
            <p className="text-sm text-slate-400 mt-1">
              {confidence < 0.5
                ? 'Consider verifying this response or providing more context.'
                : 'This response may vary depending on context.'}
            </p>
            {hedgingPhrases.length > 0 && (
              <p className="text-xs text-slate-500 mt-2">
                Detected hedging: {hedgingPhrases.join(', ')}
              </p>
            )}
          </div>
        </motion.div>
      )}

      {/* Metrics - latency, model, confidence */}
      <div
        className="flex flex-wrap gap-4 text-sm text-slate-500"
        role="group"
        aria-label="Response metrics"
      >
        <span className="flex items-center gap-1.5">
          <Clock className="w-4 h-4" aria-hidden />
          {latencyMs}ms latency
        </span>
        <span className="flex items-center gap-1.5">
          <Cpu className="w-4 h-4" aria-hidden />
          {modelUsed}
        </span>
        <span className={cn('flex items-center gap-1.5', confidenceColor)}>
          {(confidence * 100).toFixed(0)}% confidence
        </span>
      </div>
    </div>
  )
}
