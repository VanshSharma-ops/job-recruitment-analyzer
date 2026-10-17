/**
 * frontend/src/components/StateViews.tsx
 * Calm, informative Loading, Empty, and Error states adhering to Section 7.2.
 */

import React from 'react'

interface LoadingProps {
  message?: string
}

export const LoadingState: React.FC<LoadingProps> = ({ message = 'Loading market data...' }) => (
  <div className="py-12 flex flex-col items-center justify-center text-center">
    <div className="w-5 h-5 border-2 border-rule border-t-matched rounded-full animate-spin mb-3" />
    <span className="text-[13px] text-ink-soft">{message}</span>
  </div>
)

interface EmptyProps {
  message?: string
  actionLabel?: string
  onAction?: () => void
}

export const EmptyState: React.FC<EmptyProps> = ({
  message = 'No postings match these filters. Try widening the experience range or selecting another location.',
  actionLabel,
  onAction,
}) => (
  <div className="py-10 px-6 border border-rule bg-surface/50 text-center my-3">
    <p className="text-[15px] text-ink max-w-md mx-auto mb-3">{message}</p>
    {actionLabel && onAction && (
      <button
        onClick={onAction}
        className="px-3 py-1.5 text-[13px] bg-panel border border-rule hover:border-ink-soft text-ink rounded-md transition-colors"
      >
        {actionLabel}
      </button>
    )}
  </div>
)

interface ErrorProps {
  message?: string
  onRetry?: () => void
}

export const ErrorState: React.FC<ErrorProps> = ({
  message = "Couldn't load data. Check that the API is running, then retry.",
  onRetry,
}) => (
  <div className="py-8 px-6 border border-missing/40 bg-missing/5 text-ink my-3">
    <div className="flex items-start justify-between gap-4">
      <div>
        <div className="text-[13px] font-bold text-missing mb-1">Data Retrieval Notice</div>
        <p className="text-[15px] text-ink">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-3 py-1 text-[13px] bg-panel border border-missing text-missing hover:bg-missing hover:text-white rounded-md transition-colors shrink-0"
        >
          Retry request
        </button>
      )}
    </div>
  </div>
)
