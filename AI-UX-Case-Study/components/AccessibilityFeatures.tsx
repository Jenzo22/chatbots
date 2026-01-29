'use client'

import { motion } from 'framer-motion'
import {
  Keyboard,
  Eye,
  Volume2,
  Focus,
  CheckCircle2,
} from 'lucide-react'

/**
 * Accessibility-First AI Interactions
 * Decision: AI interfaces must work for everyone.
 * Document and demonstrate WCAG-aligned patterns.
 */

const FEATURES = [
  {
    icon: Keyboard,
    title: 'Keyboard navigation',
    description: 'All interactive elements are focusable and operable via keyboard. Tab through sections, Enter to expand.',
  },
  {
    icon: Focus,
    title: 'Visible focus indicators',
    description: 'Focus rings (2px outline) on :focus-visible. Never remove focus outline—it\'s critical for keyboard users.',
  },
  {
    icon: Volume2,
    title: 'Screen reader support',
    description: 'ARIA labels, live regions for dynamic content, role="alert" for errors. Response announced via aria-live.',
  },
  {
    icon: Eye,
    title: 'Reduced motion',
    description: 'Respects prefers-reduced-motion. Animations disabled for users who prefer less motion.',
  },
  {
    icon: CheckCircle2,
    title: 'High contrast',
    description: 'Supports prefers-contrast for users who need higher contrast. Semantic color usage.',
  },
]

export function AccessibilityFeatures() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-semibold mb-2">
          Accessibility-First AI Interactions
        </h2>
        <p className="text-slate-400 text-sm max-w-2xl">
          AI interfaces must work for everyone. These patterns ensure keyboard
          users, screen reader users, and users with motion sensitivity can
          interact effectively.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {FEATURES.map(({ icon: Icon, title, description }, i) => (
          <motion.div
            key={title}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="p-4 rounded-lg bg-slate-800/50 border border-slate-700"
          >
            <div className="flex items-start gap-3">
              <Icon className="w-5 h-5 text-ai-400 flex-shrink-0 mt-0.5" aria-hidden />
              <div>
                <h3 className="font-medium text-slate-200">{title}</h3>
                <p className="text-sm text-slate-400 mt-1">{description}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="p-4 rounded-lg bg-slate-800/30 border border-slate-700">
        <h3 className="font-medium text-slate-200 mb-2">Try it</h3>
        <ul className="text-sm text-slate-400 space-y-1 list-disc list-inside">
          <li>Tab through the section tabs above—each is focusable</li>
          <li>Use Enter/Space to expand sections</li>
          <li>Focus the Generate button and submit with Enter</li>
          <li>Errors are announced via role="alert"</li>
        </ul>
      </div>
    </div>
  )
}
