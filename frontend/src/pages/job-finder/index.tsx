import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Row, Col, Typography, Space, Divider } from "antd";
import JobCard from "./components/job-card";
import FullscreenLoader from "../../components/fullscreen-loader";
import { jobApi } from "../../services/job-finder";
import { Job } from "../../lib/types/job";
import JobDetail from "./components/job-detail";

const { Title } = Typography;

export default function JobFindingPage() {
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const { data: jobs, isLoading } = useQuery({
    queryKey: ["jobs"],
    queryFn: jobApi.getJobs,
  });

  useEffect(() => {
    if (jobs && jobs.length > 0 && !selectedJob) {
      setSelectedJob(jobs[0] || null);
    }
  }, [jobs, selectedJob]);

  if (isLoading) {
    return <FullscreenLoader />;
  }

  const handleToggleFavorite = (jobId: string) => {
    console.log(`Toggling favorite for job ID: ${jobId}`);
  }

  const handleSelectJob = (job: Job) => {
    setSelectedJob(job);
  };

  return (
    <div style={{ margin: "24px auto 0 auto" }}>
      <Title level={2} style={{ textAlign: "center", marginBottom: "24px" }}>
        <span className="app-gradient-text" style={{ fontWeight: 700 }}>
          Find Your Dream Job
        </span>
      </Title>
      <Row gutter={16} style={{ height: "100%" }}>
        <Col span={9} >
          <Space direction="vertical" size={12} style={{ width: "100%", borderRadius: 8 }} className="scrollbar-custom">
            {jobs?.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                handleToggleFavorite={(e: MouseEvent) => {
                  e.stopPropagation();
                  handleToggleFavorite(job.id);
                }}
                handleSelectJob={handleSelectJob}
                isSelected={selectedJob?.id === job.id}
                isFavorite={false}
              />
            ))}
            {jobs?.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                handleToggleFavorite={(e: MouseEvent) => {
                  e.stopPropagation();
                  handleToggleFavorite(job.id);
                }}
                handleSelectJob={handleSelectJob}
                isSelected={selectedJob?.id === job.id}
                isFavorite={false}
              />
            ))}
          </Space>
        </Col>
        <Col span={15}>
          {selectedJob ? (
            <JobDetail 
              job={selectedJob}
              isFavorite={false}
              handleToggleFavorite={(e: MouseEvent) => {
                e.stopPropagation();
                handleToggleFavorite(selectedJob.id);
              }}
            />
          ) : (
            <div>No job selected</div>
          )}
        </Col>
      </Row>
    </div>
  );
}
