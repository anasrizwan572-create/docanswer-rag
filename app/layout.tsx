import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'DocAnswer — Trust-First Document Q&A Assistant',
  description: 'Grounded plain-language answers with exact verified source passages for professionals.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased selection:bg-sky-100 selection:text-sky-900">{children}</body>
    </html>
  )
}
