export interface Job {
  id: string;
  title: string;
  companyName: string;
  companyLogo?: string;
  location: string;
  datePosted: Date;
  originalUrl: string;
  skills: string[];
  type?: string;
  level?: string;
  salary?: string;
  isFavorite?: boolean;
}

export interface DetailJob {
  id: string;
  title: string;
  originalUrl: string;
  company: Company;
  location: string;
  datePosted: Date;
  skills: string[];
  jobDescription: string;
  jobRequirements?: string;
  type?: string;
  level?: string;
  salary?: string;
  benefit?: string;
  isExpired?: boolean;
  isFavorite?: boolean;
  isAnalyzed?: boolean;
}

export interface Company {
  name: string;
  logo?: string;
  address?: string;
  description?: string;
}

export interface JobAnalysis extends Job {
  matchScore: number;
  isCreatedCV: boolean;
  weaknesses: string[];
  strengths: string[];
  analyzedAt: Date;
}

export interface JobAnalysisDetail extends JobAnalysis {
  generalFeedback: string;
  roleFeedback: string;
  skillsFeedback: string;
  workExperienceFeedback: string;
  educationFeedback: string;
  languageFeedback: string;
}

export interface JobQueryParams {
  page: number;
  pageSize: number;
  search?: string;
  filterByJobLevel?: string[];
}

export interface JobAnalysisQueryParams {
  page: number;
  pageSize: number;
  search?: string;
}
