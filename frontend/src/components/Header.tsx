/**
 * frontend/src/components/Header.tsx
 * Clean, calm header with persistent synthetic dataset notice and tab navigation.
 */

import React from 'react'

export type TabType = 'analysis' | 'jobs' | 'gap'

interface HeaderProps {
  activeTab: TabType
  onTabChange: (tab: TabType) => void
  totalPostings?: number
}

export const Header: React.FC<HeaderProps> = ({ activeTab, onTabChange, totalPostings = 5600 }) => {
  return (
    <header className="border-b border-rule bg-panel">
      {/* Top persistent synthetic data banner */}
      <div className="bg-surface border-b border-rule px-4 sm:px-8 py-1.5 text-[12px] text-ink-soft flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-matched inline-block" />
          <span>Note: Synthetic seed dataset based on Indian tech market ({totalPostings.toLocaleString('en-IN')} postings).</span>
        </span>
      </div>

      {/* Main Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-[18px] sm:text-[20px] font-bold text-ink tracking-tight m-0">
            Job Recruitment Analyzer
          </h1>
          <p className="text-[13px] text-ink-soft m-0">
            Market skills demand, compensation bands, and skills gap analysis
          </p>
        </div>

        {/* Tab Navigation */}
        <nav className="flex items-center gap-1 border border-rule p-0.5 rounded-md bg-surface text-[14px]">
          <button
            onClick={() => onTabChange('analysis')}
            className={`px-3 py-1 font-medium rounded-md transition-colors ${
              activeTab === 'analysis'
                ? 'bg-panel text-ink shadow-none border border-rule/50'
                : 'text-ink-soft hover:text-ink hover:bg-panel/40'
            }`}
          >
            Market Analysis
          </button>
          <button
            onClick={() => onTabChange('gap')}
            className={`px-3 py-1 font-medium rounded-md transition-colors ${
              activeTab === 'gap'
                ? 'bg-panel text-ink shadow-none border border-rule/50'
                : 'text-ink-soft hover:text-ink hover:bg-panel/40'
            }`}
          >
            Skill Gap
          </button>
          <button
            onClick={() => onTabChange('jobs')}
            className={`px-3 py-1 font-medium rounded-md transition-colors ${
              activeTab === 'jobs'
                ? 'bg-panel text-ink shadow-none border border-rule/50'
                : 'text-ink-soft hover:text-ink hover:bg-panel/40'
            }`}
          >
            Job Postings
          </button>
        </nav>
      </div>
    </header>
  )
}
