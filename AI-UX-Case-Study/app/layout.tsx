import type { Metadata } from 'next'
import { DM_Sans } from 'next/font/google'
import './globals.css'

const dmSans = DM_Sans({
  subsets: ['latin'],
  variable: '--font-dm-sans',
})

export const metadata: Metadata = {
  title: 'AI UX Case Study | Thoughtful AI Interaction Patterns',
  description:
    'A case study showcasing prompt engineering best practices, model uncertainty handling, progressive disclosure, and accessibility-first AI interactions.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={dmSans.variable}>
      <body className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased">
        <main className="min-h-screen">{children}</main>
      </body>
    </html>
  )
}
