import { useState } from 'react';
import { Typography, Tabs, Flex, theme } from 'antd';
import LoginForm from './components/auth-forms/login-form';
import RegisterForm from './components/auth-forms/register-form';
import { TypewriterEffect } from '../../components/magic-ui/typewriter-effect';
import { FlipWords } from '../../components/magic-ui/flip-words';
import { motion } from 'framer-motion';
import searchIllustration from '../../assets/search-illustration.svg';

const { Title, Text } = Typography;

const AuthPage = () => {
  const { token } = theme.useToken();
  const [activeTab, setActiveTab] = useState('login');

  const handleTabChange = (key: string) => {
    setActiveTab(key);
  };

  return (
    <Flex style={{ height: '100vh', backgroundColor: token.colorBgContainer }} align="center" justify="center">
      <Flex
        vertical
        align="center"
        justify="center"
        gap={32}
        style={{
          width: '47%',
          height: '95%',
          overflow: 'hidden',
          padding: '2rem',
          borderRadius: 16,
          background: token.colorPrimaryBg,
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontWeight: 'bold', fontSize: 32 }} className='app-gradient-text'>
            <TypewriterEffect
              words={[
                { text: "Job" },
                { text: "Tinder" }
              ]}
            />
          </div>
          <Flex vertical align="start" style={{ marginTop: '1rem', fontSize: '1.5rem', fontWeight: 500 }}>
            <span>
              Find your<span style={{ fontWeight: 700 }}><FlipWords
                words={[
                  "dream job",
                  "perfect match",
                  "ideal career",
                  "best opportunity"
                ]}
                duration={3000}
                className="app-gradient-text"
              /></span>
            </span>
            <span>
              with our AI-powered job search and analysis system
            </span>
          </Flex>
        </div>

        <motion.div
          animate={{
            y: [10, -10, 10],
            rotate: [0, 2, 0, -2, 0]
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          style={{ width: '80%', maxWidth: '500px' }}
        >
          <img
            src={searchIllustration}
            alt="Search Illustration"
            style={{ height: 'auto' }}
          />
        </motion.div>
      </Flex>

      <Flex
        vertical
        align="center"
        justify="space-between"
        style={{
          width: '50%',
        }}
      >
        <Flex
          vertical
          style={{
            width: '100%',
            maxWidth: '500px',
          }}
        >
          <Flex vertical style={{ textAlign: 'center' }}>
            <Title level={2} style={{ margin: 0, marginBottom: '0.5rem' }}>
              {activeTab === 'login' ? 'Holla, Welcome back' : 'Join us today!'}
            </Title>
            <Text type="secondary" style={{ fontSize: '1rem' }}>
              {activeTab === 'login'
                ? 'Sign in to continue your job hunting journey'
                : 'Create an account to find your dream job'}
            </Text>
          </Flex>
          <Tabs
            activeKey={activeTab}
            onChange={handleTabChange}
            size="large"
            centered
            items={[
              {
                key: 'login',
                label: 'Login',
                children: <LoginForm />,
              },
              {
                key: 'register',
                label: 'Register',
                children: <RegisterForm />,
              },
            ]}
          />
        </Flex>
      </Flex>
    </Flex>
  );
};

export default AuthPage;