import { useState } from 'react';
import {
  Avatar,
  Button,
  Tooltip,
  Typography,
  Card,
  Flex,
  theme,
} from 'antd';
import { UserOutlined, CopyOutlined, CheckOutlined } from '@ant-design/icons';
import { ChatMessage as ChatMessageType, ChatRole } from '../../../../lib/types/ai-assistant';
import { motion } from 'framer-motion';
import { blueDark } from '@ant-design/colors';
import { Robot } from 'react-bootstrap-icons';
import CustomMarkdown from '../../../../components/custom-markdown';

const { Text } = Typography;
const { useToken } = theme;

interface ChatMessageProps {
  message: ChatMessageType;
  // onRegenerateResponse?: () => void;
  // onEditMessage?: () => void;
}

const ChatMessage = ({ message }: ChatMessageProps) => {
  const { token } = useToken();
  const [copied, setCopied] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const isUser = message.role === ChatRole.USER;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      style={{ marginBottom: '24px', width: '100%' }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Flex
        justify={isUser ? "flex-end" : "flex-start"}
        align="start"
        style={{ width: '100%' }}
      >
        {!isUser && (
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.2 }}
            style={{ marginRight: '12px' }}
          >
            <Avatar
              icon={<Robot />}
              style={{
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
              }}
              className='app-gradient'
            />
          </motion.div>
        )}

        {isUser ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <Card
              style={{
                borderRadius: 32,
                backgroundColor: token.colorPrimaryBg,
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
                border: 'none',
              }}
              styles={{
                body: {
                  padding: '8px 16px'
                }
              }}
            >
              <Text style={{ whiteSpace: 'pre-wrap' }}>{message.content}</Text>
            </Card>
            <Flex
              justify="space-between"
              align="center"
              style={{ marginTop: '8px' }}
            >
              <Text type="secondary">
                {formatDate(message.timestamp)}
              </Text>
            </Flex>
          </div>
        ) : (
          <div style={{ position: 'relative', width: '100%' }}>
            <CustomMarkdown
              content={message.content}
              id={message.id}
            />

            <Flex
              justify="space-between"
              align="center"
              style={{ marginTop: '8px' }}
            >
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {formatDate(message.timestamp)}
              </Text>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: isHovered ? 1 : 0 }}
                transition={{ duration: 0.2 }}
                style={{ display: 'flex', gap: '4px' }}
              >
                <Tooltip title={copied ? "Copied!" : "Copy message"} color={blueDark[2]}>
                  <Button
                    type="text"
                    icon={copied ? <CheckOutlined style={{ color: token.colorSuccess  }}/> : <CopyOutlined />}
                    onClick={() => copyToClipboard(message.content)}
                    size="small"
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  />
                </Tooltip>
              </motion.div>
            </Flex>
          </div>
        )}

        {isUser && (
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.2 }}
            style={{ marginLeft: '12px' }}
          >
            <Avatar
              icon={<UserOutlined />}
              style={{
                backgroundColor: token.colorPrimary,
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
              }}
            />
          </motion.div>
        )}
      </Flex>
    </motion.div>
  );
};

export default ChatMessage;