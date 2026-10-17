/**
 * frontend/src/components/SkillsPanel.tsx
 * Persistent "Your skills" workspace panel (1/3 width on desktop).
 * Allows freshers to maintain their skill stack and inspect immediate gap metrics.
 */

import React, { useState } from 'react'
import { SkillGapResponse } from '../lib/types'
import { formatPercentage } from '../lib/formatters'

interface SkillsPanelProps {
  userSkills: string[]
  gapData: SkillGapResponse | null
  loading: boolean
  onAddSkill: (skill: string) => void
  onRemoveSkill: (skill: string) => void
  onCompareFullGap: () => void
}

const COMMON_FRESHER_SKILLS = ['Python', 'SQL', 'Git', 'Java', 'JavaScript', 'React', 'Docker', 'FastAPI']

export const SkillsPanel: React.FC<SkillsPanelProps> = ({
  userSkills,
  gapData,
  loading,
  onAddSkill,
  onRemoveSkill,
  onCompareFullGap,
}) => {
  const [inputVal, setInputVal] = useState('')

  const handleAdd = (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    const trimmed = inputVal.trim()
    if (!trimmed) return
    onAddSkill(trimmed)
    setInputVal('')
  }

  return (
    <aside className="bg-panel border border-rule p-5 rounded-none space-y-5">
      {/* Panel Heading */}
      <div className="border-b border-rule pb-3">
        <div className="flex items-baseline justify-between">
          <h2 className="text-[18px] font-bold text-ink tracking-tight m-0">Your profile</h2>
          <span className="text-[13px] text-ink-soft">
            {userSkills.length} {userSkills.length === 1 ? 'skill' : 'skills'} listed
          </span>
        </div>
        <p className="text-[13px] text-ink-soft mt-1 mb-0">
          List what you know to see what is missing for your target role.
        </p>
      </div>

      {/* Input Form */}
      <form onSubmit={handleAdd} className="space-y-2">
        <label htmlFor="skill-input" className="block text-[13px] font-medium text-ink">
          Add skill
        </label>
        <div className="flex gap-2">
          <input
            id="skill-input"
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="e.g. Docker, Python, AWS"
            className="flex-1 px-3 py-1.5 text-[14px] bg-surface border border-rule rounded-md text-ink focus:border-matched focus:outline-none"
          />
          <button
            type="submit"
            className="px-3 py-1.5 text-[13px] font-medium bg-matched text-white hover:bg-matched/90 rounded-md transition-colors shrink-0"
          >
            Add skill
          </button>
        </div>

        {/* Quick Suggestion Chips */}
        <div className="pt-1 flex flex-wrap gap-1.5 items-center">
          <span className="text-[11px] text-ink-soft">Quick add:</span>
          {COMMON_FRESHER_SKILLS.filter((s) => !userSkills.includes(s)).slice(0, 5).map((sk) => (
            <button
              key={sk}
              type="button"
              onClick={() => onAddSkill(sk)}
              className="text-[11px] px-1.5 py-0.5 bg-surface hover:bg-rule/70 text-ink border border-rule rounded-sm transition-colors"
            >
              +{sk}
            </button>
          ))}
        </div>
      </form>

      {/* User's Active Skills Tag List */}
      <div>
        <div className="text-[13px] font-medium text-ink mb-2">Current skills</div>
        {userSkills.length === 0 ? (
          <p className="text-[13px] text-ink-soft italic bg-surface/60 p-3 border border-rule/60 m-0">
            You have not listed any skills yet. Add what you know or click quick add items above.
          </p>
        ) : (
          <div className="flex flex-wrap gap-1.5 max-h-48 overflow-y-auto pr-1">
            {userSkills.map((s) => {
              const isMatched = gapData?.matched_skills.some((m) => m.skill.toLowerCase() === s.toLowerCase())
              return (
                <span
                  key={s}
                  className={`inline-flex items-center gap-1 px-2.5 py-1 text-[13px] rounded-sm border ${
                    isMatched
                      ? 'bg-matched/10 border-matched/40 text-matched font-medium'
                      : 'bg-surface border-rule text-ink'
                  }`}
                >
                  <span>{s}</span>
                  <button
                    type="button"
                    onClick={() => onRemoveSkill(s)}
                    className="text-ink-soft hover:text-missing ml-0.5 focus:outline-none"
                    aria-label={`Remove ${s}`}
                  >
                    ×
                  </button>
                </span>
              )
            })}
          </div>
        )}
      </div>

      {/* Live Gap Preview Box */}
      <div className="border-t border-rule pt-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-[14px] font-bold text-ink">Market match rate</div>
          <div className="text-[18px] font-bold text-matched font-mono">
            {loading ? '...' : gapData ? formatPercentage(gapData.match_percentage) : '0.0%'}
          </div>
        </div>

        {/* Dynamic Insight Sentence */}
        {gapData && !loading && (
          <div className="p-3 bg-surface border border-rule text-[13px] text-ink leading-relaxed">
            {gapData.summary_insight}
          </div>
        )}

        {/* Missing top 3 priority preview */}
        {gapData && gapData.missing_skills.length > 0 && !loading && (
          <div className="space-y-1.5">
            <div className="text-[12px] font-medium text-ink-soft">
              Top skills to learn next (ranked by demand):
            </div>
            <ul className="list-none p-0 m-0 space-y-1">
              {gapData.missing_skills.slice(0, 3).map((item) => (
                <li
                  key={item.skill}
                  className="text-[13px] flex items-center justify-between py-1 px-2 bg-surface/50 border border-rule/50"
                >
                  <span className="font-medium text-missing">
                    {item.importance_rank}. {item.skill}
                  </span>
                  <span className="text-[12px] text-ink-soft">
                    {formatPercentage(item.demand_percentage)} of jobs
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <button
          onClick={onCompareFullGap}
          className="w-full py-2 px-3 text-[13px] font-semibold bg-panel border border-rule hover:border-ink text-ink rounded-md transition-colors mt-2"
        >
          Compare my skills
        </button>
      </div>
    </aside>
  )
}
