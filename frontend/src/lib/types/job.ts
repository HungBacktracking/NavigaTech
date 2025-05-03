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
  salary?: string;
  benefit?: string;
  isExpired?: boolean;
  isFavorite?: boolean;
}

export interface Company {
  name: string;
  logo?: string;
  address?: string;
  description?: string;
}

export interface JobQueryParams {
  page: number;
  pageSize: number;
  search?: string;
  filterByJobType?: string[];
}
