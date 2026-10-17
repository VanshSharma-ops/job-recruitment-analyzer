/**
 * frontend/src/components/TopSkillsBarChart.tsx
 * Horizontal ranked bars showing market demand (% of postings).
 * Accessible: Uses both color and explicit textual indicators ('you have this' / 'missing').
 * Exposes sample size n.
 */

import React from 'react'
import { SkillDemanded } from '../lib/types'
import { formatPercentage, formatSampleSize } from '../lib/formatters'

interface TopSkillsBarChartProps {
  skills: SkillDemanded[]
  sampleSize: number
  roleName: string
  userSkills: string[]
  onToggleSkill: (skillName: string) => void
}

export const TopSkillsBarChart: React.FC<TopSkillsBarChartProps> = ({
  skills,
  sampleSize,
  roleName,
  userSkills,
  onToggleSkill,
}) => {
  const userSkillSet = new Set(userSkills.map((s) => s.toLowerCase()))

  return (
    <div className="bg-panel border border-rule p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-rule pb-3 mb-4">
        <div>
          <h3 className="text-[18px] font-bold text-ink m-0">Top demanded skills</h3>
          <p className="text-[13px] text-ink-soft m-0">
            Percentage of {roleName} job postings requiring each skill
          </p>
        </div>
        <div className="text-[13px] font-mono text-ink-soft bg-surface px-2 py-0.5 border border-rule">
          {formatSampleSize(sampleSize)}
        </div>
      </div>

      {skills.length === 0 ? (
        <p className="text-[13px] text-ink-soft italic py-6 text-center m-0">
          No skills data available for this criteria.
        </p>
      ) : (
        <div className="space-y-2.5">
          {skills.slice(0, 14).map((item) => {
            const hasSkill = userSkillSet.has(item.skill.toLowerCase())
            const barWidth = Math.min(100, Math.max(3, item.percentage))

            return (
              <div
                key={item.skill}
                onClick={() => onToggleSkill(item.skill)}
                className="group cursor-pointer select-none py-1 px-1 -mx-1 hover:bg-surface/60 transition-colors"
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault()
                    onToggleSkill(item.skill)
                  }
                }}
                aria-label={`${item.skill}: required in ${item.percentage}% of postings. ${hasSkill ? 'You have this.' : 'Missing from profile. Click to add.'}`}
              >
                {/* Row Header */}
                <div className="flex items-baseline justify-between text-[13px] mb-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-ink group-hover:text-matched transition-colors">
                      {item.skill}
                    </span>
                    <span className="text-[11px] text-ink-soft">({item.category})</span>
                    <span
                      className={`text-[11px] px-1.5 py-0.2 rounded-sm border ${
                        hasSkill
                          ? 'bg-matched/10 text-matched border-matched/30 font-medium'
                          : 'bg-missing/10 text-missing border-missing/30'
                      }`}
                    >
                      {hasSkill ? 'you have this' : 'missing'}
                    </span>
                  </div>
                  <div className="font-mono text-[13px] text-ink font-semibold">
                    {formatPercentage(item.percentage)}
                  </div>
                </div>

                {/* Horizontal Bar Graphic */}
                <div className="h-2 w-full bg-surface border border-rule/60 overflow-hidden">
                  <div
                    style={{ width: `${barWidth}%` }}
                    className={`h-full transition-all duration-300 ${
                      hasSkill ? 'bg-matched' : 'bg-missing'
                    }`}
                  />
                </div>
              </div>
            )
          })}
        </div>
      )}

      <div className="mt-4 pt-3 border-t border-rule flex items-center justify-between text-[12px] text-ink-soft">
        <span>Click any skill row to add or remove it from your profile.</span>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 bg-matched inline-block" /> Matched
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 bg-missing inline-block" /> Missing
          </span>
        </div>
      </div>
    </div>
  )
}
