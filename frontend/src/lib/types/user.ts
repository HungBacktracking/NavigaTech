export interface User {
  id: string;
  email: string;
  name?: string;
  avatar_url?: string;
  uploaded_resume: boolean;
}

export type UserLoginDto = {
  email: string;
  password: string;
};

export interface BasicInfoFormData {
  email: string;
  name: string;
  headline: string;
  location: string;
  introduction: string;
  phone_number: string;
  linkedin_url: string;
  github_url: string;
}

export interface Skill {
  id: string;
  name: string;
}

export interface Project {
  id: string;
  project_name: string;
  role?: string;
  description?: string;
  achievement?: string;
  start_date?: string;
  end_date?: string;
}

export interface Experience {
  id: string;
  company: string;
  position: string;
  start_date: string;
  end_date: string;
  description: string;
}

export interface Education {
  id: string;
  major: string;
  school_name: string;
  degree_type: string;
  is_current: boolean;
  gpa?: string;
  description?: string;
  start_date?: string;
  end_date?: string;
}

export interface Adward {
  id: string;
  name: string;
  description: string;
  award_date: string;
}

export interface UserDetail {
  id: string;
  email: string;
  name: string;
  avatar_url: string;
  uploaded_resume: boolean;
  headline: string;
  phone_number: string;
  location: string;
  education: string;
  linkedin_url: string;
  github_url: string;
  resume_url: string;
  introduction: string;
  projects: Project[];
  experiences: Experience[];
  educations: Education[];
  skills: Skill[];
  adwards: Adward[];
}
