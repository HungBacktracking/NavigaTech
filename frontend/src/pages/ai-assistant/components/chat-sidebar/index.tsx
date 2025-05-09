import { useState, KeyboardEvent, ChangeEvent, useMemo } from 'react';
import { Button, Input, Typography, Divider, Empty, theme, Flex, List, Spin, Dropdown } from 'antd';
import { PlusOutlined, CloseOutlined, MenuUnfoldOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { aiAssistantApi } from '../../../../services/ai-assistant';
import { ChatConversation } from '../../../../lib/types/ai-assistant';
import AIButton from '../../../../components/ai-button';
import { Chat, ThreeDotsVertical } from 'react-bootstrap-icons';
import styles from './styles.module.css';

const { Text, Title } = Typography;

interface ChatSidebarProps {
  conversations: ChatConversation[];
  isLoading: boolean;
  collapsed: boolean;
  onToggle: () => void;
  selectedConversationId?: string;
  onCreateNewConversation: () => void;
}

const groupConversationsByDate = (conversations: ChatConversation[]) => {
  const result: Record<"Today" | "Yesterday" | "Last 7 Days" | "Older", ChatConversation[]> = {
    "Today": [],
    "Yesterday": [],
    "Last 7 Days": [],
    "Older": []
  };

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  const lastWeek = new Date(today);
  lastWeek.setDate(lastWeek.getDate() - 7);

  conversations.forEach(conv => {
    const updatedDate = new Date(conv.updatedAt);
    updatedDate.setHours(0, 0, 0, 0);

    if (updatedDate.getTime() === today.getTime()) {
      result['Today'].push(conv);
    } else if (updatedDate.getTime() === yesterday.getTime()) {
      result['Yesterday'].push(conv);
    } else if (updatedDate > lastWeek) {
      result['Last 7 Days'].push(conv);
    } else {
      result['Older'].push(conv);
    }
  });

  return result;
};

const ChatSidebar = ({ conversations, isLoading, collapsed, onToggle, selectedConversationId, onCreateNewConversation }: ChatSidebarProps) => {
  const { token } = theme.useToken();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [editingConversationId, setEditingConversationId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const filteredConversations = useMemo(() => {
    if (!searchQuery.trim()) return conversations;
    return conversations.filter(conv => conv.title.toLowerCase().includes(searchQuery.toLowerCase()));
  }, [conversations, searchQuery]);

  const groupedConversations = useMemo(() =>
    groupConversationsByDate(filteredConversations),
    [filteredConversations]
  );

  const deleteConversationMutation = useMutation({
    mutationFn: aiAssistantApi.deleteConversation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      if (selectedConversationId && filteredConversations.length > 1) {
        const currentIndex = filteredConversations.findIndex(conv => conv.id === selectedConversationId);
        const nextConversation = filteredConversations[currentIndex === 0 ? 1 : currentIndex - 1];
        if (nextConversation) {
          navigate(`/ai-assistant/${nextConversation.id}`);
        }
      } else {
        navigate('/ai-assistant');
      }
    }
  });

  const { mutate: updateConversationTitle } = useMutation({
    mutationFn: ({ id, title }: { id: string, title: string }) =>
      aiAssistantApi.updateConversationTitle(id, title),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      setEditingConversationId(null);
    }
  });

  const handleTitleUpdate = () => {
    if (editingConversationId && editTitle.trim()) {
      updateConversationTitle({
        id: editingConversationId,
        title: editTitle
      });
    }
  };

  const startEditing = (conversation: ChatConversation) => {
    setEditingConversationId(conversation.id);
    setEditTitle(conversation.title);
  };

  const cancelEditing = () => {
    setEditingConversationId(null);
    setEditTitle('');
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleTitleUpdate();
    } else if (e.key === 'Escape') {
      cancelEditing();
    }
  };

  const handleConversationClick = (conversationId: string) => {
    navigate(`/ai-assistant/${conversationId}`);
  };

  return (
    <>
      <Button
        type="primary"
        size="large"
        shape="circle"
        icon={<MenuUnfoldOutlined />}
        onClick={onToggle}
        style={{
          position: 'fixed',
          top: '7%',
          left: 16,
          zIndex: 10,
          display: collapsed ? 'flex' : 'none',
          justifyContent: 'center',
          alignItems: 'center',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
        }}
      />
      <motion.div
        style={{
          position: 'fixed',
          top: '7%',
          left: 16,
          bottom: '7%',
          zIndex: 10,
          overflowX: 'hidden',
        }}
        initial={false}
        animate={collapsed ? "closed" : "open"}
        variants={{
          open: { width: 300, transition: { duration: 0.3, ease: "easeInOut" } },
          closed: { width: 0, transition: { duration: 0.3, ease: "easeInOut" } }
        }}
      >
        <Flex
          vertical
          style={{
            height: '100%',
            width: '300px',
            backgroundColor: token.colorBgContainer,
            boxShadow: '2px 0 8px rgba(0, 0, 0, 0.05)',
            borderRadius: '16px',
          }}
          className="scrollbar-custom"
        >
          <Flex vertical gap="small" style={{
            padding: '16px',
          }}>
            <Flex justify="space-between" align="center">
              <Title level={4} style={{ margin: 0 }}>AI Assistant </Title>
              <Button
                type="text"
                icon={collapsed ? <MenuUnfoldOutlined /> : <MenuUnfoldOutlined rotate={180} />}
                onClick={onToggle}
                style={{ color: token.colorTextSecondary }}
              />
            </Flex>

            <Input
              placeholder="Search conversations"
              prefix={<SearchOutlined />}
              value={searchQuery}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
              style={{ borderRadius: '32px' }}
            />

            <AIButton
              icon={<PlusOutlined />}
              onClick={onCreateNewConversation}
              style={{ borderRadius: '32px' }}
              block
            >
              New Chat
            </AIButton>
          </Flex>

          {isLoading ? (
            <Flex align="center" justify="center" style={{ height: '100%' }}>
              <Spin size="large" style={{ color: token.colorPrimary }} />
            </Flex>
          ) : filteredConversations.length === 0 ? (
            <Empty
              description="No conversations found"
              style={{ marginTop: '48px' }}
            />
          ) : (
            Object.entries(groupedConversations).map(([group, convs]) => (
              convs.length > 0 && (
                <div key={group}>
                  <Divider orientation="left" style={{
                    margin: '8px 0',
                    fontSize: '8px',
                    color: token.colorTextSecondary,
                  }}>
                    {group}
                  </Divider>
                  <List
                    dataSource={convs}
                    renderItem={(conversation) => (
                      <List.Item
                        key={conversation.id}
                        onClick={() => handleConversationClick(conversation.id)}
                        style={{
                          padding: '8px',
                          borderRadius: '8px',
                          margin: '8px',
                          cursor: 'pointer',
                          backgroundColor: selectedConversationId === conversation.id ? token.colorPrimaryBg : 'transparent',
                          transition: 'background-color 0.2s, border-color 0.2s',
                          border: 'none',
                        }}
                        className={styles['conversation-item']}
                      >
                        {editingConversationId === conversation.id ? (
                          <Flex align="center" style={{ width: '100%' }}>
                            <Input
                              value={editTitle}
                              onChange={(e: ChangeEvent<HTMLInputElement>) => setEditTitle(e.target.value)}
                              onBlur={handleTitleUpdate}
                              onKeyDown={handleKeyDown}
                              autoFocus
                              onClick={(e: ChangeEvent<HTMLInputElement>) => e.stopPropagation()}
                              style={{ flex: 1, borderRadius: '4px' }}
                            />
                            <Button
                              type="text"
                              icon={<CloseOutlined />}
                              onClick={(e: MouseEvent) => {
                                e.stopPropagation();
                                cancelEditing();
                              }}
                              size="small"
                              style={{ marginLeft: '8px' }}
                            />
                          </Flex>
                        ) : (
                          <Flex justify="space-between" align="center" style={{ width: '100%' }}>
                            <Text
                              ellipsis
                              style={{
                                flex: 1,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                                color: selectedConversationId === conversation.id ? token.colorPrimaryActive : token.colorText,
                              }}
                            >
                              <Chat style={{ marginRight: 4 }} /> {conversation.title}
                            </Text>
                            <div className={styles['conversation-actions']}>
                              <Dropdown
                                menu={{
                                  items: [
                                    {
                                      key: 'edit',
                                      icon: <EditOutlined />,
                                      label: 'Edit title',
                                      onClick: (e) => {
                                        e.domEvent.stopPropagation();
                                        startEditing(conversation);
                                      },
                                    },
                                    {
                                      key: 'delete',
                                      icon: <DeleteOutlined />,
                                      label: 'Delete',
                                      danger: true,
                                      onClick: (e) => {
                                        e.domEvent.stopPropagation();
                                        const confirmDelete = window.confirm('Are you sure you want to delete this conversation?');
                                        if (confirmDelete) {
                                          deleteConversationMutation.mutate(conversation.id);
                                        }
                                      },
                                    },
                                  ],
                                }}
                                placement="bottomRight"
                                trigger={['click']}
                                getPopupContainer={(trigger) => trigger.parentElement || document.body}
                              >
                                <Button
                                  type="text"
                                  icon={<ThreeDotsVertical />}
                                  onClick={(e: MouseEvent) => e.stopPropagation()}
                                  size="small"
                                  style={{ color: token.colorTextSecondary }}
                                />
                              </Dropdown>
                            </div>
                          </Flex>
                        )}
                      </List.Item>
                    )}
                  />
                </div>
              )
            ))
          )}
        </Flex>
      </motion.div>
    </>
  );
};

export default ChatSidebar;