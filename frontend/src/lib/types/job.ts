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
  resume_url?: string;
  is_favorite: boolean;
}

export interface FavoriteJobRequest {
  job_id: string;
  user_id: string;
  is_analyze?: boolean;
  is_generated_resume?: boolean;
  is_favorite: boolean;
}

export interface JobAnalytic {
  general_score: number;
  general_feedback: string;
  skill_feedback: string;
  role_feedback: string;
  experience_feedback: string;
  benefit_feedback: string;
  education_feedback: string;
}

export interface JobFavoriteResponse extends Job {
  job_analytics?: JobAnalytic;
}

export interface JobSearchRequest extends PageRequest {
  query: string;
  roles?: string[];
  levels?: string[];
}
