import { Layout, Flex } from 'antd';
import { Suspense } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import NavBar from '../components/navbar';
import FullscreenLoader from '../components/fullscreen-loader';

const { Content, Footer } = Layout;

const MainLayout = () => {
  const location = useLocation();
  const isAIAssistantPage = location.pathname.includes('/ai-assistant');

  return (
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
    </Layout>
  );
};

export default MainLayout;
