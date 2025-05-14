import { createContext, useContext } from 'react';
import { JobAnalytic } from '../../lib/types/job';

interface JobAnalysisContextType {
  showJobAnalysis: (analysis: JobAnalytic) => void;
}

export const JobAnalysisContext = createContext<JobAnalysisContextType | undefined>(undefined);

export const useJobAnalysis = () => {
  const context = useContext(JobAnalysisContext);
  if (!context) {
    throw new Error('useJobAnalysis must be used within a JobAnalysisProvider');
  }
  return context;
};