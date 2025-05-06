import { Flex, Spin } from 'antd';
import styles from './styles.module.css';
import { CSSProperties } from 'react';

interface FullscreenLoaderProps {
  size?: 'small' | 'default' | 'large';
  fullscreen?: boolean;
  backdrop?: boolean;
  height?: string | number;
}

const FullscreenLoader = ({
  size = 'large',
  fullscreen = true,
  backdrop = false,
  height = '100%',
}: FullscreenLoaderProps) => {
  const containerStyles: CSSProperties = fullscreen
    ? {
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      zIndex: 9999,
    }
    : {
      position: 'relative',
      width: '100%',
      height,
    };

  return (
    <Flex
      justify="center"
      align="center"
      className={`
        ${styles.container}
        ${backdrop ? styles.withBackdrop : ''}
      `}
      style={containerStyles}
    >
      <Spin
        size={size}
        className={styles.spinner}
      />
    </Flex>
  );
};

export default FullscreenLoader;
