import { useEffect, useState } from 'react';
import { Steps, Typography, theme, Flex, message, List } from 'antd';
import { motion } from 'framer-motion';
import { authApi } from '../../services/auth';
import {
  UploadStep,
  ProcessingStep,
  SuccessStep,
} from './components/processing-cv-steps';
import uploadIllustration from '../../assets/upload-illustration.svg';
import { useAuth } from '../../contexts/auth/auth-context';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;

const UploadCVPage = () => {
  const [messageApi, contextHolder] = message.useMessage();
  const { token } = theme.useToken();
  const [currentStep, setCurrentStep] = useState(0);
  const { user } = useAuth();
  const navigate = useNavigate();
  
  useEffect(() => {
    if (user && user.uploaded_resume) {
      navigate('/home', { replace: true });
    }
  }, [user]);

  const handleUpload = async (file: File) => {
    try {
      await authApi.uploadCV(file);

      setCurrentStep(1);

      await processCV();
    } catch (error) {
      console.error('Upload failed:', error);
      messageApi.error('Failed to upload CV. Please try again.');
    }
  };

  const processCV = async () => {
    try {
      const userData = await authApi.processCV();
      console.log('CV processed successfully:', userData);

      setCurrentStep(2);

      setTimeout(() => {
        window.location.href = '/home';
      }, 1000);
    } catch (error) {
      console.error('Processing failed:', error);
      messageApi.error('Failed to process your CV. Please try again.');
      setCurrentStep(0);
    }
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 0:
        return <UploadStep onUpload={handleUpload} />;
      case 1:
        return <ProcessingStep />;
      case 2:
        return <SuccessStep />;
      default:
        return null;
    }
  };

  return (
    <>
      {contextHolder}
      <Flex style={{ height: '100vh', backgroundColor: token.colorBgContainer, padding: '24px' }} align="center" justify="center">
        <Flex
          vertical
          align="center"
          justify="center"
          gap={32}
          style={{
            width: '40%',
            height: '95%',
            overflow: 'hidden',
            padding: '2rem',
            borderRadius: 16,
            background: token.colorPrimaryBg,
          }}
        >
          <div style={{ marginTop: '1rem', fontSize: '1.5rem', fontWeight: 500 }}>
            Let us analyze your resume to find <span style={{ fontWeight: 700 }} className="app-gradient-text">perfect job matches</span>
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
            style={{ width: '80%', maxWidth: '300px' }}
          >
            <img
              src={uploadIllustration}
              alt="CV Upload Illustration"
              style={{ height: 'auto' }}
            />
          </motion.div>

          <Flex vertical>
            <Title level={4} style={{ margin: 0, marginBottom: '0.5rem' }}>
              👋 Guidelines for your resume
            </Title>
            <List
              dataSource={[
                'Is in PDF format',
                'Is in English',
                'Contains readable text & is not an image',
                'Is a maximum of 5 MB in filesize',
                'Is not password protected',
                'Contains only your resume and no other additional documents',
              ]}
              split={false}
              renderItem={(item) => (
                <List.Item style={{ padding: 4 }}>
                  <Text>👉 {item}</Text>
                </List.Item>
              )}
            />
          </Flex>
        </Flex>

        <Flex
          vertical
          align="center"
          justify="space-between"
          style={{
            width: '60%',
            height: '100%',
            padding: '0 1rem'
          }}
        >
          <Title level={2} style={{ margin: 16 }}>
            {currentStep === 0 ? 'Upload Your Resume / CV' :
              currentStep === 1 ? 'Processing Your CV' :
                'Success!'}
          </Title>

          {renderCurrentStep()}

          <Steps
            current={currentStep}
            style={{
              marginBottom: '16px',
              width: '100%',
              padding: '0 1rem',
            }}
            items={[
              {
                title: 'Upload CV',
              },
              {
                title: 'Processing',
              },
              {
                title: 'Complete',
              }
            ]}
          />
        </Flex>
      </Flex>
    </>
  );
};

export default UploadCVPage;