import { Button, Space, theme } from 'antd';
import { useState } from 'react';
import { ArrowRight, ChatLeft } from 'react-bootstrap-icons';

interface SuggestionItemProps {
  content: string;
  handleClick: (content: string) => void;
}

const SuggestionItem = ({
  content,
  handleClick,
}: SuggestionItemProps) => {
  const [isHovered, setIsHovered] = useState(false);
  const { token } = theme.useToken();

  return (
    <Button
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
        padding: '8px 16px',
        borderRadius: '32px',
        backgroundColor: isHovered ? token.colorInfoBg : undefined,
        transition: 'all 0.3s ease',
        transform: isHovered ? 'translateY(-2px)' : undefined,
        height: 'auto',
      }}
      onClick={() => handleClick(content)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      block
    >
      <Space direction="horizontal" size="small" style={{ width: '100%' }}>
        <ChatLeft size={12} />
        <span style={{ textWrap: 'wrap' }}>{content}</span>
      </Space>
      <ArrowRight />
    </Button>
  );
};

export default SuggestionItem;