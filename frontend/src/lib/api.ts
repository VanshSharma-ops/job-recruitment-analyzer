/**
 * frontend/src/lib/api.ts
 * Centralized typed API client.
 */

import {
  CompanyTopResponse,
  JobItem,
  JobListResponse,
  LocationTopResponse,
  RoleListResponse,
  SalaryResponse,
  SkillGapRequest,
  SkillGapResponse,
  SkillTopResponse,
} from './types'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }

  try {
    const res = await fetch(url, { ...options, headers })
    if (!res.ok) {
      const errorData = await res.json().catch(() => null)
      const message = errorData?.detail || `HTTP ${res.status}: ${res.statusText}`
      throw new Error(message)
    }
    return (await res.json()) as T
  } catch (err: unknown) {
    if (err instanceof Error) {
      throw err
    }
    throw new Error('An unknown network error occurred. Please check that the backend server is running.')
  }
}

export const api = {
  getRoles(): Promise<RoleListResponse> {
    return request<RoleListResponse>('/roles')
  },

  getJobs(params: {
    role?: string
    city?: string
    min_exp?: number
    max_exp?: number
    skills?: string[]
    search?: string
    page?: number
    page_size?: number
  } = {}): Promise<JobListResponse> {
    const query = new URLSearchParams()
    if (params.role) query.set('role', params.role)
    if (params.city) query.set('city', params.city)
    if (params.min_exp !== undefined && params.min_exp !== null) query.set('min_exp', String(params.min_exp))
    if (params.max_exp !== undefined && params.max_exp !== null) query.set('max_exp', String(params.max_exp))
    if (params.search) query.set('search', params.search)
    if (params.page) query.set('page', String(params.page))
    if (params.page_size) query.set('page_size', String(params.page_size))
    if (params.skills && params.skills.length > 0) {
      params.skills.forEach((s) => query.append('skills', s))
    }

    const qs = query.toString()
    return request<JobListResponse>(`/jobs${qs ? `?${qs}` : ''}`)
  },

  getJob(jobId: number): Promise<JobItem> {
    return request<JobItem>(`/jobs/${jobId}`)
  },

  getTopSkills(params: {
    role?: string
    city?: string
    min_exp?: number
    max_exp?: number
    limit?: number
  } = {}): Promise<SkillTopResponse> {
    const query = new URLSearchParams()
    if (params.role) query.set('role', params.role)
    if (params.city) query.set('city', params.city)
    if (params.min_exp !== undefined && params.min_exp !== null) query.set('min_exp', String(params.min_exp))
    if (params.max_exp !== undefined && params.max_exp !== null) query.set('max_exp', String(params.max_exp))
    if (params.limit) query.set('limit', String(params.limit))

    const qs = query.toString()
    return request<SkillTopResponse>(`/skills/top${qs ? `?${qs}` : ''}`)
  },

  getSalary(params: { role?: string; city?: string } = {}): Promise<SalaryResponse> {
    const query = new URLSearchParams()
    if (params.role) query.set('role', params.role)
    if (params.city) query.set('city', params.city)

    const qs = query.toString()
    return request<SalaryResponse>(`/salary${qs ? `?${qs}` : ''}`)
  },

  getTopLocations(params: {
    role?: string
    min_exp?: number
    max_exp?: number
    limit?: number
  } = {}): Promise<LocationTopResponse> {
    const query = new URLSearchParams()
    if (params.role) query.set('role', params.role)
    if (params.min_exp !== undefined && params.min_exp !== null) query.set('min_exp', String(params.min_exp))
    if (params.max_exp !== undefined && params.max_exp !== null) query.set('max_exp', String(params.max_exp))
    if (params.limit) query.set('limit', String(params.limit))

    const qs = query.toString()
    return request<LocationTopResponse>(`/locations/top${qs ? `?${qs}` : ''}`)
  },

  getTopCompanies(params: {
    role?: string
    city?: string
    min_exp?: number
    max_exp?: number
    limit?: number
  } = {}): Promise<CompanyTopResponse> {
    const query = new URLSearchParams()
    if (params.role) query.set('role', params.role)
    if (params.city) query.set('city', params.city)
    if (params.min_exp !== undefined && params.min_exp !== null) query.set('min_exp', String(params.min_exp))
    if (params.max_exp !== undefined && params.max_exp !== null) query.set('max_exp', String(params.max_exp))
    if (params.limit) query.set('limit', String(params.limit))

    const qs = query.toString()
    return request<CompanyTopResponse>(`/companies/top${qs ? `?${qs}` : ''}`)
  },

  compareSkillGap(req: SkillGapRequest): Promise<SkillGapResponse> {
    return request<SkillGapResponse>('/gap', {
      method: 'POST',
      body: JSON.stringify(req),
    })
  },
}
