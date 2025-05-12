import { Education, Project, Skill, UserDetail, Experience } from "../lib/types/user";

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

export const mockUserDetail: UserDetail = {
  id: "1",
  email: "user@example.com",
  name: "John Doe",
  avatar_url: "",
  uploaded_resume: true,
  headline: "Senior Software Developer",
  phone_number: "+1 (555) 123-4567",
  location: "San Francisco, CA",
  education: "Computer Science",
  linkedin_url: "https://linkedin.com/in/johndoe",
  github_url: "https://github.com/johndoe",
  resume_url: "",
  introduction: "Experienced software developer with expertise in React, Node.js, and cloud technologies.",
  projects: [
    {
      id: "p1",
      project_name: "E-commerce Platform",
      role: "Lead Developer",
      description: "Built a scalable e-commerce platform using React and Node.js.",
      achievement: "Increased sales by 30% within 3 months of launch.",
      start_date: "2022-01-01",
      end_date: "2023-02-15"
    },
    {
      id: "p2",
      project_name: "Mobile Banking App",
      role: "Frontend Developer",
      description: "Developed a responsive mobile banking application with React Native.",
      achievement: "Achieved 4.8/5 rating on app stores.",
      start_date: "2021-03-10",
      end_date: "2022-05-20"
    }
  ],
  experiences: [
    {
      id: "e1",
      company: "Tech Solutions Inc.",
      position: "Senior Developer",
      start_date: "2021-06-01",
      end_date: "",
      description: "Leading a team of developers to build enterprise-level applications."
    },
    {
      id: "e2",
      company: "Digital Creations",
      position: "Software Engineer",
      start_date: "2018-03-15",
      end_date: "2021-05-30",
      description: "Developed and maintained multiple web applications using React and TypeScript."
    }
  ],
  educations: [
    {
      id: "ed1",
      major: "Computer Science",
      school_name: "University of California, Berkeley",
      degree_type: "Bachelor's Degree",
      is_current: false,
      gpa: "3.8",
      description: "Graduated with honors",
      start_date: "2014-09-01",
      end_date: "2018-05-15"
    }
  ],
  skills: [
    { id: "s1", name: "React" },
    { id: "s2", name: "TypeScript" },
    { id: "s3", name: "Node.js" },
    { id: "s4", name: "AWS" },
    { id: "s5", name: "GraphQL" }
  ],
  adwards: [
    {
      id: "a1",
      name: "Developer of the Year",
      description: "Recognized for outstanding contribution to open-source projects",
      award_date: "2022-12-15"
    }
  ]
};

export const userAPI = {
  getUserDetail: async (userId: string): Promise<UserDetail> => {
    console.log(`Fetching user details for ID: ${userId}`);
    await new Promise(resolve => setTimeout(resolve, 500));
    return mockUserDetail;
  },
  
  updateBasicInfo: async (userId: string, basicInfo: BasicInfoFormData): Promise<BasicInfoFormData> => {
    console.log(`Updating basic info for user ID: ${userId}`, basicInfo);
    
    await new Promise(resolve => setTimeout(resolve, 500));
    return basicInfo;
  },

  updateSkills: async (userId: string, skills: string[]): Promise<Skill[]> => {
    console.log(`Updating skills for user ID: ${userId}`, skills);
    await new Promise(resolve => setTimeout(resolve, 500));
    mockUserDetail.skills = skills.map((skill, index) => ({ id: `s${index + 1}`, name: skill }));
    return mockUserDetail.skills;
  },

  addEducation: async (userId: string, education: Education): Promise<Education> => {
    console.log(`Adding education record for user ID: ${userId}`, education);
    await new Promise(resolve => setTimeout(resolve, 500));
    mockUserDetail.educations.push(education);
    return education;
  },
  
  updateEducation: async (userId: string, education: Education): Promise<Education> => {
    console.log(`Updating education record with ID: ${education.id} for user ID: ${userId}`, education);
    await new Promise(resolve => setTimeout(resolve, 500));
    const index = mockUserDetail.educations.findIndex(ed => ed.id === education.id);
    if (index !== -1) {
      mockUserDetail.educations[index] = education;
    }
    return education;
  },
  
  deleteEducation: async (userId: string, educationId: string): Promise<boolean> => {
    console.log(`Deleting education record with ID: ${educationId} for user ID: ${userId}`);
    await new Promise(resolve => setTimeout(resolve, 500));
    const index = mockUserDetail.educations.findIndex(ed => ed.id === educationId);
    if (index !== -1) {
      mockUserDetail.educations.splice(index, 1);
    }
    return true;
  },

  addExperience: async (userId: string, experience: Experience): Promise<Experience> => {
    console.log(`Adding experience record for user ID: ${userId}`, experience);
    await new Promise(resolve => setTimeout(resolve, 500));
    mockUserDetail.experiences.push(experience);
    return experience;
  },
  
  updateExperience: async (userId: string, experience: Experience): Promise<Experience> => {
    console.log(`Updating experience record with ID: ${experience.id} for user ID: ${userId}`, experience);
    await new Promise(resolve => setTimeout(resolve, 500));
    const index = mockUserDetail.experiences.findIndex(exp => exp.id === experience.id);
    if (index !== -1) {
      mockUserDetail.experiences[index] = experience;
    }
    return experience;
  },
  
  deleteExperience: async (userId: string, experienceId: string): Promise<boolean> => {
    console.log(`Deleting experience record with ID: ${experienceId} for user ID: ${userId}`);
    await new Promise(resolve => setTimeout(resolve, 1000));
    const index = mockUserDetail.experiences.findIndex(exp => exp.id === experienceId);
    if (index !== -1) {
      mockUserDetail.experiences.splice(index, 1);
    }
    return true;
  },

  addProject: async (userId: string, project: Project): Promise<Project> => {
    console.log(`Adding project record for user ID: ${userId}`, project);
    await new Promise(resolve => setTimeout(resolve, 500));
    mockUserDetail.projects.push(project);
    return project;
  },
  
  updateProject: async (userId: string, project: Project): Promise<Project> => {
    console.log(`Updating project record with ID: ${project.id} for user ID: ${userId}`, project);
    await new Promise(resolve => setTimeout(resolve, 500));
    const index = mockUserDetail.projects.findIndex(pr => pr.id === project.id);
    if (index !== -1) {
      mockUserDetail.projects[index] = project;
    }
    return project;
  },
  
  deleteProject: async (userId: string, projectId: string): Promise<boolean> => {
    console.log(`Deleting project record with ID: ${projectId} for user ID: ${userId}`);
    await new Promise(resolve => setTimeout(resolve, 500));
    const index = mockUserDetail.projects.findIndex(pr => pr.id === projectId);
    if (index !== -1) {
      mockUserDetail.projects.splice(index, 1);
    }
    return true;
  }
};
