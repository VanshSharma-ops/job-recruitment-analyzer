/**
 * frontend/src/components/HiringLocationsTable.tsx
 * Dense sorted table with inline bar column for city hiring volume.
 */

import React from 'react'
import { LocationItem } from '../lib/types'
import { formatLpa, formatPercentage, formatSampleSize } from '../lib/formatters'

interface HiringLocationsTableProps {
  locations: LocationItem[]
  roleName: string
  onCityClick?: (city: string) => void
}

export const HiringLocationsTable: React.FC<HiringLocationsTableProps> = ({
  locations,
  roleName,
  onCityClick,
}) => {
  return (
    <div className="bg-panel border border-rule p-5">
      <div className="border-b border-rule pb-3 mb-3">
        <h3 className="text-[18px] font-bold text-ink m-0">Hiring locations</h3>
        <p className="text-[13px] text-ink-soft m-0">Top Indian cities hiring for {roleName}</p>
      </div>

      {locations.length === 0 ? (
        <p className="text-[13px] text-ink-soft italic py-4 text-center m-0">
          No location data available for this query.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-[13px]">
            <thead>
              <tr className="border-b border-rule text-ink-soft text-[12px]">
                <th className="py-2 pr-3 font-medium">City</th>
                <th className="py-2 px-3 font-medium">Market share</th>
                <th className="py-2 px-3 font-medium text-right">Postings</th>
                <th className="py-2 pl-3 font-medium text-right">Median salary</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-rule/50">
              {locations.map((loc) => {
                const isLowSample = loc.sample_size < 20
                return (
                  <tr
                    key={loc.city}
                    onClick={() => onCityClick?.(loc.city)}
                    className={`hover:bg-surface/50 transition-colors ${
                      onCityClick ? 'cursor-pointer' : ''
                    } ${isLowSample ? 'opacity-65' : ''}`}
                  >
                    <td className="py-2.5 pr-3 font-medium text-ink flex items-center gap-1.5">
                      <span>{loc.city}</span>
                      {isLowSample && (
                        <span className="text-[10px] text-ink-soft bg-rule/50 px-1 py-0.2 rounded-sm">
                          n&lt;20
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 w-40">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 flex-1 bg-surface border border-rule/50 overflow-hidden">
                          <div
                            style={{ width: `${Math.min(100, loc.percentage)}%` }}
                            className="h-full bg-ink-soft"
                          />
                        </div>
                        <span className="font-mono text-[12px] text-ink-soft w-10 text-right">
                          {formatPercentage(loc.percentage)}
                        </span>
                      </div>
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono text-ink">
                      {formatSampleSize(loc.posting_count)}
                    </td>
                    <td className="py-2.5 pl-3 text-right font-mono font-medium text-ink">
                      {formatLpa(loc.median_salary_lpa)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
