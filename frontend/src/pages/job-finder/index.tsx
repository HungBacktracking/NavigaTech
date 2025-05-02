import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Row, Col, Typography, Space, Flex, message, Pagination, Input, Spin, Skeleton } from "antd";
import { ReloadOutlined, SearchOutlined } from "@ant-design/icons";
import JobCard from "./components/job-card";
import { jobApi, JobQueryParams } from "../../services/job-finder";
import { Job } from "../../lib/types/job";
import JobDetail from "./components/job-detail";
import SuggestionItem from "./components/suggestion-item";
import AIButton from "../../components/ai-button";

const { Title } = Typography;
const { Search } = Input;

export default function JobFindingPage() {
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [queryParams, setQueryParams] = useState<JobQueryParams>({
    page: 1,
    pageSize: 5,
    search: "",
  });
  const queryClient = useQueryClient();

  const [lastPaginationData, setLastPaginationData] = useState({
    page: 1,
    pageSize: 5,
    total: 0,
  });

  const {
    data: jobsData,
    isLoading: isJobsLoading,
  } = useQuery({
    queryKey: ["jobs", queryParams],
    queryFn: () => jobApi.getJobs(queryParams),
  });

  useEffect(() => {
    if (jobsData) {
      setLastPaginationData({
        page: jobsData.page,
        pageSize: jobsData.pageSize,
        total: jobsData.total,
      });
    }
  }, [jobsData]);

  const { data: suggestionItems = [], isLoading: isSuggestionsLoading } = useQuery({
    queryKey: ["suggestions"],
    queryFn: jobApi.getPromptSuggestions,
  });

  const { mutate: toggleFavorite } = useMutation({
    mutationFn: (jobId: string) => jobApi.toggleFavorite(jobId),
    onSuccess: ({ jobId, isFavorite }) => {
      queryClient.setQueryData(["jobs", queryParams], (oldData: any) => {
        if (!oldData) return oldData;

        return {
          ...oldData,
          items: oldData.items.map((job: Job) =>
            job.id === jobId ? { ...job, isFavorite } : job
          )
        };
      });

      message.success(`Job ${isFavorite ? 'added to' : 'removed from'} favorites`);

      if (selectedJob && selectedJob.id === jobId) {
        setSelectedJob({ ...selectedJob, isFavorite });
      }
    },
    onError: () => {
      message.error("Failed to update favorites. Please try again.");
    }
  });

  const { mutate: refreshSuggestions, isPending: isRefreshingSuggestions } = useMutation({
    mutationFn: jobApi.getPromptSuggestions,
    onSuccess: (newSuggestions) => {
      queryClient.setQueryData(['suggestions'], newSuggestions);
      message.success("Suggestions refreshed successfully");
    },
    onError: () => {
      message.error("Failed to refresh suggestions. Please try again.");
    }
  });

  useEffect(() => {
    if (jobsData) {
      if (jobsData.items.length > 0 && !selectedJob) {
        setSelectedJob(jobsData.items[0] || null);
      } else if (jobsData.items.length > 0 && selectedJob) {
        const stillExists = jobsData.items.some(job => job.id === selectedJob.id);
        if (!stillExists) {
          setSelectedJob(jobsData.items[0] || null);
        } else {
          const updatedJob = jobsData.items.find(job => job.id === selectedJob.id);
          if (updatedJob) {
            setSelectedJob(updatedJob);
          }
        }
      } else if (jobsData.items.length === 0) {
        setSelectedJob(null);
      }
    }
  }, [jobsData, selectedJob]);

  const handleRefreshSuggestions = () => {
    refreshSuggestions();
  };

  const handlePageChange = (page: number) => {
    setQueryParams(prev => ({ ...prev, page }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSearch = (value: string) => {
    setQueryParams(prev => ({ ...prev, page: 1, search: value }));
  };

  const shouldShowPagination = () => {
    if (isJobsLoading) {
      return lastPaginationData.total > 0;
    } else {
      return jobsData && jobsData.total > 0;
    }
  };

  return (
    <div style={{ margin: "24px auto 0 auto" }}>
      <Flex vertical align="center">
        <Title level={2} style={{ textAlign: "center", margin: 0 }}>
          <span className="app-gradient-text" style={{ fontWeight: 700 }}>
            Find Your Dream Job
          </span>
        </Title>
        <Title level={4} style={{ textAlign: "center", margin: 0 }}>
          Discover opportunities that match your skills and preferences with our <span className="app-gradient-text" style={{ fontWeight: 600 }}>AI-Powered</span> job search
        </Title>
        <Space direction="vertical" size={12} style={{ width: isSuggestionsLoading ? 800 : undefined, maxWidth: "800px", marginTop: 16 }}>
          <Flex horizontal justify="space-between" align="center" style={{ width: "100%" }}>
            <Title level={5} style={{ textAlign: "left", margin: 0 }}>
              Suggestions for you:
            </Title>
            <AIButton
              icon={<ReloadOutlined />}
              loading={isRefreshingSuggestions}
              onClick={handleRefreshSuggestions}
            >
              Refresh
            </AIButton>
          </Flex>
          {isSuggestionsLoading ? (
            <Spin
              size="large"
              style={{ margin: "0 auto", display: "block" }}
              tip="Loading suggestions..."
            />
          ) : (
            suggestionItems.map((item, index) => (
              <SuggestionItem
                key={index}
                content={item}
                handleClick={() => {
                  console.log(`Suggestion clicked: ${item}`);
                }}
              />
            ))
          )}
        </Space>
      </Flex>
      <Row gutter={16} style={{ height: "100%", marginTop: 24 }}>
        <Col span={9}>
          <Space direction="vertical" size={16} style={{ width: "100%" }}>
            <Search
              placeholder="Search jobs by title, company, or location"
              onSearch={handleSearch}
              enterButton={<SearchOutlined />}
              allowClear
              size="large"
            />

            <Space direction="vertical" size={12} style={{ width: "100%", borderRadius: 8, padding: 8 }} className="scrollbar-custom">
              {isJobsLoading ? (
                Array(5).fill(0).map((_, index) => (
                  <div key={index} style={{ padding: '16px', border: '1px solid #f0f0f0', borderRadius: '8px' }}>
                    <Skeleton active avatar paragraph={{ rows: 4 }} />
                  </div>
                ))
              ) : (
                jobsData?.items?.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    handleToggleFavorite={(e: MouseEvent) => {
                      e.stopPropagation();
                      toggleFavorite(job.id);
                    }}
                    handleSelectJob={() => setSelectedJob(job)}
                    isSelected={selectedJob?.id === job.id}
                    isFavorite={job.isFavorite || false}
                  />
                ))
              )}

              {!isJobsLoading && jobsData?.items?.length === 0 && (
                <div style={{ textAlign: 'center', padding: '24px 0' }}>
                  <p>No jobs found matching your search criteria</p>
                </div>
              )}

              {shouldShowPagination() && (
                <Flex justify="center" style={{ marginTop: 16 }}>
                  <Pagination
                    current={isJobsLoading ? lastPaginationData.page : jobsData!.page}
                    pageSize={isJobsLoading ? lastPaginationData.pageSize : jobsData!.pageSize}
                    total={isJobsLoading ? lastPaginationData.total : jobsData!.total}
                    onChange={handlePageChange}
                    showSizeChanger={false}
                    disabled={isJobsLoading}
                  />
                </Flex>
              )}
            </Space>
          </Space>
        </Col>
        <Col span={15}>
          {selectedJob ? (
            <JobDetail
              job={selectedJob}
              isFavorite={selectedJob.isFavorite || false}
              handleToggleFavorite={(e: MouseEvent) => {
                e.stopPropagation();
                toggleFavorite(selectedJob.id);
              }}
            />
          ) : (
            <div style={{ height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <Title level={5} style={{ textAlign: "center", margin: 0 }}>
                Select a job to view details
              </Title>
            </div>
          )}
        </Col>
      </Row>
    </div>
  );
}
