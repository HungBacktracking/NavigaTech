import { MouseEvent, useEffect, useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Row, Col, Typography, Space, Flex, message, Pagination, Skeleton, Card, Image, theme } from "antd";
import { ReloadOutlined } from "@ant-design/icons";
import { motion, AnimatePresence } from "framer-motion";
import JobCard from "./components/job-card";
import { jobApi } from "../../services/job-finder";
import { Job, JobAnalytic, JobSearchRequest } from "../../lib/types/job";
import JobDetail from "./components/job-detail";
import SuggestionItem from "./components/suggestion-item";
import AIButton from "../../components/ai-button";
import selectionSvg from "../../assets/selection.svg";
import emptyStateSvg from "../../assets/empty-state.svg";
import AISearchBar from "./components/ai-search-bar";
import MultiChoiceFilter from "./components/multi-choice-filter";
import { jobAnalysisApi } from "../../services/job-analysis";
import { useJobAnalysis } from "../../contexts/job-analysis/job-analysis-context";

const { Title } = Typography;

// Animation variants
const searchContainerVariants = {
  hidden: { opacity: 0, height: 0, marginTop: 0 },
  visible: { opacity: 1, height: "auto", marginTop: 16, transition: { duration: 0.3 } },
  exit: { opacity: 0, height: 0, marginTop: 0, transition: { duration: 0.3 } }
};

export default function JobFindingPage() {
  const { token } = theme.useToken();
  const queryClient = useQueryClient();
  const [messageApi, contextHolder] = message.useMessage({
    top: 50,
    duration: 2,
    maxCount: 3,
  });
  const { showJobAnalysis } = useJobAnalysis();
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [searchValue, setSearchValue] = useState("");
  const [navbarHeight, setNavbarHeight] = useState(0);
  const [queryParams, setQueryParams] = useState<JobSearchRequest>({
    page: 1,
    page_size: 10,
    query: "",
    levels: [],
    roles: [],
  });
  const [lastPaginationData, setLastPaginationData] = useState({
    page: 1,
    page_size: 10,
    total: 0,
  });
  const [selectedJobTitles, setSelectedJobTitles] = useState<string[]>([]);
  const [selectedJobLevels, setSelectedJobLevels] = useState<string[]>([]);
  const [analyzingJobIds, setAnalyzingJobIds] = useState<string[]>([]);
  const [isRecommendationMode, setIsRecommendationMode] = useState(false);

  const { data: jobsData, isLoading: isJobsLoading } = useQuery({
    queryKey: ['jobs', queryParams, isRecommendationMode],
    queryFn: () => {
      if (isRecommendationMode) {
        return jobApi.getRecommendedJobs({
          page: queryParams.page,
          page_size: queryParams.page_size
        });
      } else {
        return jobApi.getJobs(queryParams);
      }
    }
  });

  const { data: suggestionItems, isLoading: isSuggestionsLoading, isFetching: isSuggestionsFetching, refetch: refreshSuggestions } = useQuery({
    queryKey: ['suggestions'],
    queryFn: jobApi.getPromptSuggestions,
  });

  const { data: jobRoles, isLoading: isJobLevelsLoading } = useQuery({
    queryKey: ['jobLevelOptions'],
    queryFn: jobApi.getJobRoleOptions,
  });

  const { data: jobTitles, isLoading: isJobTitlesLoading } = useQuery({
    queryKey: ['jobTitleOptions'],
    queryFn: jobApi.getJobTitleOptions,
  });

  const { mutate: toggleFavorite } = useMutation({
    mutationFn: ({ jobId, isFavorite }: { jobId: string, isFavorite: boolean }) => {
      return jobApi.toggleFavorite(jobId, isFavorite);
    },
    onSuccess: (data) => {
      const { id: jobId, is_favorite: isFavorite } = data;

      const updatedJobs = jobsData?.items.map((job: Job) => {
        if (job.id === jobId) {
          return { ...job, is_favorite: isFavorite };
        }
        return job;
      });

      queryClient.setQueryData(['jobs', queryParams, isRecommendationMode], {
        ...jobsData,
        items: updatedJobs,
      });

      messageApi.success(`Job ${isFavorite ? 'added to' : 'removed from'} favorites`);
    },
    onError: () => {
      messageApi.error("Failed to update favorites. Please try again.");
    }
  });

  const { mutate: analyzeJobMutation } = useMutation({
    mutationFn: (jobId: string) => jobAnalysisApi.analyzeJob(jobId),
    onMutate: (jobId) => {
      setAnalyzingJobIds(prev => [...prev, jobId]);
    },
    onSuccess: (result) => {
      if (result) {
        messageApi.success("Job is being processed in the background. You will be notified when it is ready.");
        queryClient.invalidateQueries({ queryKey: ['jobAnalyses'] });
      } else {
        messageApi.error("Failed to analyze job. The job may be already analyzed!");
      }
    },
    onError: () => {
      messageApi.error("Failed to analyze job. The job may be already analyzed!");
    },
    onSettled: (_, __, jobId) => {
      setAnalyzingJobIds(prev => prev.filter(id => id !== jobId));
    }
  });

  const selectedJob = useMemo(() => {
    return jobsData?.items?.find((job: Job) => job.id === selectedJobId) || null;
  }, [jobsData, selectedJobId]);

  useMemo(() => {
    if (jobsData && !isRecommendationMode) {
      setLastPaginationData({
        page: (jobsData as any).page,
        page_size: (jobsData as any).page_size,
        total: (jobsData as any).total,
      });
    }
  }, [jobsData, isRecommendationMode]);

  useMemo(() => {
    const navbar = document.querySelector('header');
    const navbarHeightValue = navbar ? navbar.getBoundingClientRect().height + 16 : 48;
    setNavbarHeight(navbarHeightValue);
  }, []);

  useEffect(() => {
      setSelectedJobId(jobsData?.items[0]?.id || null);
  }, [jobsData]);

  const handlePageChange = (page: number) => {
    setQueryParams(prev => ({ ...prev, page }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSearch = () => {
    setQueryParams(prev => ({ ...prev, page: 1, query: searchValue }));
  };

  const handleLevelFilterChange = (selectedLevels: string[]) => {
    setSelectedJobLevels(selectedLevels);
    if (selectedLevels.length > 0) {
      setQueryParams(prev => ({
        ...prev,
        page: 1,
        levels: selectedLevels,
      }));
    } else if (selectedLevels.length === 0 && queryParams.levels) {
      setQueryParams(prev => ({ ...prev, page: 1, levels: [] }));
    }
  };

  const handleJobTitleFilterChange = (selectedTitles: string[]) => {
    setSelectedJobTitles(selectedTitles);
    if (selectedTitles.length > 0) {
      setQueryParams(prev => ({
        ...prev,
        page: 1,
        roles: selectedTitles
      }));
    } else if (selectedTitles.length === 0 && queryParams.roles?.length) {
      setQueryParams(prev => ({ ...prev, page: 1, roles: [] }));
    }
  };

  const handleAnalyzeJob = (jobId: string) => {
    if (!jobId) return;
    analyzeJobMutation(jobId);
  };

  const handleViewModeChange = (checked: boolean) => {
    setIsRecommendationMode(checked);
    setQueryParams(prev => ({ ...prev, page: 1 }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleViewJobAnalysis = (jobAnalysis: JobAnalytic) => {
    showJobAnalysis(jobAnalysis);
  }

  return (
    <>
      {contextHolder}
      <Flex vertical align="center">
        <Title level={2} style={{ textAlign: "center", margin: 0 }}>
          <span className="app-gradient-text" style={{ fontWeight: 700 }}>
            Find Your Dream Job
          </span>
        </Title>

        <Title level={4} style={{ textAlign: "center", margin: '8px 0 0' }}>
          Discover opportunities that match your skills and preferences with our <span className="app-gradient-text" style={{ fontWeight: 600 }}>AI-Powered</span> job search
        </Title>

        <Flex
          justify="space-between"
          align="center"
          style={{ margin: '16px 0' }}
        >
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div
              style={{
                background: token.colorBgContainer,
                borderRadius: '32px',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                display: 'flex',
                position: 'relative',
                gap: 8,
              }}
            >
              <div
                style={{
                  position: 'absolute',
                  height: '100%',
                  background: token.colorPrimary,
                  borderRadius: '32px',
                  transition: 'all 0.3s ease',
                  transform: isRecommendationMode ? 'translateX(calc(50% - 32px))' : 'translateX(0)',
                  width: isRecommendationMode ? '76%' : '24%',
                  zIndex: 0,
                }}
              />
              <div
                onClick={() => handleViewModeChange(false)}
                style={{
                  padding: '8px 16px',
                  textAlign: 'center',
                  fontWeight: 500,
                  cursor: 'pointer',
                  color: isRecommendationMode ? token.colorText : token.colorTextLightSolid,
                  zIndex: 1,
                  position: 'relative',
                  transition: 'color 0.3s ease',
                }}
              >
                All
              </div>
              <div
                onClick={() => handleViewModeChange(true)}
                style={{
                  padding: '8px 16px',
                  textAlign: 'center',
                  fontWeight: 500,
                  cursor: 'pointer',
                  color: isRecommendationMode ? token.colorTextLightSolid : token.colorText,
                  zIndex: 1,
                  position: 'relative',
                  transition: 'color 0.3s ease',
                }}
              >
                Recommendations
              </div>
            </div>
          </div>
        </Flex>

        <AnimatePresence>
          {!isRecommendationMode && (
            <motion.div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                width: '100%',
              }}
              variants={searchContainerVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
            >
              <Space direction="vertical" size={12} style={{ width: isSuggestionsLoading ? 800 : undefined, maxWidth: "800px" }}>
                <Flex justify="space-between" align="center" style={{ width: "100%" }}>
                  <Title level={5} style={{ textAlign: "left", margin: 0 }}>
                    Suggestions for you:
                  </Title>
                  <AIButton
                    icon={<ReloadOutlined />}
                    loading={isSuggestionsFetching}
                    onClick={() => refreshSuggestions()}
                    disabled={isSuggestionsFetching}
                  >
                    {isSuggestionsFetching ? "Refresing..." : "Refresh"}
                  </AIButton>
                </Flex>
                {isSuggestionsLoading ? (
                  <Skeleton active paragraph={{ rows: 2 }} style={{ width: '100%' }} />
                ) : (
                  suggestionItems?.map((item, index) => (
                    <SuggestionItem
                      key={index}
                      content={item}
                      handleClick={() => {
                        setSearchValue(item);
                      }}
                    />
                  )) || []
                )}
              </Space>

              <AISearchBar
                searchValue={searchValue}
                setSearchValue={setSearchValue}
                handleSearch={handleSearch}
              />

              <Flex vertical gap={16} align="start" style={{ width: "100%" }}>
                <MultiChoiceFilter
                  label="Job Levels"
                  options={Array.isArray(jobRoles) ? jobRoles.map(role => ({ label: role, value: role })) : []}
                  selectedValues={selectedJobLevels}
                  onChange={handleLevelFilterChange}
                  isLoading={isJobLevelsLoading}
                />

                <MultiChoiceFilter
                  label="Job Titles"
                  options={Array.isArray(jobTitles) ? jobTitles.map(title => ({ label: title, value: title })) : []}
                  selectedValues={selectedJobTitles}
                  onChange={handleJobTitleFilterChange}
                  isLoading={isJobTitlesLoading}
                />
              </Flex>
            </motion.div>
          )}
        </AnimatePresence>

        <div style={{ padding: '16px 16px 4px 8px', width: '100%' }}>
          <Typography.Text strong>
            {isJobsLoading
              ? <Skeleton.Node active style={{ width: 100, height: 16 }} />
              : isRecommendationMode
                ? `${jobsData?.items.length || 0} personalized recommendations for you`
                : `${jobsData?.items.length || 0} jobs found`}
          </Typography.Text>
        </div>
      </Flex>

      <Row gutter={16} style={{ height: "100%" }}>
        <Col span={9}>
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
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ staggerChildren: 0.1 }}
              >
                {jobsData?.items.map((job, index) => (
                  <motion.div
                    key={job.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    style={{ marginBottom: 16 }}
                  >
                    <JobCard
                      job={job}
                      handleToggleFavorite={(e: MouseEvent) => {
                        e.stopPropagation();
                        toggleFavorite({ jobId: job.id, isFavorite: job.is_favorite });
                      }}
                      handleSelectJob={() => setSelectedJobId(job.id)}
                      handleJobAnalysisClick={handleAnalyzeJob}
                      handleViewDetail={handleViewJobAnalysis}
                      isSelected={selectedJobId === job.id}
                      isAnalyzing={analyzingJobIds.includes(job.id)}
                    />
                  </motion.div>
                ))}
              </motion.div>
            )}

            {!isJobsLoading && jobsData?.items.length === 0 && (
              <div style={{ textAlign: 'center', padding: '0 0 24px 0', background: '#fff', borderRadius: 16 }}>
                <Image
                  src={emptyStateSvg}
                  alt="No jobs found"
                  preview={false}
                  style={{ width: 200, height: 200 }}
                />
                <Title level={5} style={{ margin: 0 }}>
                  {isRecommendationMode ? 'No recommendations available' : 'No jobs found'}
                </Title>
                <p style={{ margin: 0 }}>
                  {isRecommendationMode
                    ? 'Try updating your profile to get personalized recommendations.'
                    : 'Try adjusting your search criteria or check back later.'}
                </p>
              </div>
            )}

            {/* Show pagination for both modes */}
            <AnimatePresence>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <Pagination
                  align="center"
                  current={isRecommendationMode ? queryParams.page : lastPaginationData.page}
                  pageSize={isRecommendationMode ? queryParams.page_size : lastPaginationData.page_size}
                  total={isRecommendationMode ? jobsData?.items.length : lastPaginationData.total}
                  onChange={handlePageChange}
                  showSizeChanger={false}
                  disabled={isJobsLoading}
                />
              </motion.div>
            </AnimatePresence>
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
          {isJobsLoading ? (
            <Card
              style={{ padding: '4px', borderRadius: '8px', height: '100%' }}
              title={
                <Space size="large" style={{ width: "100%", padding: 8 }}>
                  <Skeleton.Node active style={{ width: 60, height: 60, borderRadius: 4 }} />
                  <Skeleton.Node active style={{ height: 32, width: 600 }} />
                </Space>
              }
            >
              <Skeleton active paragraph={{ rows: 10 }} />
            </Card>
          ) : selectedJob ? (
            <JobDetail
              job={selectedJob}
              isFavorite={selectedJob.is_favorite || false}
              handleToggleFavorite={(e: MouseEvent) => {
                e.stopPropagation();
                toggleFavorite({ jobId: selectedJob.id, isFavorite: selectedJob.is_favorite });
              }}
              handleJobAnalysisClick={handleAnalyzeJob}
              isAnalyzing={analyzingJobIds.includes(selectedJob.id)}
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