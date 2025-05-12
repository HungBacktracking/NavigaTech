import { Typography } from 'antd';
import { CheckCircleOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';

const { Title, Paragraph } = Typography;

const SuccessStep = () => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      style={{ textAlign: 'center', padding: '24px 0' }}
    >
      <CheckCircleOutlined style={{ fontSize: 64, color: '#52c41a', marginBottom: 24 }} />
      <Title level={3}>Profile Updated Successfully!</Title>
      <Paragraph>
        You can now explore job opportunities that match your profile.
      </Paragraph>
      <Paragraph type="secondary">
        Redirecting you to the dashboard...
      </Paragraph>
    </motion.div>
  );
};

export default SuccessStep;