import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Row, Col, Typography, Space, Flex, message, Pagination, Skeleton, Card, Image } from "antd";
import { ReloadOutlined } from "@ant-design/icons";
import JobCard from "./components/job-card";
import { jobApi, JobQueryParams } from "../../services/job-finder";
import { Job } from "../../lib/types/job";
import JobDetail from "./components/job-detail";
import SuggestionItem from "./components/suggestion-item";
import AIButton from "../../components/ai-button";
import selectionSvg from "../../assets/selection.svg";
import emptyStateSvg from "../../assets/empty-state.svg";
import AISearchBar from "./components/ai-search-bar";

const { Title } = Typography;

export default function JobFindingPage() {
  const queryClient = useQueryClient();
  const [messageApi, contextHolder] = message.useMessage();
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [queryParams, setQueryParams] = useState<JobQueryParams>({
    page: 1,
    pageSize: 10,
    search: "",
  });
  const [searchValue, setSearchValue] = useState("");
  const [navbarHeight, setNavbarHeight] = useState(0);
  const [lastPaginationData, setLastPaginationData] = useState({
    page: 1,
    pageSize: 5,
    total: 0,
  });

  const {
    data: jobsData,
    isLoading: isJobsLoading,
  } = useQuery({
    queryKey: ['jobs', queryParams],
    queryFn: () => jobApi.getJobs(queryParams),
  });

  const { data: suggestionItems = [], isLoading: isSuggestionsLoading } = useQuery({
    queryKey: ['suggestions'],
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

      messageApi.success(`Job ${isFavorite ? 'added to' : 'removed from'} favorites`);

      if (selectedJob && selectedJob.id === jobId) {
        setSelectedJob({ ...selectedJob, isFavorite });
      }
    },
    onError: () => {
      messageApi.error("Failed to update favorites. Please try again.");
    }
  });

  const { mutate: refreshSuggestions, isPending: isRefreshingSuggestions } = useMutation({
    mutationFn: jobApi.getPromptSuggestions,
    onSuccess: (newSuggestions) => {
      queryClient.setQueryData(['suggestions'], newSuggestions);
      messageApi.success("Suggestions refreshed successfully");
    },
    onError: () => {
      messageApi.error("Failed to refresh suggestions. Please try again.");
    }
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

  useEffect(() => {
    const navbar = document.querySelector('header');
    const navbarHeightValue = navbar ? navbar.getBoundingClientRect().height + 16 : 48;
    setNavbarHeight(navbarHeightValue);
  }, []);

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

  const handlePageChange = (page: number) => {
    setQueryParams(prev => ({ ...prev, page }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSearch = () => {
    setQueryParams(prev => ({ ...prev, page: 1, search: searchValue }));
  };

  return (
    <>
      {contextHolder}
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
              onClick={() => refreshSuggestions()}
            >
              Refresh
            </AIButton>
          </Flex>
          {isSuggestionsLoading ? (
            <Skeleton active paragraph={{ rows: 2 }} style={{ width: 800 }} />
          ) : (
            suggestionItems.map((item, index) => (
              <SuggestionItem
                key={index}
                content={item}
                handleClick={() => {
                  setSearchValue(item);
                }}
              />
            ))
          )}
        </Space>
        <AISearchBar
          searchValue={searchValue}
          setSearchValue={setSearchValue}
          handleSearch={handleSearch}
        />
      </Flex>

      <Row gutter={16} style={{ height: "100%", marginTop: 24 }}>
        <Col
          span={9}
        >
          <Space direction="vertical" size={12} style={{ width: "100%", borderRadius: 8 }}>
            {isJobsLoading ? (
              Array(5).fill(0).map((_, index) => (
                <Card
                  key={index}
                  style={{ padding: '4px', borderRadius: '16px' }}
                  title={
                    <Space size="large">
                      <Skeleton.Node active style={{ width: 40, height: 40, borderRadius: 4 }} />
                      <Skeleton.Node active style={{ height: 24 }} />
                    </Space>

                  }
                >
                  <Skeleton active paragraph={{ rows: 4 }} />
                </Card>
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
              <div style={{ textAlign: 'center', padding: '0 0 24px 0', background: '#fff', borderRadius: 16 }}>
                <Image
                  src={emptyStateSvg}
                  alt="No jobs found"
                  preview={false}
                  style={{ width: 200, height: 200 }}
                />
                <Title level={5} style={{ margin: 0 }}>No jobs found</Title>
                <p style={{ margin: 0 }}>Try adjusting your search criteria or check back later.</p>
              </div>
            )}

            <Flex justify="center" style={{ marginTop: 16, marginBottom: 24 }}>
              <Pagination
                current={isJobsLoading ? lastPaginationData.page : jobsData!.page}
                pageSize={isJobsLoading ? lastPaginationData.pageSize : jobsData!.pageSize}
                total={isJobsLoading ? lastPaginationData.total : jobsData!.total}
                onChange={handlePageChange}
                showSizeChanger={false}
                disabled={isJobsLoading}
              />
            </Flex>
          </Space>
        </Col>

        <Col
          span={15}
          style={{
            position: 'sticky',
            top: navbarHeight,
            height: `calc(100vh - ${navbarHeight}px)`,
            paddingBottom: 8,
          }}
        >
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
            <div style={{ height: '70vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
              <Image
                src={selectionSvg}
                alt="No job selected"
                preview={false}
              />
              <Title level={4} style={{ textAlign: "center", margin: 0 }}>
                Select a job to view details
              </Title>
            </div>
          )}
        </Col>
      </Row>
    </>
  );
}
