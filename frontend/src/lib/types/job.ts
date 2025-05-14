import { PageRequest } from "./pagination";

export interface Job {
  id: string;
  from_site: string;
  job_url: string;
  logo_url: string;
  job_name: string;
  job_level?: string;
  company_name: string;
  company_type?: string;
  company_address?: string;
  company_description?: string;
  job_type?: string;
  skills: string;
  location?: string;
  date_posted?: string;
  job_description: string;
  job_requirement: string;
  benefit?: string;
  is_analyze: boolean;
  is_favorite: boolean;
}

export interface FavoriteJobRequest {
  job_id: string;
  user_id: string;
  is_analyze?: boolean;
  is_generated_resume?: boolean;
  is_favorite: boolean;
}

export interface JobAnalytic extends Job {
  id: string;
  job_id: string;
  match_overall: number;
  match_experience: number;
  match_skills: number;
  weaknesses: string;
  strengths: string;
  overall_assessment: string;
  strength_details: string;
  weakness_concerns: string;
  recommendations: string;
  questions: string;
  roadmap: string;
  conclusion: string;
}

export interface JobFavoriteResponse extends Job {
  job_analytics?: JobAnalytic;
}

export interface JobSearchRequest extends PageRequest {
  query: string;
  roles?: string[];
  levels?: string[];
}

export interface JobAnalyticSearchRequest extends PageRequest {
  search?: string;
}
