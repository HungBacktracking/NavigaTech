import { Button } from 'antd';
import { ButtonProps } from 'antd/es/button';
import styles from './styles.module.css';

type AIButtonProps = ButtonProps & {
  variant?: 'primary' | 'secondary';
};

const AIButton: React.FC<AIButtonProps> = ({
  children,
  className = '',
  variant = 'primary',
  onClick,
  ...props
}) => {
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    onClick?.(e);
  };

  return (
    <div className={styles.buttonWrapper}>
      <Button
        {...props}
        className={`${styles.aiButton} ${variant === 'secondary' ? styles.secondary : styles.primary} ${className}`}
        onClick={handleClick}
      >
        <span className={styles.content}>{children}</span>
      </Button>
    </div>
  );
};

export default AIButton;