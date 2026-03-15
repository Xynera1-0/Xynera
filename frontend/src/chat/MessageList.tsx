import { useEffect, useRef } from 'react'
import { useChatStore } from '@/store/chatStore'
import { MessageItem } from './MessageItem'
import { ProcessingIndicator } from './ProcessingIndicator'

export function MessageList() {
  const messages = useChatStore((s) => s.messages)
  const jobStatus = useChatStore((s) => s.jobStatus)
  const error = useChatStore((s) => s.error)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length, jobStatus])

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="max-w-3xl mx-auto space-y-6">
        {messages.map((msg) => (
          <MessageItem
            key={msg.id}
            role={msg.role}
            content={msg.content}
            artifact={msg.artifact}
          />
        ))}

        {(jobStatus === 'queued' || jobStatus === 'processing') && (
          <ProcessingIndicator />
        )}

        {error && (
          <div className="flex justify-start">
            <div className="max-w-2xl pl-8">
              <p className="text-sm text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">
                {error}
              </p>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  )
}
