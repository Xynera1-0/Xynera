import type { Artifact } from '@/types'
import { ArtifactRenderer } from '@/artifacts/ArtifactRenderer'

interface Props {
  role: 'user' | 'assistant'
  content: string | null
  artifact: Artifact | null
}

export function MessageItem({ role, content, artifact }: Props) {
  if (role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-2xl px-4 py-2.5 rounded-2xl rounded-br-md bg-brand-600 text-white text-sm leading-relaxed">
          {content}
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-4xl w-full space-y-3">
        {/* Agent avatar */}
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-brand-900 border border-brand-700 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5 text-brand-400">
              <path d="M8 1a4 4 0 0 0-4 4v1H3a1 1 0 0 0-1 1v6a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7a1 1 0 0 0-1-1h-1V5a4 4 0 0 0-4-4Zm2 5V5a2 2 0 1 0-4 0v1h4Z" />
            </svg>
          </div>
          <span className="text-xs text-gray-500 font-medium">Xynera</span>
        </div>

        {/* Content or artifact */}
        {artifact ? (
          <ArtifactRenderer artifact={artifact} />
        ) : content ? (
          <div className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap pl-8">
            {content}
          </div>
        ) : null}
      </div>
    </div>
  )
}
