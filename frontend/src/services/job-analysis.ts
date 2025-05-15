import api from "../lib/clients/axios/api";
import { JobFavoriteResponse } from "../lib/types/job";

export const jobAnalysisApi = {
  async getJobAnalyses(): Promise<JobFavoriteResponse[]> {
    try {
      const response = await api.get('/job-analysis/full');
      console.log('Job analyses response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching job analyses:', error);
      throw error;
    }
  },

  async getJobAnalysis(id: string): Promise<JobFavoriteResponse> {
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
