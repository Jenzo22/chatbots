'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronRight, ChevronDown, Sparkles, Zap, Shield } from 'lucide-react'
import { cn } from '@/lib/utils'

/**
 * Progressive Disclosure - Reveal AI capabilities gradually.
 * Decision: Don't overwhelm users with all features at once.
 * Start simple, expand on demand.
 */

const CAPABILITY_LEVELS = [
  {
    id: 'basic',
    title: 'Basic',
    description: 'Simple text generation',
    icon: Sparkles,
    features: ['Single-turn Q&A', 'Plain text output'],
  },
  {
    id: 'intermediate',
    title: 'Intermediate',
    description: 'Structured prompts & uncertainty',
    icon: Zap,
    features: [
      'Prompt templates',
      'Confidence scores',
      'Hedging detection',
      'Latency metrics',
    ],
  },
  {
    id: 'advanced',
    title: 'Advanced',
    description: 'Full AI UX patterns',
    icon: Shield,
    features: [
      'Progressive disclosure',
      'Accessibility-first',
      'BigQuery metrics',
      'Vertex AI integration',
    ],
  },
]

export function ProgressiveDisclosure() {
  const [expandedId, setExpandedId] = useState<string | null>('basic')

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-semibold mb-2">
          Progressive Disclosure of AI Capabilities
        </h2>
        <p className="text-slate-400 text-sm max-w-2xl">
          Reveal features gradually instead of overwhelming users. Start with
          the simplest interaction, then expand as users explore.
        </p>
      </div>

      <div className="space-y-2" role="list">
        {CAPABILITY_LEVELS.map((level) => {
          const Icon = level.icon
          const isExpanded = expandedId === level.id

          return (
            <div
              key={level.id}
              className="rounded-lg border border-slate-700 bg-slate-800/30 overflow-hidden"
              role="listitem"
            >
              <button
                onClick={() =>
                  setExpandedId((s) => (s === level.id ? null : level.id))
                }
                className={cn(
                  'w-full flex items-center gap-4 px-4 py-4 text-left',
                  'hover:bg-slate-800/50 focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ai-500',
                  'transition-colors'
                )}
                aria-expanded={isExpanded}
                aria-controls={`content-${level.id}`}
                id={`header-${level.id}`}
              >
                <Icon className="w-5 h-5 text-ai-400 flex-shrink-0" aria-hidden />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-slate-200">{level.title}</p>
                  <p className="text-sm text-slate-500 truncate">
                    {level.description}
                  </p>
                </div>
                {isExpanded ? (
                  <ChevronDown className="w-5 h-5 text-slate-500 flex-shrink-0" aria-hidden />
                ) : (
                  <ChevronRight className="w-5 h-5 text-slate-500 flex-shrink-0" aria-hidden />
                )}
              </button>

              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    id={`content-${level.id}`}
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                    aria-labelledby={`header-${level.id}`}
                  >
                    <div className="px-4 pb-4 pt-0">
                      <ul className="space-y-2 pl-9" role="list">
                        {level.features.map((feature) => (
                          <li
                            key={feature}
                            className="text-sm text-slate-400 flex items-center gap-2"
                          >
                            <span className="w-1.5 h-1.5 rounded-full bg-ai-500" aria-hidden />
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )
        })}
      </div>

      <div className="p-4 rounded-lg bg-slate-800/30 border border-slate-700">
        <p className="text-sm text-slate-400">
          <strong className="text-slate-300">Design decision:</strong> Users
          land on the Prompt Playground first. Uncertainty handling and
          progressive disclosure are revealed as they interact. This reduces
          cognitive load and lets users discover capabilities at their own pace.
        </p>
      </div>
    </div>
  )
}
