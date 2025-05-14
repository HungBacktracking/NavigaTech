import api from "../lib/clients/axios/api";
import { JobAnalytic, JobAnalyticSearchRequest } from "../lib/types/job";
import { PageResponse } from "../lib/types/pagination";

export const jobAnalysisApi = {
  async getJobAnalyses(params: JobAnalyticSearchRequest): Promise<PageResponse<JobAnalytic>> {
    try {
      const response = await api.get('/job-analysis', { 
        params
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching job analyses:', error);
      throw error;
    }
  },

  async getJobAnalysis(id: string): Promise<JobAnalytic> {
    try {
      const response = await api.get(`/job-analysis/${id}`);
      console.log(`Job analysis response for ID ${id}:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`Error fetching job analysis with ID ${id}:`, error);
      throw error;
    }
  },

  async analyzeJob(jobId: string): Promise<{ message: string, task_id: string }> {
    try {
      const response = await api.post(`/job-analysis/${jobId}`);
      
      return response.data;
    } catch (error) {
      console.error(`Error creating job analysis for job ID ${jobId}:`, error);
      throw error;
    }
  },

  async deleteJobAnalysis(id: string): Promise<{ message: string }> {
    try {
      const response = await api.delete(`/job-analysis/${id}`);
      
      return response.data;
    } catch (error) {
      console.error(`Error deleting job analysis with ID ${id}:`, error);
      throw error;
    }
  }

};
