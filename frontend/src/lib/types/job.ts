export interface Job {
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
}

export interface Company {
  name: string;
  logo?: string;
  address?: string;
  description?: string;
}
