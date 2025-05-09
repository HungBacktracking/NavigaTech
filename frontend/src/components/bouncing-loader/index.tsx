import { theme } from 'antd';
import { motion } from 'framer-motion';

const BouncingLoader = () => {
  const { token } = theme.useToken();

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      style={{
        marginTop: '8px',
        marginLeft: '48px',
        display: 'flex',
        gap: '4px'
      }}
    >
      <motion.span
        animate={{
          scale: [0.8, 1.2, 0.8],
          opacity: [0.5, 1, 0.5]
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          delay: 0
        }}
        style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: token.colorPrimary,
          display: 'inline-block'
        }}
      />
      <motion.span
        animate={{
          scale: [0.8, 1.2, 0.8],
          opacity: [0.5, 1, 0.5]
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          delay: 0.3
        }}
        style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: token.colorPrimary,
          display: 'inline-block'
        }}
      />
      <motion.span
        animate={{
          scale: [0.8, 1.2, 0.8],
          opacity: [0.5, 1, 0.5]
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          delay: 0.6
        }}
        style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: token.colorPrimary,
          display: 'inline-block'
        }}
      />
    </motion.div>
  )
};

export default BouncingLoader;