/**
 * frontend/src/components/QuerySentence.tsx
 * The hero-replacement: Sentence-style query control at the top of the app.
 * "Show me [Backend Developer] jobs in [All India] with [0-2 years] experience."
 */

import React from 'react'

export interface QueryFilters {
  role: string
  city: string
  expBand: string
  minExp?: number
  maxExp?: number
}

interface QuerySentenceProps {
  filters: QueryFilters
  rolesList: string[]
  citiesList: string[]
  onChange: (updated: Partial<QueryFilters>) => void
  onReset: () => void
}

export const EXP_OPTIONS = [
  { label: 'any experience', minExp: undefined, maxExp: undefined },
  { label: '0-1 years (Fresher)', minExp: 0, maxExp: 1 },
  { label: '1-3 years (Junior)', minExp: 1, maxExp: 3 },
  { label: '3-6 years (Mid-level)', minExp: 3, maxExp: 6 },
  { label: '6-10 years (Senior)', minExp: 6, maxExp: 10 },
  { label: '10+ years (Lead)', minExp: 10, maxExp: 30 },
]

export const QuerySentence: React.FC<QuerySentenceProps> = ({
  filters,
  rolesList,
  citiesList,
  onChange,
  onReset,
}) => {
  const isFiltered =
    filters.role !== 'Backend Developer' ||
    filters.city !== 'All India' ||
    filters.expBand !== 'any experience'

  const handleExpChange = (label: string) => {
    const opt = EXP_OPTIONS.find((o) => o.label === label)
    onChange({
      expBand: label,
      minExp: opt?.minExp,
      maxExp: opt?.maxExp,
    })
  }

  return (
    <div className="bg-panel border-b border-rule py-5 px-4 sm:px-8">
      <div className="max-w-7xl mx-auto flex flex-wrap items-baseline justify-between gap-y-4 gap-x-6">
        <div className="text-[20px] sm:text-[24px] lg:text-[28px] text-ink font-normal leading-relaxed">
          <span>Show me </span>
          
          {/* Role selector */}
          <span className="inline-block relative border-b-2 border-matched pb-0.5 mx-1 font-semibold text-ink">
            <select
              value={filters.role}
              onChange={(e) => onChange({ role: e.target.value })}
              className="bg-transparent text-matched font-bold cursor-pointer pr-5 py-0 focus:outline-none appearance-none"
              aria-label="Target job role"
            >
              {rolesList.map((r) => (
                <option key={r} value={r} className="text-ink bg-panel font-normal text-[15px]">
                  {r}
                </option>
              ))}
            </select>
            <span className="absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none text-[11px] text-matched">▼</span>
          </span>

          <span> jobs in </span>

          {/* City selector */}
          <span className="inline-block relative border-b-2 border-matched pb-0.5 mx-1 font-semibold text-ink">
            <select
              value={filters.city}
              onChange={(e) => onChange({ city: e.target.value })}
              className="bg-transparent text-matched font-bold cursor-pointer pr-5 py-0 focus:outline-none appearance-none"
              aria-label="Job hiring location"
            >
              <option value="All India" className="text-ink bg-panel font-normal text-[15px]">
                All India
              </option>
              {citiesList.map((c) => (
                <option key={c} value={c} className="text-ink bg-panel font-normal text-[15px]">
                  {c}
                </option>
              ))}
            </select>
            <span className="absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none text-[11px] text-matched">▼</span>
          </span>

          <span> with </span>

          {/* Experience selector */}
          <span className="inline-block relative border-b-2 border-matched pb-0.5 mx-1 font-semibold text-ink">
            <select
              value={filters.expBand}
              onChange={(e) => handleExpChange(e.target.value)}
              className="bg-transparent text-matched font-bold cursor-pointer pr-5 py-0 focus:outline-none appearance-none"
              aria-label="Experience requirement"
            >
              {EXP_OPTIONS.map((o) => (
                <option key={o.label} value={o.label} className="text-ink bg-panel font-normal text-[15px]">
                  {o.label}
                </option>
              ))}
            </select>
            <span className="absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none text-[11px] text-matched">▼</span>
          </span>

          <span> experience.</span>
        </div>

        {isFiltered && (
          <button
            onClick={onReset}
            className="text-[13px] text-ink-soft hover:text-ink underline underline-offset-4 shrink-0 transition-colors"
          >
            Clear filters
          </button>
        )}
      </div>
    </div>
  )
}
