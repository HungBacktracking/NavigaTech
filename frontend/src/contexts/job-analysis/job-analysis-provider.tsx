import React, { useState } from 'react';
import { Modal } from 'antd';
import { JobFavoriteResponse } from '../../lib/types/job';
import JobAnalysisDetail from '../../pages/job-analysis/components/job-analysis-detail';
import { JobAnalysisContext } from './job-analysis-context';

export const JobAnalysisProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [processedJobAnalysis, setProcessedJobAnalysis] = useState<JobFavoriteResponse | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  const showJobAnalysis = (analysis: JobFavoriteResponse) => {
    setProcessedJobAnalysis(analysis);
    setIsDetailModalOpen(true);
  };

  return (
    <JobAnalysisContext.Provider value={{ showJobAnalysis }}>
      {children}
      <Modal
        title={null}
        open={isDetailModalOpen}
        footer={null}
        onCancel={() => setIsDetailModalOpen(false)}
        destroyOnHidden
        width={1000}
        style={{ top: 20, borderRadius: 16 }}
      >
        <JobAnalysisDetail analytic={processedJobAnalysis} />
      </Modal>
    </JobAnalysisContext.Provider>
  );
};