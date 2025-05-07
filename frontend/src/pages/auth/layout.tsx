import { Layout } from 'antd';
import { Outlet } from 'react-router-dom';

const { Content } = Layout;

const AuthLayout = () => {
  return (
    <Layout style={{ height: '100vh' }}>
      <Content style={{ width: '100%' }}>
        <Outlet />
      </Content>
    </Layout>
  );
};

export default AuthLayout;