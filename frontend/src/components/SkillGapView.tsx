/**
 * frontend/src/components/SkillGapView.tsx
 * The memorable centerpiece of the product: Detailed Skill-Gap breakdown.
 * Shows matched skills, missing skills ranked by demand, market percentages, and computed insight.
 */

import React from 'react'
import { SkillGapResponse } from '../lib/types'
import { formatPercentage, formatSampleSize } from '../lib/formatters'
import { LoadingState } from './StateViews'

interface SkillGapViewProps {
  data: SkillGapResponse | null
  loading: boolean
  roleName: string
  onAddSkill: (skill: string) => void
  onRemoveSkill: (skill: string) => void
}

export const SkillGapView: React.FC<SkillGapViewProps> = ({
  data,
  loading,
  roleName,
  onAddSkill,
  onRemoveSkill,
}) => {
  if (loading) {
    return (
      <div className="bg-panel border border-rule p-8">
        <LoadingState message="Analyzing skill gaps against role postings..." />
      </div>
    )
  }

  if (!data || data.sample_size === 0) {
    return (
      <div className="bg-panel border border-rule p-8 text-center">
        <h3 className="text-[18px] font-bold text-ink mb-2">No postings found for {roleName}</h3>
        <p className="text-[14px] text-ink-soft max-w-md mx-auto">
          Try broadening the filter criteria or selecting a different role to evaluate your skills.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Skill Gap Banner Card */}
      <div className="bg-panel border border-rule p-6">
        <div className="flex flex-wrap items-baseline justify-between gap-4 border-b border-rule pb-4 mb-4">
          <div>
            <span className="text-[13px] font-medium text-ink-soft">Skill Gap Analysis</span>
            <h2 className="text-[24px] sm:text-[28px] font-bold text-ink tracking-tight m-0">
              {data.role}
            </h2>
          </div>
          <div className="text-right">
            <div className="text-[12px] text-ink-soft font-mono">Market Alignment</div>
            <div className="text-[32px] font-bold text-matched font-mono leading-none mt-1">
              {formatPercentage(data.match_percentage)}
            </div>
            <div className="text-[12px] text-ink-soft font-mono mt-1">
              Sample size: {formatSampleSize(data.sample_size)}
            </div>
          </div>
        </div>

        {/* Dynamic Computed Insight Line */}
        <div className="p-4 bg-surface border-l-4 border-matched text-[15px] text-ink leading-relaxed font-normal">
          <span className="font-bold mr-1">Market Insight:</span>
          <span>{data.summary_insight}</span>
        </div>
      </div>

      {/* Missing Skills Section */}
      <div className="bg-panel border border-rule p-6 space-y-4">
        <div className="border-b border-rule pb-3 flex items-baseline justify-between">
          <div>
            <h3 className="text-[18px] font-bold text-missing m-0">
              What you are missing ({data.missing_skills.length} skills)
            </h3>
            <p className="text-[13px] text-ink-soft m-0">
              Commonly required skills for {data.role} ranked in order of employer demand
            </p>
          </div>
          <span className="text-[12px] text-ink-soft">Ranked by demand %</span>
        </div>

        {data.missing_skills.length === 0 ? (
          <p className="text-[14px] text-matched italic py-4">
            Congratulations! You have listed every commonly demanded skill for this role.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-[13px]">
              <thead>
                <tr className="border-b border-rule text-ink-soft text-[12px]">
                  <th className="py-2.5 pr-2 font-medium w-12 text-center">Rank</th>
                  <th className="py-2.5 px-3 font-medium">Skill</th>
                  <th className="py-2.5 px-3 font-medium">Category</th>
                  <th className="py-2.5 px-3 font-medium">Market demand</th>
                  <th className="py-2.5 px-3 font-medium text-right">In postings</th>
                  <th className="py-2.5 pl-3 font-medium text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-rule/40 font-normal">
                {data.missing_skills.map((item) => (
                  <tr key={item.skill} className="hover:bg-surface/50 transition-colors">
                    <td className="py-3 pr-2 text-center font-mono font-bold text-missing">
                      {item.importance_rank}
                    </td>
                    <td className="py-3 px-3 font-bold text-ink">
                      {item.skill}
                    </td>
                    <td className="py-3 px-3 text-ink-soft">
                      {item.category}
                    </td>
                    <td className="py-3 px-3 w-48">
                      <div className="flex items-center gap-2">
                        <div className="h-2 flex-1 bg-surface border border-rule/50 overflow-hidden">
                          <div
                            style={{ width: `${Math.min(100, item.demand_percentage)}%` }}
                            className="h-full bg-missing"
                          />
                        </div>
                        <span className="font-mono text-[12px] font-semibold text-missing w-12 text-right">
                          {formatPercentage(item.demand_percentage)}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-3 text-right font-mono text-ink-soft">
                      {item.mention_count} / {data.sample_size}
                    </td>
                    <td className="py-3 pl-3 text-right">
                      <button
                        onClick={() => onAddSkill(item.skill)}
                        className="px-2.5 py-1 text-[12px] font-medium bg-panel border border-rule hover:border-matched hover:text-matched text-ink rounded-md transition-colors whitespace-nowrap"
                      >
                        + Add to mine
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Matched Skills Section */}
      <div className="bg-panel border border-rule p-6 space-y-4">
        <div className="border-b border-rule pb-3">
          <h3 className="text-[18px] font-bold text-matched m-0">
            What you already have ({data.matched_skills.length} skills matched)
          </h3>
          <p className="text-[13px] text-ink-soft m-0">
            Skills you list that match employer requirements for {data.role}
          </p>
        </div>

        {data.matched_skills.length === 0 ? (
          <p className="text-[13px] text-ink-soft italic py-4">
            None of your listed skills currently match the top market postings for this role.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-[13px]">
              <thead>
                <tr className="border-b border-rule text-ink-soft text-[12px]">
                  <th className="py-2.5 pr-3 font-medium">Skill</th>
                  <th className="py-2.5 px-3 font-medium">Category</th>
                  <th className="py-2.5 px-3 font-medium">Role demand</th>
                  <th className="py-2.5 px-3 font-medium text-right">In postings</th>
                  <th className="py-2.5 pl-3 font-medium text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-rule/40 font-normal">
                {data.matched_skills.map((item) => (
                  <tr key={item.skill} className="hover:bg-surface/50 transition-colors">
                    <td className="py-3 pr-3 font-bold text-ink flex items-center gap-2">
                      <span>{item.skill}</span>
                    </td>
                    <td className="py-3 px-3 text-ink-soft">
                      {item.category}
                    </td>
                    <td className="py-3 px-3 w-48">
                      <div className="flex items-center gap-2">
                        <div className="h-2 flex-1 bg-surface border border-rule/50 overflow-hidden">
                          <div
                            style={{ width: `${Math.min(100, item.demand_percentage)}%` }}
                            className="h-full bg-matched"
                          />
                        </div>
                        <span className="font-mono text-[12px] font-semibold text-matched w-12 text-right">
                          {formatPercentage(item.demand_percentage)}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-3 text-right font-mono text-ink-soft">
                      {item.mention_count} / {data.sample_size}
                    </td>
                    <td className="py-3 pl-3 text-right">
                      <button
                        onClick={() => onRemoveSkill(item.skill)}
                        className="text-[12px] text-ink-soft hover:text-missing underline transition-colors"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
