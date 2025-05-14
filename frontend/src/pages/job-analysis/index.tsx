import { MouseEvent, useMemo, useState } from 'react';
import { Typography, Space, Input, Empty, Flex, message, Skeleton, Card, Button, Image, Pagination } from 'antd';
import { StarOutlined, MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Splitter } from 'antd';

import { jobAnalysisApi } from '../../services/job-analysis';
import { jobApi } from '../../services/job-finder';
import JobAnalysisCard from './components/job-analysis-card';
import MiniFavoriteJobCard from './components/mini-favorite-job-card';
import emptyStateSvg from '../../assets/empty-state.svg';
import { Link } from 'react-router-dom';
import { orange } from '@ant-design/colors';
import { JobAnalytic, JobFavoriteResponse } from '../../lib/types/job';
import { useJobAnalysis } from '../../contexts/job-analysis/job-analysis-context';

const { Title, Text } = Typography;
// const { Search } = Input;

const JobAnalysisPage = () => {
  const queryClient = useQueryClient();
  const [messageApi, contextHolder] = message.useMessage({
    top: 50,
  });
  const { showJobAnalysis } = useJobAnalysis();
  // const [searchValue, setSearchValue] = useState('');
  const [selectedJob, setSelectedJob] = useState<JobAnalytic | null>(null);
  const [favoriteQueryParams, setFavoriteQueryParams] = useState({
    page: 1,
    page_size: 10,
  });
  const [lastFavoritesPaginationData, setLastFavoritesPaginationData] = useState({
    page: 1,
    pageSize: 10,
    total: 0,
  });
  const [isFavoritePanelOpen, setIsFavoritePanelOpen] = useState(false);
  const [favoritePanelWidth, setFavoritePanelWidth] = useState([0, 100]);
  const [analyzingJobIds, setAnalyzingJobIds] = useState<string[]>([]);
  const [deletingJobIds, setDeletingJobIds] = useState<string[]>([]);

  const { data: jobAnalyses, isLoading: isAnalysesLoading } = useQuery({
    queryKey: ['jobAnalyses'],
    queryFn: () => jobAnalysisApi.getJobAnalyses(),
  });

  const { data: favoriteJobs, isLoading: isFavoritesLoading } = useQuery({
    queryKey: ['favoriteJobs', favoriteQueryParams],
    queryFn: () => jobApi.getFavoriteJobs(favoriteQueryParams),
    enabled: isFavoritePanelOpen,
  });

  const { mutate: deleteJobAnalysis } = useMutation({
    mutationFn: (jobId: string) => jobAnalysisApi.deleteJobAnalysis(jobId),
    onMutate: (jobId) => {
      setDeletingJobIds(prev => [...prev, jobId]);
    },
    onSuccess: (success, jobId) => {
      if (success) {
        messageApi.success('Job analysis deleted successfully');

        if (selectedJob?.id === jobId) {
          setSelectedJob(null);
        }

        queryClient.invalidateQueries({ queryKey: ['jobAnalyses'] });
      } else {
        messageApi.error('Failed to delete job analysis');
      }
    },
    onError: () => {
      messageApi.error('An error occurred while deleting the job analysis');
    },
    onSettled: (_, __, jobId) => {
      setDeletingJobIds(prev => prev.filter(id => id !== jobId));
    }
  });

  const { mutate: createAnalysis } = useMutation({
    mutationFn: (jobId: string) => jobAnalysisApi.analyzeJob(jobId),
    onMutate: (jobId) => {
      setAnalyzingJobIds(prev => [...prev, jobId]);
    },
    onSuccess: (analysisJobResponse) => {
      if (analysisJobResponse) {
        messageApi.success('Job is being processed in the background. You will be notified when it is ready.');
        queryClient.invalidateQueries({ queryKey: ['jobAnalyses'] });
      } else {
        messageApi.error("Failed to analyze job. The job may be already analyzed!")
      }
    },
    onError: () => {
      messageApi.error("Failed to analyze job. The job may be already analyzed!");
    },
    onSettled: (_, __, jobId) => {
      setAnalyzingJobIds(prev => prev.filter(id => id !== jobId));
    }
  });

  const { mutate: toggleFavorite } = useMutation({
    mutationFn: ({ id, is_favorite }: { id: string, is_favorite: boolean }) => jobApi.toggleFavorite(id, is_favorite),
    onSuccess: ({ id, is_favorite }: { id: string, is_favorite: boolean }) => {
      queryClient.invalidateQueries({ queryKey: ['favoriteJobs', favoriteQueryParams] });
      messageApi.success(`Job ${is_favorite ? 'added to' : 'removed from'} favorites`);
    },
    onError: () => {
      messageApi.error('Failed to update favorites');
    }
  });

  // useMemo(() => {
  //   if (jobAnalyses) {
  //     setLastAnalysesPaginationData({
  //       page: jobAnalyses.page,
  //       pageSize: jobAnalyses.page_size,
  //       total: jobAnalyses.total,
  //     });
  //   }
  // }, [jobAnalyses]);

  useMemo(() => {
    if (favoriteJobs) {
      setLastFavoritesPaginationData({
        page: favoriteJobs.page,
        pageSize: favoriteJobs.page_size,
        total: favoriteJobs.total,
      });
    }
  }, [favoriteJobs]);

  const toggleFavoritePanel = () => {
    if (isFavoritePanelOpen) {
      setFavoritePanelWidth([0, 100]);
      setIsFavoritePanelOpen(false);
    } else {
      setFavoritePanelWidth([25, 75]);
      setIsFavoritePanelOpen(true);
    }
  };

  // const handleAnalysesPageChange = (page: number) => {
  //   setAnalysesQueryParams(prev => ({ ...prev, page }));
  // }

  const handelFavoritesPageChange = (page: number) => {
    setFavoriteQueryParams(prev => ({ ...prev, page }));
  }

  return (
    <>
      {contextHolder}
      <Flex vertical gap="small">
        <Space direction="vertical">
          <Title level={2} style={{ textAlign: 'center', margin: 0 }}>
            <span className='app-gradient-text' style={{ fontWeight: 700 }}>
              Job Analysis
            </span>
          </Title>
          <Title level={4} style={{ textAlign: 'center', margin: 0 }}>
            Analyze your job applications and get personalized insights to improve your chances of success
          </Title>
        </Space>
        <div>
          <Button
            variant="outlined"
            shape="round"
            icon={isFavoritePanelOpen ? <MenuFoldOutlined /> : <MenuUnfoldOutlined />}
            onClick={toggleFavoritePanel}
          >
            {isFavoritePanelOpen ? 'Hide Favorites' : 'Show Favorites'}
          </Button>
        </div>

        <Splitter
          onResize={setFavoritePanelWidth}
        >
          <Splitter.Panel
            size={favoritePanelWidth[0]}
            resizable={isFavoritePanelOpen}
            min="10%"
            max="25%"
          >
            <Flex
              vertical
              style={{
                background: '#fff',
                borderRadius: '16px',
                padding: '16px',
                overflow: 'auto',
                height: 'auto',
              }}
            >
              <Flex justify="space-between" align="center" style={{ marginBottom: 16 }}>
                <Flex align="center" gap={8}>
                  <StarOutlined style={{ color: orange.primary, fontSize: 16 }} />
                  <Title level={4} style={{ margin: 0 }}>Favorite Jobs</Title>
                </Flex>
              </Flex>
              {isFavoritesLoading ? (
                <Space direction="vertical" style={{ width: '100%' }}>
                  {Array(5).fill(0).map((_, index) => (
                    <Skeleton key={index} active paragraph={{ rows: 1 }} />
                  ))}
                </Space>
              ) : favoriteJobs && favoriteJobs.items.length > 0 ? (
                <Flex vertical gap="middle" style={{ width: '100%' }}>
                  <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    {favoriteJobs.items.map(job => (
                      <MiniFavoriteJobCard
                        key={job.id}
                        job={job}
                        isAnalyzing={analyzingJobIds.includes(job.id)}
                        handleAnalyze={() => {
                          createAnalysis(job.id);
                        }}
                        handleToggleFavorite={(e: MouseEvent) => {
                          e.stopPropagation();
                          toggleFavorite({
                            id: job.id,
                            is_favorite: job.is_favorite,
                          });
                        }}
                        handleViewDetail={() => {
                          showJobAnalysis(job);
                        }}
                      />
                    ))}
                  </Space>

                </Flex>
              ) : (
                <Empty
                  description="No favorites found"
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                />
              )}
              <Pagination
                align="center"
                current={isFavoritesLoading ? lastFavoritesPaginationData.page : favoriteJobs?.page}
                pageSize={isFavoritesLoading ? lastFavoritesPaginationData.pageSize : favoriteJobs?.page_size}
                total={isFavoritesLoading ? lastFavoritesPaginationData.total : favoriteJobs?.total}
                onChange={handelFavoritesPageChange}
                disabled={isFavoritesLoading}
                showSizeChanger={false}
                style={{ marginTop: 16 }}
              />
            </Flex>
          </Splitter.Panel>

          <Splitter.Panel
            size={favoritePanelWidth[1]}
            style={{ padding: '16px', overflow: 'auto' }}
          >
            <Flex vertical gap="large">
              {/* <Search
                placeholder="Eg: Software Engineer"
                value={searchValue}
                onChange={(e: ChangeEvent<HTMLInputElement>) => {
                  setSearchValue(e.target.value);
                }}
                onSearch={() => {
                  setAnalysesQueryParams(prev => ({ ...prev, search: searchValue }));
                }}
                style={{ maxWidth: 500 }}
                enterButton={<SearchOutlined />}
                allowClear
              /> */}

              <Space direction="vertical" size={12} style={{ width: "100%" }}>
                {isAnalysesLoading ? (
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
                ) : jobAnalyses && jobAnalyses.length > 0 ? (
                  <Flex vertical gap="small">
                    <Space direction="vertical" size={12} style={{ width: "100%" }}>
                      {jobAnalyses.map((jobAnalyticResponse) => (
                        <JobAnalysisCard
                          key={jobAnalyticResponse.id}
                          jobAnalytic={jobAnalyticResponse}
                          handleDeleteJobAnalytic={deleteJobAnalysis}
                          isDeletingJobAnalytic={deletingJobIds.includes(jobAnalyticResponse.id)}
                          handleViewDetail={(jobId) => {
                            const job = jobAnalyses.find(item => item.id === jobId);
                            if (job) {
                              showJobAnalysis(job);
                            }
                          }}
                        />
                      ))}
                    </Space>
                  </Flex>
                ) : (
                  <div style={{ textAlign: 'center', padding: '0 0 24px 0', background: '#fff', borderRadius: 16 }}>
                    <Image
                      src={emptyStateSvg}
                      alt="No analyzed jobs found"
                      preview={false}
                      style={{ width: 200, height: 200 }}
                    />
                    <Title level={5} style={{ margin: 0 }}>No analyzed jobs found</Title>
                    <Text>
                      You haven't analyzed any jobs yet. Start analyzing your job from your favorites or <Link to="/home">find a job</Link>.
                    </Text>
                  </div>
                )}
                {/* <Pagination
                  align="center"
                  current={isAnalysesLoading ? lastAnalysesPaginationData.page : jobAnalyses?.page}
                  pageSize={isAnalysesLoading ? lastAnalysesPaginationData.pageSize : jobAnalyses?.page_size}
                  total={isAnalysesLoading ? lastAnalysesPaginationData.total : jobAnalyses?.total}
                  onChange={handleAnalysesPageChange}
                  showSizeChanger={false}
                  disabled={isAnalysesLoading}
                /> */}
              </Space>
            </Flex>
          </Splitter.Panel>
        </Splitter>
      </Flex>
    </>
  );
};

export default JobAnalysisPage;