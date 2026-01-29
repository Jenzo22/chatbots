import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-uncertainty-low'
  if (confidence >= 0.5) return 'text-uncertainty-medium'
  return 'text-uncertainty-high'
}

export function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.8) return 'High confidence'
  if (confidence >= 0.5) return 'Moderate confidence'
  return 'Low confidence'
}
