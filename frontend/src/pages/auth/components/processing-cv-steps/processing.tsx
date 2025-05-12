import { Typography, theme, Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';

const { Title, Paragraph } = Typography;

const ProcessingStep = () => {
  const { token } = theme.useToken();

  return (
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
  );
};

export default ProcessingStep;