import { useState, type FormEvent, type KeyboardEvent } from 'react'

interface Props {
  onSend: (query: string) => void
  disabled?: boolean
}

export function MessageInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState('')

  function handleSubmit(e?: FormEvent) {
    e?.preventDefault()
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="border-t border-gray-800 px-4 py-4">
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto flex items-end gap-3">
        <textarea
          rows={1}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask an intelligence question..."
          disabled={disabled}
          className="input-field resize-none flex-1 max-h-40 overflow-y-auto"
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="btn-primary shrink-0 h-9"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
            <path d="M3.105 2.288a.75.75 0 0 0-.826.95l1.903 6.308H9.5a.75.75 0 0 1 0 1.5H4.182l-1.903 6.308a.75.75 0 0 0 .826.95 28.897 28.897 0 0 0 15.208-7.757.75.75 0 0 0 0-1.502A28.897 28.897 0 0 0 3.105 2.288Z" />
          </svg>
        </button>
      </form>
      <p className="text-center text-xs text-gray-600 mt-2">
        Analysis may take 20-40 s while agents gather live signals.
      </p>
    </div>
  )
}
