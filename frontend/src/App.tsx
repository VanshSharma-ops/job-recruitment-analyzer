/**
 * frontend/src/App.tsx
 * Main application container for Job Recruitment Analyzer.
 * Synchronizes filters with URL search params, manages skills profile state,
 * and coordinates data loading from the FastAPI backend.
 */

import React, { useEffect, useState, useCallback } from 'react'
import { api } from './lib/api'
import {
  CompanyTopResponse,
  JobListResponse,
  LocationTopResponse,
  SalaryResponse,
  SkillGapResponse,
  SkillTopResponse,
} from './lib/types'
import { Header, TabType } from './components/Header'
import { EXP_OPTIONS, QueryFilters, QuerySentence } from './components/QuerySentence'
import { SkillsPanel } from './components/SkillsPanel'
import { TopSkillsBarChart } from './components/TopSkillsBarChart'
import { SalaryRangePlot } from './components/SalaryRangePlot'
import { HiringLocationsTable } from './components/HiringLocationsTable'
import { TopCompaniesList } from './components/TopCompaniesList'
import { JobSearchTable } from './components/JobSearchTable'
import { SkillGapView } from './components/SkillGapView'
import { ErrorState, LoadingState } from './components/StateViews'

const DEFAULT_SKILLS = ['Python', 'SQL', 'Git']
const CITIES_LIST = [
  'Bengaluru',
  'Hyderabad',
  'Pune',
  'Delhi NCR',
  'Mumbai',
  'Chennai',
  'Kolkata',
  'Ahmedabad',
  'Kochi',
  'Jaipur',
]

export const App: React.FC = () => {
  // --- 1. State from URL Query Parameters ---
  const [activeTab, setActiveTab] = useState<TabType>('analysis')
  const [filters, setFilters] = useState<QueryFilters>({
    role: 'Backend Developer',
    city: 'All India',
    expBand: 'any experience',
    minExp: undefined,
    maxExp: undefined,
  })

  // --- 2. User Skills Profile (Persisted in localStorage) ---
  const [userSkills, setUserSkills] = useState<string[]>(() => {
    try {
      const stored = localStorage.getItem('job_analyzer_user_skills')
      if (stored) return JSON.parse(stored)
    } catch {}
    return DEFAULT_SKILLS
  })

  // Save to localStorage on change
  useEffect(() => {
    try {
      localStorage.setItem('job_analyzer_user_skills', JSON.stringify(userSkills))
    } catch {}
  }, [userSkills])

  // --- 3. Dynamic Roles Taxonomy List from DB ---
  const [rolesList, setRolesList] = useState<string[]>([
    'Backend Developer',
    'Frontend Developer',
    'Full Stack Developer',
    'Data Engineer',
    'Machine Learning Engineer',
    'DevOps Engineer',
    'Data Analyst',
    'Mobile Developer',
  ])
  const [totalPostings, setTotalPostings] = useState<number>(5600)

  // --- 4. Market Data States ---
  const [skillsData, setSkillsData] = useState<SkillTopResponse | null>(null)
  const [salaryData, setSalaryData] = useState<SalaryResponse | null>(null)
  const [locationsData, setLocationsData] = useState<LocationTopResponse | null>(null)
  const [companiesData, setCompaniesData] = useState<CompanyTopResponse | null>(null)
  const [gapData, setGapData] = useState<SkillGapResponse | null>(null)
  const [jobsData, setJobsData] = useState<JobListResponse | null>(null)

  // Job Search Tab specific states
  const [jobSearchQuery, setJobSearchQuery] = useState('')
  const [jobsPage, setJobsPage] = useState(1)

  // Loading and Error States
  const [loadingAnalysis, setLoadingAnalysis] = useState(false)
  const [loadingGap, setLoadingGap] = useState(false)
  const [loadingJobs, setLoadingJobs] = useState(false)
  const [analysisError, setAnalysisError] = useState<string | null>(null)

  // --- 5. Sync from URL on Mount & Back/Forward Navigation ---
  useEffect(() => {
    const parseUrl = () => {
      const params = new URLSearchParams(window.location.search)
      const roleParam = params.get('role') || 'Backend Developer'
      const cityParam = params.get('city') || 'All India'
      const expParam = params.get('exp') || 'any experience'
      const tabParam = (params.get('tab') as TabType) || 'analysis'

      const matchedExp = EXP_OPTIONS.find((o) => o.label === expParam)

      setFilters({
        role: roleParam,
        city: cityParam,
        expBand: expParam,
        minExp: matchedExp?.minExp,
        maxExp: matchedExp?.maxExp,
      })

      if (['analysis', 'jobs', 'gap'].includes(tabParam)) {
        setActiveTab(tabParam)
      }
    }

    parseUrl()
    window.addEventListener('popstate', parseUrl)
    return () => window.removeEventListener('popstate', parseUrl)
  }, [])

  // Sync to URL whenever filters or active tab changes
  const updateUrlParams = useCallback(
    (newFilters: QueryFilters, tab: TabType) => {
      const params = new URLSearchParams()
      if (newFilters.role) params.set('role', newFilters.role)
      if (newFilters.city && newFilters.city !== 'All India') params.set('city', newFilters.city)
      if (newFilters.expBand && newFilters.expBand !== 'any experience') params.set('exp', newFilters.expBand)
      if (tab !== 'analysis') params.set('tab', tab)

      const newUrl = `${window.location.pathname}${params.toString() ? `?${params.toString()}` : ''}`
      window.history.pushState(null, '', newUrl)
    },
    []
  )

  const handleFilterChange = (updated: Partial<QueryFilters>) => {
    const next = { ...filters, ...updated }
    setFilters(next)
    setJobsPage(1)
    updateUrlParams(next, activeTab)
  }

  const handleResetFilters = () => {
    const resetFilters: QueryFilters = {
      role: 'Backend Developer',
      city: 'All India',
      expBand: 'any experience',
      minExp: undefined,
      maxExp: undefined,
    }
    setFilters(resetFilters)
    setJobSearchQuery('')
    setJobsPage(1)
    updateUrlParams(resetFilters, activeTab)
  }

  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab)
    updateUrlParams(filters, tab)
  }

  // --- 6. Initial Roles Load ---
  useEffect(() => {
    api
      .getRoles()
      .then((res) => {
        if (res.roles.length > 0) {
          setRolesList(res.roles.map((r) => r.role))
          setTotalPostings(res.total_postings)
        }
      })
      .catch((err) => {
        console.error('Failed to load roles list:', err)
      })
  }, [])

  // --- 7. Load Analysis Data from API ---
  const loadMarketAnalysis = useCallback(() => {
    setLoadingAnalysis(true)
    setAnalysisError(null)

    const cityArg = filters.city === 'All India' ? undefined : filters.city

    Promise.all([
      api.getTopSkills({
        role: filters.role,
        city: cityArg,
        min_exp: filters.minExp,
        max_exp: filters.maxExp,
        limit: 25,
      }),
      api.getSalary({
        role: filters.role,
        city: cityArg,
      }),
      api.getTopLocations({
        role: filters.role,
        min_exp: filters.minExp,
        max_exp: filters.maxExp,
        limit: 10,
      }),
      api.getTopCompanies({
        role: filters.role,
        city: cityArg,
        min_exp: filters.minExp,
        max_exp: filters.maxExp,
        limit: 15,
      }),
    ])
      .then(([skillsRes, salaryRes, locationsRes, companiesRes]) => {
        setSkillsData(skillsRes)
        setSalaryData(salaryRes)
        setLocationsData(locationsRes)
        setCompaniesData(companiesRes)
      })
      .catch((err) => {
        setAnalysisError(err.message || 'Failed to load market data')
      })
      .finally(() => {
        setLoadingAnalysis(false)
      })
  }, [filters])

  // --- 8. Load Skill Gap Data from API ---
  const loadSkillGap = useCallback(() => {
    setLoadingGap(true)
    const cityArg = filters.city === 'All India' ? undefined : filters.city

    api
      .compareSkillGap({
        role: filters.role,
        skills: userSkills,
        city: cityArg,
        min_exp: filters.minExp,
        max_exp: filters.maxExp,
      })
      .then((res) => {
        setGapData(res)
      })
      .catch((err) => {
        console.error('Skill gap calculation error:', err)
      })
      .finally(() => {
        setLoadingGap(false)
      })
  }, [filters, userSkills])

  // --- 9. Load Job Postings Data from API ---
  const loadJobPostings = useCallback(() => {
    setLoadingJobs(true)
    const cityArg = filters.city === 'All India' ? undefined : filters.city

    api
      .getJobs({
        role: filters.role,
        city: cityArg,
        min_exp: filters.minExp,
        max_exp: filters.maxExp,
        search: jobSearchQuery || undefined,
        page: jobsPage,
        page_size: 15,
      })
      .then((res) => {
        setJobsData(res)
      })
      .catch((err) => {
        console.error('Failed to load job postings:', err)
      })
      .finally(() => {
        setLoadingJobs(false)
      })
  }, [filters, jobSearchQuery, jobsPage])

  // Trigger data loads when dependencies change
  useEffect(() => {
    loadMarketAnalysis()
  }, [loadMarketAnalysis])

  useEffect(() => {
    loadSkillGap()
  }, [loadSkillGap])

  useEffect(() => {
    if (activeTab === 'jobs') {
      loadJobPostings()
    }
  }, [activeTab, loadJobPostings])

  // --- User Skill Management Handlers ---
  const handleAddSkill = (skill: string) => {
    const trimmed = skill.trim()
    if (!trimmed) return
    if (userSkills.some((s) => s.toLowerCase() === trimmed.toLowerCase())) return
    setUserSkills([...userSkills, trimmed])
  }

  const handleRemoveSkill = (skill: string) => {
    setUserSkills(userSkills.filter((s) => s.toLowerCase() !== skill.toLowerCase()))
  }

  const handleToggleSkill = (skillName: string) => {
    if (userSkills.some((s) => s.toLowerCase() === skillName.toLowerCase())) {
      handleRemoveSkill(skillName)
    } else {
      handleAddSkill(skillName)
    }
  }

  return (
    <div className="min-h-screen bg-surface flex flex-col selection:bg-matched/20 selection:text-ink">
      {/* Top Header */}
      <Header activeTab={activeTab} onTabChange={handleTabChange} totalPostings={totalPostings} />

      {/* Query Sentence Top Control */}
      <QuerySentence
        filters={filters}
        rolesList={rolesList}
        citiesList={CITIES_LIST}
        onChange={handleFilterChange}
        onReset={handleResetFilters}
      />

      {/* Main Content Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-8 py-6">
        {analysisError ? (
          <ErrorState message={analysisError} onRetry={loadMarketAnalysis} />
        ) : (
          <div className="flex flex-col lg:flex-row gap-6 items-start">
            {/* Primary Content (2/3 width on desktop) */}
            <div className="w-full lg:w-2/3 space-y-6">
              {activeTab === 'analysis' && (
                <>
                  {loadingAnalysis ? (
                    <div className="bg-panel border border-rule p-8">
                      <LoadingState message="Aggregating market metrics from database..." />
                    </div>
                  ) : (
                    <>
                      {/* Top Demanded Skills Horizontal Bars */}
                      <TopSkillsBarChart
                        skills={skillsData?.skills || []}
                        sampleSize={skillsData?.sample_size || 0}
                        roleName={filters.role}
                        userSkills={userSkills}
                        onToggleSkill={handleToggleSkill}
                      />

                      {/* Salary Range / Dot Plot by Experience Band */}
                      <SalaryRangePlot salaryData={salaryData} roleName={filters.role} />

                      {/* Hiring Geography & Companies Split Grid */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <HiringLocationsTable
                          locations={locationsData?.locations || []}
                          roleName={filters.role}
                          onCityClick={(c) => handleFilterChange({ city: c })}
                        />
                        <TopCompaniesList
                          companies={companiesData?.companies || []}
                          roleName={filters.role}
                        />
                      </div>
                    </>
                  )}
                </>
              )}

              {activeTab === 'gap' && (
                <SkillGapView
                  data={gapData}
                  loading={loadingGap}
                  roleName={filters.role}
                  onAddSkill={handleAddSkill}
                  onRemoveSkill={handleRemoveSkill}
                />
              )}

              {activeTab === 'jobs' && (
                <JobSearchTable
                  data={jobsData}
                  loading={loadingJobs}
                  currentPage={jobsPage}
                  onPageChange={setJobsPage}
                  userSkills={userSkills}
                  searchQuery={jobSearchQuery}
                  onSearchChange={(q) => {
                    setJobSearchQuery(q)
                    setJobsPage(1)
                  }}
                  onClearFilters={handleResetFilters}
                />
              )}
            </div>

            {/* Persistent 'Your skills' Panel (1/3 width on desktop) */}
            <div className="w-full lg:w-1/3 lg:sticky lg:top-6">
              <SkillsPanel
                userSkills={userSkills}
                gapData={gapData}
                loading={loadingGap}
                onAddSkill={handleAddSkill}
                onRemoveSkill={handleRemoveSkill}
                onCompareFullGap={() => handleTabChange('gap')}
              />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-rule bg-panel py-6 px-4 sm:px-8 mt-12 text-[13px] text-ink-soft">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="font-bold text-ink">Job Recruitment Analyzer</div>
            <div>Built for engineering students and freshers analyzing Indian market trends.</div>
          </div>
          <div className="text-[12px] font-mono">
            FastAPI • PostgreSQL • React • Tailwind CSS
          </div>
        </div>
      </footer>
    </div>
  )
}
