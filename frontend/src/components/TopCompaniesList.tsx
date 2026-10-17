/**
 * frontend/src/components/TopCompaniesList.tsx
 * Plain ranked list with posting counts and company demand share.
 */

import React from 'react'
import { CompanyItem } from '../lib/types'
import { formatPercentage, formatSampleSize } from '../lib/formatters'

interface TopCompaniesListProps {
  companies: CompanyItem[]
  roleName: string
}

export const TopCompaniesList: React.FC<TopCompaniesListProps> = ({ companies, roleName }) => {
  return (
    <div className="bg-panel border border-rule p-5">
      <div className="border-b border-rule pb-3 mb-3">
        <h3 className="text-[18px] font-bold text-ink m-0">Top hiring employers</h3>
        <p className="text-[13px] text-ink-soft m-0">Companies with the highest {roleName} open headcount</p>
      </div>

      {companies.length === 0 ? (
        <p className="text-[13px] text-ink-soft italic py-4 text-center m-0">
          No employer data available for this query.
        </p>
      ) : (
        <ol className="list-decimal list-inside space-y-1.5 p-0 m-0 text-[13px]">
          {companies.slice(0, 12).map((comp, idx) => (
            <li
              key={comp.company}
              className="flex items-center justify-between py-1.5 px-2 border-b border-rule/30 hover:bg-surface/50 transition-colors"
            >
              <span className="font-medium text-ink flex items-center gap-2">
                <span className="text-ink-soft font-mono text-[12px] w-4">{idx + 1}.</span>
                <span>{comp.company}</span>
              </span>
              <div className="flex items-center gap-3 font-mono">
                <span className="text-[12px] text-ink-soft">{formatPercentage(comp.percentage)}</span>
                <span className="text-[13px] font-semibold text-ink w-16 text-right">
                  {formatSampleSize(comp.posting_count)}
                </span>
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}
