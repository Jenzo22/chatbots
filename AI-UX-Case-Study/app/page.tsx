'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Sparkles,
  ChevronDown,
  Accessibility,
  Lightbulb,
  AlertCircle,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { PROMPT_TEMPLATES } from '@/lib/ai-client'
import { PromptPlayground } from '@/components/PromptPlayground'
import { UncertaintyDisplay } from '@/components/UncertaintyDisplay'
import { ProgressiveDisclosure } from '@/components/ProgressiveDisclosure'
import { AccessibilityFeatures } from '@/components/AccessibilityFeatures'

type Section = 'playground' | 'uncertainty' | 'disclosure' | 'accessibility'

export default function HomePage() {
  const [expandedSection, setExpandedSection] = useState<Section | null>(
    'playground'
  )

  const sections: { id: Section; title: string; icon: React.ReactNode }[] = [
    { id: 'playground', title: 'Prompt Engineering Playground', icon: <Lightbulb className="w-5 h-5" /> },
    { id: 'uncertainty', title: 'Model Uncertainty Handling', icon: <AlertCircle className="w-5 h-5" /> },
    { id: 'disclosure', title: 'Progressive Disclosure', icon: <ChevronDown className="w-5 h-5" /> },
    { id: 'accessibility', title: 'Accessibility-First AI', icon: <Accessibility className="w-5 h-5" /> },
  ]

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="max-w-5xl mx-auto px-6 py-12">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="w-8 h-8 text-ai-400" aria-hidden />
            <h1 className="text-3xl font-bold tracking-tight">
              AI UX Case Study
            </h1>
          </div>
          <p className="text-slate-400 text-lg max-w-2xl">
            Thoughtful AI interaction patterns: prompt engineering, uncertainty
            handling, progressive disclosure, and accessibility-first design.
          </p>
        </div>
      </header>

      {/* Section navigation - Progressive disclosure entry points */}
      <nav
        className="border-b border-slate-800"
        aria-label="AI UX pattern sections"
      >
        <div className="max-w-5xl mx-auto px-6">
          <ul className="flex flex-wrap gap-1">
            {sections.map(({ id, title, icon }) => (
              <li key={id}>
                <button
                  onClick={() =>
                    setExpandedSection((s) => (s === id ? null : id))
                  }
                  className={cn(
                    'flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors',
                    'hover:bg-slate-800/50 focus-visible:ring-2 focus-visible:ring-ai-500 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950',
                    expandedSection === id
                      ? 'text-ai-400 bg-slate-800/80 border-b-2 border-ai-500'
                      : 'text-slate-400 hover:text-slate-200'
                  )}
                  aria-expanded={expandedSection === id}
                  aria-controls={`section-${id}`}
                  id={`tab-${id}`}
                >
                  {icon}
                  {title}
                </button>
              </li>
            ))}
          </ul>
        </div>
      </nav>

      {/* Content sections */}
      <div className="max-w-5xl mx-auto px-6 py-12">
        <AnimatePresence mode="wait">
          {expandedSection === 'playground' && (
            <motion.section
              key="playground"
              id="section-playground"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              aria-labelledby="tab-playground"
            >
              <PromptPlayground />
            </motion.section>
          )}
          {expandedSection === 'uncertainty' && (
            <motion.section
              key="uncertainty"
              id="section-uncertainty"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              aria-labelledby="tab-uncertainty"
            >
              <UncertaintyDisplay />
            </motion.section>
          )}
          {expandedSection === 'disclosure' && (
            <motion.section
              key="disclosure"
              id="section-disclosure"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              aria-labelledby="tab-disclosure"
            >
              <ProgressiveDisclosure />
            </motion.section>
          )}
          {expandedSection === 'accessibility' && (
            <motion.section
              key="accessibility"
              id="section-accessibility"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              aria-labelledby="tab-accessibility"
            >
              <AccessibilityFeatures />
            </motion.section>
          )}
        </AnimatePresence>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-800 mt-24 py-8">
        <div className="max-w-5xl mx-auto px-6 text-center text-slate-500 text-sm">
          <p>
            AI UX Case Study — Demonstrating thoughtful AI interaction patterns.
            See README for architecture, metrics, and deployment.
          </p>
        </div>
      </footer>
    </div>
  )
}
