import { useEffect, useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Layout, Space, Typography } from "antd"
import JobCard from "./components/job-card"
import FullscreenLoader from "../../components/fullscreen-loader"
import { jobApi } from "../../services/job-finder"
import { Job } from "../../lib/types/job"

const { Content } = Layout;
const { Title } = Typography;

export default function JobFindingPage() {
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const { data: jobs, isLoading } = useQuery({
    queryKey: ["jobs"],
    queryFn: jobApi.getJobs,
  });

  useEffect(() => {
    if (jobs && jobs.length > 0 && !selectedJob) {
      setSelectedJob(jobs[0] || null)
    }
  }, [jobs, selectedJob]);

  if (isLoading) {
    return <FullscreenLoader />
  }

  const handleSelectJob = (job: Job) => {
    setSelectedJob(job);
  };

  return (
    <Layout>
      <Content style={{ margin: '24px auto 0 auto' }}>
        <Title level={2} style={{ textAlign: 'center', marginBottom: '24px' }}>
          <span className="app-gradient-text" style={{ fontWeight: 700 }}>Find Your Dream Job</span>
        </Title>
        <Space direction="vertical" size="large">
          {jobs != undefined ? jobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              handleSelectJob={handleSelectJob}
              isSelected={selectedJob?.id === job.id}
              isFavorite={false}
            />
          )) : null}
        </Space>
      </Content>
    </Layout>
  )
}
