/**
 * frontend/src/components/JobSearchTable.tsx
 * Dense sortable table of job postings with pagination and expandable description.
 */

import React, { useState } from 'react'
import { JobItem, JobListResponse } from '../lib/types'
import { formatExpRange, formatLpa, formatSampleSize } from '../lib/formatters'
import { EmptyState, LoadingState } from './StateViews'

interface JobSearchTableProps {
  data: JobListResponse | null
  loading: boolean
  currentPage: number
  onPageChange: (page: number) => void
  userSkills: string[]
  searchQuery: string
  onSearchChange: (query: string) => void
  onClearFilters: () => void
}

export const JobSearchTable: React.FC<JobSearchTableProps> = ({
  data,
  loading,
  currentPage,
  onPageChange,
  userSkills,
  searchQuery,
  onSearchChange,
  onClearFilters,
}) => {
  const [expandedJobId, setExpandedJobId] = useState<number | null>(null)
  const userSkillSet = new Set(userSkills.map((s) => s.toLowerCase()))

  const toggleExpand = (id: number) => {
    setExpandedJobId(expandedJobId === id ? null : id)
  }

  return (
    <div className="bg-panel border border-rule p-5 space-y-4">
      {/* Header and Search control */}
      <div className="flex flex-wrap items-baseline justify-between gap-3 border-b border-rule pb-4">
        <div>
          <h3 className="text-[18px] font-bold text-ink m-0">Job postings database</h3>
          <p className="text-[13px] text-ink-soft m-0">
            Browse matching openings with extracted skills breakdown
          </p>
        </div>
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search title, company, or city..."
            className="px-3 py-1.5 text-[13px] bg-surface border border-rule rounded-md text-ink w-64 focus:outline-none focus:border-matched"
          />
          <div className="text-[13px] font-mono text-ink-soft bg-surface px-2.5 py-1 border border-rule">
            {formatSampleSize(data?.total || 0)}
          </div>
        </div>
      </div>

      {loading ? (
        <LoadingState message="Fetching job postings..." />
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          message="No postings match these filters. Try widening the experience range or clearing search keywords."
          actionLabel="Clear all filters"
          onAction={onClearFilters}
        />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-[13px]">
            <thead>
              <tr className="border-b border-rule text-ink-soft text-[12px]">
                <th className="py-2.5 pr-3 font-medium">Job title & company</th>
                <th className="py-2.5 px-3 font-medium">Location</th>
                <th className="py-2.5 px-3 font-medium">Experience</th>
                <th className="py-2.5 px-3 font-medium">Compensation</th>
                <th className="py-2.5 px-3 font-medium">Extracted skills</th>
                <th className="py-2.5 pl-3 font-medium text-right">Posted</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-rule/40 font-normal">
              {data.items.map((job: JobItem) => {
                const isExpanded = expandedJobId === job.id
                const salDisplay =
                  job.salary_min_lpa && job.salary_max_lpa
                    ? `${formatLpa(job.salary_min_lpa)} - ${formatLpa(job.salary_max_lpa)}`
                    : job.salary_median_lpa
                    ? formatLpa(job.salary_median_lpa)
                    : 'Undisclosed'

                return (
                  <React.Fragment key={job.id}>
                    <tr
                      onClick={() => toggleExpand(job.id)}
                      className={`hover:bg-surface/50 cursor-pointer transition-colors ${
                        isExpanded ? 'bg-surface/60' : ''
                      }`}
                    >
                      <td className="py-3 pr-3">
                        <div className="font-bold text-ink">{job.title}</div>
                        <div className="text-[12px] text-ink-soft">{job.company}</div>
                      </td>
                      <td className="py-3 px-3 text-ink">
                        <div>{job.city}</div>
                        <div className="text-[11px] text-ink-soft truncate max-w-[140px]">{job.location}</div>
                      </td>
                      <td className="py-3 px-3 text-ink font-mono text-[12px]">
                        {formatExpRange(job.min_exp, job.max_exp)}
                      </td>
                      <td className="py-3 px-3 font-mono font-medium text-ink">
                        {salDisplay}
                      </td>
                      <td className="py-3 px-3">
                        <div className="flex flex-wrap gap-1 max-w-xs">
                          {job.skills.slice(0, 4).map((sk) => {
                            const isMatched = userSkillSet.has(sk.toLowerCase())
                            return (
                              <span
                                key={sk}
                                className={`text-[11px] px-1.5 py-0.2 rounded-sm border ${
                                  isMatched
                                    ? 'bg-matched/10 border-matched/40 text-matched font-medium'
                                    : 'bg-surface border-rule text-ink-soft'
                                }`}
                              >
                                {sk}
                              </span>
                            )
                          })}
                          {job.skills.length > 4 && (
                            <span className="text-[11px] text-ink-soft">
                              +{job.skills.length - 4}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 pl-3 text-right font-mono text-[12px] text-ink-soft whitespace-nowrap">
                        {job.posted_date || 'Recently'}
                      </td>
                    </tr>

                    {/* Expandable Job Description Detail */}
                    {isExpanded && (
                      <tr className="bg-surface/40">
                        <td colSpan={6} className="p-4 border-b border-rule">
                          <div className="max-w-3xl space-y-3">
                            <div className="flex items-center justify-between text-[13px] border-b border-rule/50 pb-2">
                              <span className="font-bold text-ink">Reference ID: {job.job_uid}</span>
                              <span className="text-ink-soft font-mono">Role category: {job.role}</span>
                            </div>
                            <div className="text-[13px] leading-relaxed whitespace-pre-line text-ink">
                              {job.description}
                            </div>
                            <div className="pt-2">
                              <span className="text-[12px] font-bold text-ink-soft mr-2">All skills identified:</span>
                              <div className="inline-flex flex-wrap gap-1.5 align-middle mt-1">
                                {job.skills.map((s) => {
                                  const isMatched = userSkillSet.has(s.toLowerCase())
                                  return (
                                    <span
                                      key={s}
                                      className={`text-[12px] px-2 py-0.5 border rounded-sm ${
                                        isMatched
                                          ? 'bg-matched/15 text-matched border-matched font-medium'
                                          : 'bg-panel text-ink border-rule'
                                      }`}
                                    >
                                      {s} {isMatched ? '✓' : ''}
                                    </span>
                                  )
                                })}
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination Controls */}
      {data && data.total_pages > 1 && (
        <div className="flex items-center justify-between border-t border-rule pt-4 text-[13px]">
          <span className="text-ink-soft font-mono">
            Page {data.page} of {data.total_pages} ({data.total} total postings)
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage <= 1}
              className="px-3 py-1 border border-rule rounded-md bg-panel text-ink disabled:opacity-40 disabled:cursor-not-allowed hover:border-ink transition-colors"
            >
              Previous
            </button>
            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage >= data.total_pages}
              className="px-3 py-1 border border-rule rounded-md bg-panel text-ink disabled:opacity-40 disabled:cursor-not-allowed hover:border-ink transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
