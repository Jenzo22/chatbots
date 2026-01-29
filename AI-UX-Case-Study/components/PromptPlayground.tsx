'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, Lightbulb, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PROMPT_TEMPLATES } from '@/lib/ai-client'
import { UncertaintyDisplay } from './UncertaintyDisplay'

export function PromptPlayground() {
  const [prompt, setPrompt] = useState('')
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)
  const [response, setResponse] = useState<{
    text: string
    confidence: number
    latencyMs: number
    modelUsed: string
    hedgingPhrases?: string[]
  } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const template = selectedTemplate
    ? PROMPT_TEMPLATES.find((t) => t.id === selectedTemplate)
    : null

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!prompt.trim() || loading) return

    setLoading(true)
    setError(null)
    setResponse(null)

    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt.trim(),
          systemPrompt: template?.systemPrompt,
          templateId: selectedTemplate,
          sessionId: crypto.randomUUID(),
        }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.error || 'Request failed')
      }

      const data = await res.json()
      setResponse(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-semibold mb-2">
          Prompt Engineering Best Practices
        </h2>
        <p className="text-slate-400 text-sm max-w-2xl">
          Choose a prompt pattern and see how structured prompts improve AI
          responses. Each template demonstrates a different best practice.
        </p>
      </div>

      {/* Template selector - Progressive disclosure of capabilities */}
      <div>
        <label
          htmlFor="template-select"
          className="block text-sm font-medium text-slate-300 mb-2"
        >
          Prompt pattern
        </label>
        <div className="flex flex-wrap gap-2" role="group" aria-labelledby="template-select">
          {PROMPT_TEMPLATES.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setSelectedTemplate((s) => (s === t.id ? null : t.id))}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                'focus-visible:ring-2 focus-visible:ring-ai-500 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950',
                selectedTemplate === t.id
                  ? 'bg-ai-600 text-white'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              )}
              aria-pressed={selectedTemplate === t.id}
            >
              {t.name}
            </button>
          ))}
        </div>

        {template && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-4 p-4 rounded-lg bg-slate-800/50 border border-slate-700"
          >
            <p className="text-sm text-slate-400 mb-2">
              <Lightbulb className="inline w-4 h-4 mr-1" aria-hidden />
              {template.bestPractice}
            </p>
            <div className="text-xs font-mono text-slate-500 space-y-1">
              <p>System: {template.systemPrompt}</p>
              <p>User: {template.userPromptTemplate}</p>
            </div>
          </motion.div>
        )}
      </div>

      {/* Input form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <label htmlFor="prompt-input" className="block text-sm font-medium text-slate-300">
          Your prompt
        </label>
        <textarea
          id="prompt-input"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your prompt..."
          rows={4}
          className={cn(
            'w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700',
            'text-slate-100 placeholder-slate-500',
            'focus:outline-none focus:ring-2 focus:ring-ai-500 focus:border-transparent',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
          disabled={loading}
          aria-describedby="prompt-hint"
          aria-invalid={!!error}
        />
        <p id="prompt-hint" className="text-xs text-slate-500">
          Tip: Include context and be specific for better results.
        </p>

        <button
          type="submit"
          disabled={loading || !prompt.trim()}
          className={cn(
            'flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors',
            'bg-ai-600 hover:bg-ai-500 text-white',
            'focus-visible:ring-2 focus-visible:ring-ai-500 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
          aria-busy={loading}
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" aria-hidden />
              Generating...
            </>
          ) : (
            <>
              <Send className="w-5 h-5" aria-hidden />
              Generate
            </>
          )}
        </button>
      </form>

      {error && (
        <div
          role="alert"
          className="p-4 rounded-lg bg-red-900/20 border border-red-800 text-red-300"
        >
          {error}
        </div>
      )}

      {/* Response with uncertainty display */}
      {response && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <h3 className="text-sm font-medium text-slate-300">Response</h3>
          <UncertaintyDisplay
            text={response.text}
            confidence={response.confidence}
            latencyMs={response.latencyMs}
            modelUsed={response.modelUsed}
            hedgingPhrases={response.hedgingPhrases}
          />
        </motion.div>
      )}
    </div>
  )
}
