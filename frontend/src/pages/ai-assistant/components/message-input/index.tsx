import { useState } from 'react';
import { Button, Input, Flex, theme, Typography } from 'antd';
import { SendOutlined } from '@ant-design/icons';

interface MessageInputProps {
  onSendMessage: (content: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

const MessageInput = ({
  onSendMessage,
  isLoading = false,
  disabled = false,
}: MessageInputProps) => {
  const [content, setContent] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const { token } = theme.useToken();

  const handleSubmit = () => {
    if (content.trim() && !isLoading) {
      onSendMessage(content);
      setContent('');
    }
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <Flex
      vertical
      style={{
        width: '100%',
        maxWidth: '800px',
      }}
    >
      <Flex
        align="center"
        style={{
          borderRadius: '32px',
          background: token.colorBgContainer,
          boxShadow: token.boxShadow,
          padding: '8px 16px',
          border: `1px solid ${isFocused ? token.colorPrimary : token.colorBorderSecondary}`,
          transition: 'all 0.3s ease',
        }}
        onMouseEnter={() => !isFocused && !disabled && setIsFocused(true)}
        onMouseLeave={() => !document.activeElement?.contains(document.querySelector('textarea')) && setIsFocused(false)}
      >
        <Input.TextArea
          value={content}
          onChange={handleContentChange}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Message Job Tinder AI assistant..."
          autoSize={{ minRows: 1, maxRows: 4 }}
          disabled={disabled}
          style={{
            resize: 'none',
            boxShadow: 'none',
            paddingRight: '8px',
            border: 'none',
          }}
          className="scrollbar-custom"
        />
        <Button
          type="primary"
          shape="circle"
          icon={<SendOutlined />}
          onClick={handleSubmit}
          loading={isLoading}
          disabled={disabled || !content.trim()}
          style={{
            marginLeft: '8px',
            flexShrink: 0,
          }}
        />
      </Flex>
      <Typography.Text
        style={{
          textAlign: 'center',
          marginTop: '8px',
          color: token.colorTextSecondary,
          fontSize: '12px',
          borderRadius: '32px',
          backdropFilter: 'blur(10px)',
        }}
      >
        Job Tinder Assistant can make mistakes. Please verify important information.
      </Typography.Text>
    </Flex>
  );
};

export default MessageInput;