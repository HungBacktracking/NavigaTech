import { JobSearchRequest, JobFavoriteResponse, Job } from "../lib/types/job";
import { PageResponse } from "../lib/types/pagination";
import api from "../lib/clients/axios/api";

export const jobApi = {
  getJobs: async (params: JobSearchRequest): Promise<PageResponse<Job>> => {
    try {
      const searchParams: JobSearchRequest = {
        page: params.page,
        page_size: params.page_size,
        query: params.query || "",
        roles: params.roles || [],
        levels: params.levels || []
      };

      console.log("Search params:", searchParams);
      
      const response = await api.post('/jobs/search', searchParams);
      console.log("Jobs response:", response.data);
      return response.data;
    } catch (error) {
      console.error("Error fetching jobs:", error);
      throw error;
    }
  },

  getRecommendedJobs: async (): Promise<Job[]> => {
    try {
      const response = await api.get('/jobs/recommendations');
      console.log("Recommended jobs response:", response.data);
      return response.data;
    } catch (error) {
      console.error("Error fetching recommended jobs:", error);
      throw error;
    }
  },
  
  toggleFavorite: async (jobId: string, is_favorite: boolean): Promise<{ id: string, is_favorite: boolean }> => {
    try {
      let response;
      if (is_favorite) {
        response = await api.post(`/jobs/${jobId}/delete-favorite`);
      } else {
        response = await api.post(`/jobs/${jobId}/favorite`);
      }
      console.log("Toggle favorite response:", response.data);
      // return response.data;
      return {
        id: jobId,
        is_favorite: !is_favorite,
      };
    } catch (error) {
      console.error("Error toggling favorite job:", error);
      throw error;
    }
  },
  
  getFavoriteJobs: async (params: { page: number, page_size: number }): Promise<PageResponse<JobFavoriteResponse>> => {
    try {
      const response = await api.get('/jobs/favorite', {
        params: {
          page: params.page,
          page_size: params.page_size
        }
      });
      console.log("Favorite jobs response:", response.data);
      return response.data;
    } catch (error) {
      console.error("Error fetching favorite jobs:", error);
      throw error;
    }
  },
  
  getPromptSuggestions: async (): Promise<string[]> => {
    const mockPromptSuggestions = [
      "Find Java Developer jobs in Ho Chi Minh City",
      "Senior Frontend Engineer positions with React",
      "Data Scientist roles that require Python",
      "Remote Software Engineer jobs",
      "Product Manager positions in fintech companies",
      "UX/UI Designer jobs with Figma experience",
      "DevOps Engineer positions with Kubernetes",
      "Machine Learning Engineer jobs"
    ];
    
    // Return random 3 suggestions
    return new Promise<string[]>((resolve) => {
      setTimeout(() => {
        const randomSuggestions = mockPromptSuggestions
          .sort(() => 0.5 - Math.random())
          .slice(0, 3);
        resolve(randomSuggestions);
      }, 500);
    });
  },
  
  getJobRoleOptions: async (): Promise<string[]> => {
    const jobRoles = [
      "Intern",
      "Entry level",
      "Junior",
      "Mid-level",
      "Senior",
      "Lead",
      "Manager",
      "Director",
      "Executive",
      "Principal",
      "Architect",
      "VP",
      "C-level",
      "Fellow",
      "Distinguished Engineer",
      "Staff Engineer",
      "Senior Staff Engineer",
      "Technical Lead",
      "Team Lead",
    ];
    
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(jobRoles);
      }, 500);
    });
  },
  
  getJobTitleOptions: async (): Promise<string[]> => {
    const jobTitleOptions = [
      "Software Engineer",
      "Frontend Developer",
      "Backend Developer",
      "Full Stack Developer",
      "Data Scientist",
      "Machine Learning Engineer",
      "DevOps Engineer",
      "Product Manager",
      "UX/UI Designer",
      "QA Engineer",
      "Business Analyst",
      "Project Manager",
      "Technical Writer",
      "System Administrator",
      "Network Engineer",
      "Cloud Engineer",
      "Security Analyst",
      "Database Administrator",
      "Web Developer",
      "Mobile Developer",
      "Game Developer",
      "Data Engineer",
      "Data Analyst",
      "Research Scientist",
    ];
    
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(jobTitleOptions);
      }, 500);
    });
  },
};
