import { useState, useEffect } from 'react';
import { Upload, Button, Steps, Typography, List, theme, Flex, message, Spin } from 'antd';
import { UploadOutlined, FilePdfOutlined, CheckCircleOutlined, LoadingOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import type { RcFile, UploadProps } from 'antd/es/upload';
import { authApi } from '../../services/auth';
import uploadIllustration from '../../assets/upload-illustration.svg';
import { useNavigate } from 'react-router-dom';

const { Title, Text, Paragraph } = Typography;

const UploadCVPage = () => {
  const { token } = theme.useToken();
  const navigate = useNavigate();
  const [fileList, setFileList] = useState<any[]>([]);
  const [currentStep, setCurrentStep] = useState(1);
  const [uploading, setUploading] = useState(false);

  const beforeUpload = (file: RcFile) => {
    const isPDF = file.type === 'application/pdf';
    if (!isPDF) {
      message.error('You can only upload PDF files!');
      return false;
    }

    const isLt5M = file.size / 1024 / 1024 < 5;
    if (!isLt5M) {
      message.error('File must be smaller than 5MB!');
      return false;
    }

    return true;
  };

  const handleChange: UploadProps['onChange'] = (info) => {
    setFileList(info.fileList.slice(-1));
    if (info.file.status === 'done') {
      message.success(`${info.file.name} file uploaded successfully`);
    } else if (info.file.status === 'error') {
      message.error(`${info.file.name} file upload failed.`);
    }
  };

  const handleContinue = () => {
    if (fileList.length === 0) {
      message.error('Please select a file to upload');
      return;
    }

    setCurrentStep(2);
    setUploading(true);
  };

  useEffect(() => {
    const uploadFile = async () => {
      if (currentStep === 2 && uploading) {
        try {
          await authApi.uploadCV(fileList[0].originFileObj);
          setUploading(false);
          message.success('CV uploaded successfully!');

          setTimeout(() => {
            navigate('/');
          }, 1000);
        } catch (error) {
          message.error('Failed to upload CV. Please try again.');
          setUploading(false);
          setCurrentStep(1);
        }
      }
    };

    uploadFile();
  }, [currentStep, uploading, fileList, navigate]);

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
              'Is a maximum of 2 MB in filesize',
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
          width: '50%',
          height: '75%',
          padding: '0 32px',
        }}
      >
        <Flex
          vertical
          align="center"
          style={{
            width: '100%',
          }}
        >
          <Title level={2} style={{ margin: 16 }}>
            Upload Your Resume / CV
          </Title>

          {currentStep === 1 ? (
            <Flex vertical align="center" justify="center" style={{ width: '100%' }}>
              <Upload
                beforeUpload={beforeUpload}
                onChange={handleChange}
                fileList={fileList}
                maxCount={1}
                accept=".pdf"
                listType='picture'
                style={{ width: '100%' }}
                itemRender={(originNode) => (
                  <div style={{
                    maxWidth: '360px',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}>
                    {originNode}
                  </div>
                )}
              >
                <Button
                  icon={<UploadOutlined />}
                  size="large"
                  style={{
                    height: '200px',
                    borderRadius: 16,
                    border: `1px dashed ${token.colorBorder}`,
                    display: 'flex',
                    flexDirection: 'column',
                    width: '100%',
                  }}
                >
                  <FilePdfOutlined style={{ fontSize: 40, marginBottom: 8 }} />
                  <Text>Click or drag file to this area to upload</Text>
                  <Text type="secondary">English resumes in PDF only. Max 2MB file size.</Text>
                </Button>
              </Upload>

              <Button
                type="primary"
                onClick={handleContinue}
                disabled={fileList.length === 0}
                size="large"
                style={{ marginTop: 24, borderRadius: 50, width: '80%' }}
              >
                Continue
              </Button>
            </Flex>
          ) : uploading ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              style={{ textAlign: 'center', padding: '24px 0' }}
            >
              <Spin indicator={<LoadingOutlined style={{ fontSize: 64, color: token.colorPrimary }} spin />} />
              <Title level={3}>Processing Your CV</Title>
              <Paragraph>
                We are analyzing your skills, experiences, and qualifications to match you with the best job opportunities.
              </Paragraph>
              <motion.div
                animate={{
                  width: ['0%', '100%']
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
                style={{
                  height: 4,
                  backgroundColor: token.colorPrimary,
                  borderRadius: 2,
                  marginTop: 16
                }}
              />
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              style={{ textAlign: 'center', padding: '24px 0' }}
            >
              <CheckCircleOutlined style={{ fontSize: 64, color: '#52c41a', marginBottom: 24 }} />
              <Title level={3}>CV Uploaded Successfully!</Title>
              <Paragraph>
                Redirecting you to the login page in a moment...
              </Paragraph>
            </motion.div>
          )}
        </Flex>
        <Steps
          current={currentStep - 1}
          style={{ marginTop: 48, width: '100%' }}
          items={[
            {
              title: 'Upload CV',
            },
            {
              title: 'CV Analysis',
            },
          ]}
        />
      </Flex>
    </Flex>
  );
};

export default UploadCVPage;