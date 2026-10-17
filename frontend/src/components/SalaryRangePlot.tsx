/**
 * frontend/src/components/SalaryRangePlot.tsx
 * Discrete range/dot plot showing Min, Median, and Max in LPA per experience band.
 * Explicitly exposes sample size n. Greys out stats where n < 20.
 */

import React from 'react'
import { SalaryResponse } from '../lib/types'
import { formatLpa, formatSampleSize } from '../lib/formatters'

interface SalaryRangePlotProps {
  salaryData: SalaryResponse | null
  roleName: string
}

export const SalaryRangePlot: React.FC<SalaryRangePlotProps> = ({ salaryData, roleName }) => {
  if (!salaryData) return null

  // Find overall max LPA across bands to normalize the visual range
  let maxScale = 50
  salaryData.bands.forEach((b) => {
    if (b.max_lpa && b.max_lpa > maxScale) {
      maxScale = Math.ceil(b.max_lpa / 10) * 10
    }
  })

  return (
    <div className="bg-panel border border-rule p-5">
      {/* Header */}
      <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-rule pb-3 mb-4">
        <div>
          <h3 className="text-[18px] font-bold text-ink m-0">Salary by experience band</h3>
          <p className="text-[13px] text-ink-soft m-0">
            Annual compensation ranges for {roleName} in LPA
          </p>
        </div>
        <div className="text-[13px] font-mono text-ink-soft bg-surface px-2 py-0.5 border border-rule">
          Total disclosing salary: {formatSampleSize(salaryData.overall_sample_size)}
        </div>
      </div>

      {/* Bands listing */}
      <div className="space-y-4">
        {salaryData.bands.map((b) => {
          const isLowSample = b.sample_size < 20
          const hasData = b.sample_size > 0 && b.median_lpa !== null

          const minPct = hasData && b.min_lpa ? Math.min(100, (b.min_lpa / maxScale) * 100) : 0
          const medPct = hasData && b.median_lpa ? Math.min(100, (b.median_lpa / maxScale) * 100) : 0
          const maxPct = hasData && b.max_lpa ? Math.min(100, (b.max_lpa / maxScale) * 100) : 0

          return (
            <div
              key={b.exp_band}
              className={`p-3 border transition-colors ${
                isLowSample
                  ? 'border-rule/50 bg-surface/30 opacity-70'
                  : 'border-rule bg-surface/10 hover:bg-surface/40'
              }`}
            >
              {/* Row Header */}
              <div className="flex flex-wrap items-baseline justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-[14px] text-ink">{b.exp_band}</span>
                  {isLowSample ? (
                    <span className="text-[11px] text-ink-soft bg-rule/50 px-1.5 py-0.2 rounded-sm">
                      n &lt; 20 (low confidence)
                    </span>
                  ) : null}
                </div>
                <div className="text-[13px] text-ink-soft font-mono">
                  {formatSampleSize(b.sample_size)}
                </div>
              </div>

              {/* Data numbers and visual interval */}
              {!hasData ? (
                <div className="text-[13px] text-ink-soft italic py-1">No salary data recorded for this band</div>
              ) : (
                <div>
                  {/* Visual Range Line with Dot Plot */}
                  <div className="relative h-6 flex items-center my-1 select-none">
                    {/* Background track */}
                    <div className="absolute w-full h-1 bg-rule/50" />

                    {/* Active Range Bar (Min to Max) */}
                    <div
                      className={`absolute h-1.5 ${isLowSample ? 'bg-ink-soft/40' : 'bg-matched/40'}`}
                      style={{
                        left: `${minPct}%`,
                        width: `${Math.max(1, maxPct - minPct)}%`,
                      }}
                    />

                    {/* Min Dot */}
                    <div
                      className="absolute w-2 h-2 rounded-full bg-ink-soft -ml-1 border border-panel"
                      style={{ left: `${minPct}%` }}
                      title={`Min: ${formatLpa(b.min_lpa)}`}
                    />

                    {/* Median Dot (Prominent) */}
                    <div
                      className={`absolute w-3.5 h-3.5 rounded-full border-2 border-panel -ml-1.5 ${
                        isLowSample ? 'bg-ink-soft' : 'bg-matched'
                      }`}
                      style={{ left: `${medPct}%` }}
                      title={`Median: ${formatLpa(b.median_lpa)}`}
                    />

                    {/* Max Dot */}
                    <div
                      className="absolute w-2 h-2 rounded-full bg-ink-soft -ml-1 border border-panel"
                      style={{ left: `${maxPct}%` }}
                      title={`Max: ${formatLpa(b.max_lpa)}`}
                    />
                  </div>

                  {/* Number Labels */}
                  <div className="flex justify-between items-baseline text-[12px] text-ink-soft pt-1 font-mono">
                    <span>Min: {formatLpa(b.min_lpa)}</span>
                    <span className={`font-bold ${isLowSample ? 'text-ink-soft' : 'text-ink'}`}>
                      Median: {formatLpa(b.median_lpa)}
                    </span>
                    <span>Max: {formatLpa(b.max_lpa)}</span>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      <div className="mt-4 pt-3 border-t border-rule text-[12px] text-ink-soft flex items-center justify-between">
        <span>Range shows min, median, and max. Based on annual INR converted to LPA.</span>
        <span>Scale: 0 to {maxScale} LPA</span>
      </div>
    </div>
  )
}
