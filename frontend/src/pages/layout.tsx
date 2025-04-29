import { Layout } from 'antd';
import { Suspense } from 'react';
import { Outlet } from 'react-router-dom';
import NavBar from '../components/navbar';
import FullscreenLoader from '../components/fullscreen-loader';

const { Content, Footer } = Layout;

const MainLayout = () => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <NavBar />
      <Content
        style={{
          padding: '24px',
          margin: '24px auto 0 auto',
          maxWidth: '1400px',
          width: '100%',
          boxSizing: 'border-box',
        }}
      >
        <Suspense fallback={<FullscreenLoader />}>
          <Outlet />
        </Suspense>
      </Content>
      <Footer style={{ textAlign: 'center' }}>JobTinder ©2025 Created by Brogrammers</Footer>
    </Layout>
  );
};

export default MainLayout;
