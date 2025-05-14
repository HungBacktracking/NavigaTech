import { Layout } from 'antd';
import { Suspense } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import NavBar from '../components/navbar';
import FullscreenLoader from '../components/fullscreen-loader';
import useSocketNotifications from '../hooks/use-notification';
import { useAuth } from '../contexts/auth/auth-context';
import { useJobAnalysis } from '../contexts/job-analysis/job-analysis-context';
import { JobAnalysisProvider } from '../contexts/job-analysis/job-analysis-provider';
import queryClient from '../lib/clients/query-client';

const { Content, Footer } = Layout;

const SocketNotificationHandler = () => {
  const { user } = useAuth();
  const { showJobAnalysis } = useJobAnalysis();

  const { contextHolder } = useSocketNotifications({
    userId: user?.id || null,
    token: localStorage.getItem('token'),
    handleSuccess: (notification) => {
      if (notification.task_id && notification.result) {
        showJobAnalysis(notification.result);

        queryClient.invalidateQueries({
          predicate: (query) => {
            const queryKey = query.queryKey;
            return Array.isArray(queryKey) &&
              (queryKey[0] === 'jobs' || queryKey[0] === 'favoriteJobs');
          },
        });
      }
    },
    handleFailure: (notification) => {
      console.log('Failure notification:', notification);
    }
  });

  return contextHolder;
}

const MainLayout = () => {
  const location = useLocation();
  const isAIAssistantPage = location.pathname.includes('/ai-assistant');

  return (
    <JobAnalysisProvider>
      <Layout style={{ minHeight: '100vh' }}>
        <NavBar />
        <Content
          style={{
            padding: '24px',
            margin: '32px auto 0 auto',
            maxWidth: '1400px',
            width: '100%',
            boxSizing: 'border-box',
          }}
        >
          <Suspense fallback={<FullscreenLoader />}>
            <Outlet />
          </Suspense>
        </Content>
        {!isAIAssistantPage && (
          <Footer style={{ textAlign: 'center' }}>
            <span className='app-gradient-text' style={{ fontWeight: 600 }}>JobTinder</span> ©2025 Created by Brogrammers
          </Footer>
        )}
        <SocketNotificationHandler />
      </Layout>
    </JobAnalysisProvider>
  );
};

export default MainLayout;
