/**
 * frontend/src/lib/types.ts
 * Typed schemas matching FastAPI backend models.
 */

export interface JobItem {
  id: number;
  job_uid: string;
  title: string;
  role: string;
  company: string;
  location: string;
  city: string;
  min_exp: number;
  max_exp: number;
  salary_min_inr: number | null;
  salary_max_inr: number | null;
  salary_median_inr: number | null;
  salary_min_lpa: number | null;
  salary_max_lpa: number | null;
  salary_median_lpa: number | null;
  description: string;
  posted_date: string | null;
  skills: string[];
}

export interface JobListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: JobItem[];
}

export interface RoleItem {
  role: string;
  posting_count: number;
  percentage_of_all_jobs: number;
  median_salary_lpa: number | null;
  sample_size: number;
}

export interface RoleListResponse {
  total_postings: number;
  roles: RoleItem[];
}

export interface SkillDemanded {
  skill: string;
  category: string;
  mention_count: number;
  percentage: number;
  sample_size: number;
}

export interface SkillTopResponse {
  role: string | null;
  city: string | null;
  sample_size: number;
  skills: SkillDemanded[];
}

export interface SalaryByExperienceBand {
  exp_band: string;
  min_exp: number;
  max_exp: number;
  sample_size: number;
  median_lpa: number | null;
  min_lpa: number | null;
  max_lpa: number | null;
  median_inr: number | null;
  min_inr: number | null;
  max_inr: number | null;
}

export interface SalaryResponse {
  role: string | null;
  city: string | null;
  overall_sample_size: number;
  overall_median_lpa: number | null;
  bands: SalaryByExperienceBand[];
}

export interface LocationItem {
  city: string;
  posting_count: number;
  percentage: number;
  median_salary_lpa: number | null;
  sample_size: number;
}

export interface LocationTopResponse {
  role: string | null;
  total_postings: number;
  locations: LocationItem[];
}

export interface CompanyItem {
  company: string;
  posting_count: number;
  percentage: number;
  median_salary_lpa: number | null;
  sample_size: number;
}

export interface CompanyTopResponse {
  role: string | null;
  city: string | null;
  total_postings: number;
  companies: CompanyItem[];
}

export interface MatchedSkillItem {
  skill: string;
  category: string;
  mention_count: number;
  demand_percentage: number;
}

export interface MissingSkillItem {
  skill: string;
  category: string;
  mention_count: number;
  demand_percentage: number;
  importance_rank: number;
}

export interface SkillGapRequest {
  role: string;
  skills: string[];
  city?: string | null;
  min_exp?: number | null;
  max_exp?: number | null;
}

export interface SkillGapResponse {
  role: string;
  sample_size: number;
  user_skills_normalized: string[];
  matched_skills: MatchedSkillItem[];
  missing_skills: MissingSkillItem[];
  match_percentage: number;
  total_demanded_skills: number;
  summary_insight: string;
}
