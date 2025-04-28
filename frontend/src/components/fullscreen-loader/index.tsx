import { Flex, Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import styles from './styles.module.css';
import { ReactElement } from 'react';

interface FullscreenLoaderProps {
  tip?: string;
  size?: 'small' | 'default' | 'large';
  icon?: ReactElement;
  backdrop?: boolean;
}

const FullscreenLoader = ({
  tip = 'Loading...',
  size = 'large',
  icon,
  backdrop = true,
}: FullscreenLoaderProps) => {
  const defaultIcon = <LoadingOutlined style={{ fontSize: size === 'large' ? 40 : size === 'small' ? 24 : 32 }} />;

  return (
    <Flex
      justify="center"
      align="center" 
      className={`${styles['loader-container']} ${backdrop ? styles['with-backdrop'] : ''}`}>
      <Spin
        indicator={icon || defaultIcon}
        tip={tip}
        size={size}
        className={styles.spinner}
      />
    </Flex>
  );
};

export default FullscreenLoader;
