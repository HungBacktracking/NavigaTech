import { useState, useEffect, useRef, ChangeEvent, KeyboardEvent } from 'react';
import { Flex, Spin, Alert, message, Input, Button } from 'antd';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChatMessage as ChatMessageType, ChatRole } from '../../lib/types/ai-assistant';
import ChatSidebar from './components/chat-sidebar';
import ChatMessage from './components/chat-message';
import MessageInput from './components/message-input';
import EmptyChat from './components/empty-chat';
import { aiAssistantApi } from '../../services/ai-assistant';
import BouncingLoader from '../../components/bouncing-loader';

const AIAssistant = () => {
  const [messageApi, contextHolder] = message.useMessage({
    top: 50,
  });
  const { conversationId } = useParams<{ conversationId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [editMessageContent, setEditMessageContent] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: conversations, isLoading: isLoadingConversations } = useQuery({
    queryKey: ['conversations'],
    queryFn: aiAssistantApi.getConversations,
  });

  const { data: fetchedSamplePrompts } = useQuery({
    queryKey: ['samplePrompts'],
    queryFn: aiAssistantApi.getSamplePrompts,
  });

  const {
    data: conversation,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['conversation', conversationId],
    queryFn: () => conversationId ? aiAssistantApi.getConversation(conversationId) : null,
    enabled: !!conversationId,
  });

  useEffect(() => {
    if (!conversationId && !isLoadingConversations) {
      if (conversations && conversations.length > 0 && conversations[0]) {
        navigate(`/ai-assistant/${conversations[0].id}`);
      } else {
        createConversation("New Conversation");
      }
    }
  }, [conversationId, conversations, isLoadingConversations, navigate]);

  const { mutate: createConversation } = useMutation({
    mutationFn: aiAssistantApi.createConversation,
    onSuccess: (newConversation) => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      navigate(`/ai-assistant/${newConversation.id}`);
    },
    onError: (error) => {
      console.error("Error creating conversation:", error);
      messageApi.error("Error creating conversation. Please try again.");
    }
  });

  const { mutate: sendMessage, isPending: isSendingMessage } = useMutation({
    mutationFn: ({ conversationId, content }: { conversationId: string, content: string }) => {
      setIsThinking(true);
      queryClient.setQueryData(['conversation', conversationId], (oldData: any) => {
        if (!oldData) return oldData;

        return {
          ...oldData,
          messages: [
            ...(oldData.messages || []),
            { id: 'temp-id', role: ChatRole.USER, content, timestamp: new Date().toISOString() }
          ]
        };
      });
      scrollToBottom();
      return aiAssistantApi.sendMessage(conversationId, content);
    },
    onSuccess: ({ userMessage, aiMessage }) => {
      setIsThinking(false);
      queryClient.setQueryData(['conversation', conversationId], (oldData: any) => {
        if (!oldData) return oldData;

        const messages = oldData.messages.filter((msg: any) => msg.id !== 'temp-id');
        return {
          ...oldData,
          messages: [...messages, userMessage, aiMessage]
        };
      });
      scrollToBottom();
    },
    onError: () => {
      setIsThinking(false);
      messageApi.error("Error sending message. Please try again.");
    }
  });

  const { mutate: regenerateResponse } = useMutation({
    mutationFn: ({ messageId, conversationId }: { messageId: string, conversationId: string }) => {
      queryClient.setQueryData(['conversation', conversationId], (oldData: any) => {
        if (!oldData) return oldData;

        const messageIndex = oldData.messages.findIndex((message: any) => message.id === messageId);
        if (messageIndex === -1) return oldData;

        const userMessageIndex = messageIndex - 1;
        const newMessages = userMessageIndex >= 0 ? oldData.messages.slice(0, userMessageIndex + 1) : oldData.messages;

        return {
          ...oldData,
          messages: newMessages
        };
      });
      return aiAssistantApi.regenerateResponse(messageId, conversationId);
    },
    onSuccess: (aiMessage) => {
      setIsThinking(false);
      queryClient.setQueryData(['conversation', conversationId], (oldData: any) => {
        if (!oldData) return oldData;

        return {
          ...oldData,
          messages: [...oldData.messages, aiMessage]
        };
      });
      scrollToBottom();
    },
    onError: () => {
      setIsThinking(false);
      messageApi.error("Failed to regenerate response");
    }
  });

  const { mutate: editMessage } = useMutation({
    mutationFn: ({ conversationId, messageId, content }: { conversationId: string, messageId: string, content: string }) => {
      setIsThinking(true);
      return aiAssistantApi.editUserMessage(conversationId, messageId, content);
    },
    onSuccess: ({ editedMessage, deletedMessageIds }) => {
      queryClient.setQueryData(['conversation', conversationId], (oldData: any) => {
        if (!oldData) return oldData;

        const updatedMessages = oldData.messages
          .filter((msg: any) => !deletedMessageIds.includes(msg.id))
          .map((msg: any) => msg.id === editedMessage.id ? editedMessage : msg);

        return {
          ...oldData,
          messages: updatedMessages
        };
      });

      setEditingMessageId(null);
      setEditMessageContent('');

      if (conversationId) {
        setIsThinking(true);
        aiAssistantApi.sendMessage(conversationId, editedMessage.content)
          .then(({ aiMessage }) => {
            queryClient.setQueryData(['conversation', conversationId], (oldData: any) => {
              if (!oldData) return oldData;

              return {
                ...oldData,
                messages: [...oldData.messages, aiMessage]
              };
            });

            setIsThinking(false);
            scrollToBottom();
          })
          .catch(() => {
            setIsThinking(false);
            messageApi.error("Error generating response after edit");
          });
      }
    },
    onError: () => {
      setIsThinking(false);
      messageApi.error("Failed to edit message");
    }
  });

  useEffect(() => {
    if (conversation?.messages?.length) {
      scrollToBottom();
    }
  }, [conversation?.messages]);

  const handleSendMessage = (content: string) => {
    if (!content.trim() || !conversationId) return;

    sendMessage({ conversationId, content });
  };

  const handleRegenerateResponse = (messageId: string) => {
    if (conversationId) {
      regenerateResponse({ messageId, conversationId });
    }
  };

  const handleStartEditMessage = (message: ChatMessageType) => {
    setEditingMessageId(message.id);
    setEditMessageContent(message.content);
  };

  const handleSaveEditedMessage = () => {
    if (!editingMessageId || !conversationId || !editMessageContent.trim()) return;

    editMessage({
      conversationId,
      messageId: editingMessageId,
      content: editMessageContent
    });
  };

  const handleCancelEditMessage = () => {
    setEditingMessageId(null);
    setEditMessageContent('');
  };

  const scrollToBottom = () => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleSendSamplePrompt = (prompt: string) => {
    if (conversationId) {
      sendMessage({ conversationId, content: prompt });
    }
  };

  return (
    <>
      {contextHolder}
      <Flex horizontal align="center" justify="center">
        <ChatSidebar
          conversations={conversations ?? []}
          isLoading={isLoadingConversations}
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          selectedConversationId={conversationId}
          onCreateNewConversation={() => createConversation("New Conversation")}
        />
        <Flex
          vertical
          align="center"
          justify="center"
          style={{
            width: '100%',
            padding: '24px 0',
            marginLeft: sidebarCollapsed ? 0 : 300,
            transition: 'margin-left 0.3s ease'
          }}
        >
          {isLoading || isLoadingConversations ? (
            <Spin size="large" style={{ display: 'block', marginTop: '30%' }} />
          ) : error ? (
            <Alert
              type="error"
              message="Error loading conversation"
              description="There was an error loading this conversation. Please try again later."
              showIcon
              style={{ margin: '0 auto 20%' }}
            />
          ) : conversationId && conversation?.messages?.length === 0 ? (
            <>
              <EmptyChat
                onSelectSamplePrompt={handleSendSamplePrompt}
                samplePrompts={fetchedSamplePrompts ?? []}
              />
              <Flex
                justify="center"
                style={{
                  position: 'fixed',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  padding: '16px',
                  paddingLeft: sidebarCollapsed ? '16px' : '300px',
                  zIndex: 10,
                  transition: 'padding-left 0.3s ease',
                }}
              >
                <MessageInput
                  onSendMessage={handleSendMessage}
                  isLoading={isThinking || isSendingMessage}
                  disabled={!conversationId || isThinking || isSendingMessage || !!editingMessageId}
                />
              </Flex>
            </>
          ) : !conversationId ? (
            <Spin size="large" style={{ display: 'block', marginTop: '30%' }} />
          ) : (
            <Flex vertical style={{ width: '100%', maxWidth: '1000px' }}>
              <Flex
                vertical
                style={{
                  paddingBottom: '60px',
                  scrollBehavior: 'smooth'
                }}
              >
                {isLoading ? (
                  <Spin size="large" style={{ display: 'block', marginTop: '30%' }} />
                ) : error ? (
                  <Alert
                    type="error"
                    message="Error loading conversation"
                    description="There was an error loading this conversation. Please try again later."
                    showIcon
                    style={{ margin: '0 auto 20%' }}
                  />
                ) : (
                  <>
                    {conversation?.messages?.map((message) => (
                      <div key={message.id}>
                        <AnimatePresence>
                          {editingMessageId === message.id ? (
                            <motion.div
                              initial={{ opacity: 0, y: -5 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ duration: 0.3 }}
                            >
                              <Flex vertical style={{ width: '90%', margin: '0 auto' }}>
                                <Input.TextArea
                                  value={editMessageContent}
                                  onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setEditMessageContent(e.target.value)}
                                  onKeyDown={(e: KeyboardEvent<HTMLTextAreaElement>) => {
                                    if (e.key === 'Enter' && !e.shiftKey) {
                                      e.preventDefault();
                                      handleSaveEditedMessage();
                                    }
                                  }}
                                  placeholder="Type your message here..."
                                  autoSize={{ minRows: 2, maxRows: 4 }}
                                  disabled={isThinking || isSendingMessage}
                                  style={{
                                    borderRadius: '8px',
                                    padding: '8px',
                                  }}
                                  className="scrollbar-custom"
                                />

                                <Flex gap="small" justify="flex-end" style={{ marginTop: '10px' }}>
                                  <Button
                                    onClick={handleCancelEditMessage}
                                    disabled={isThinking || isSendingMessage}
                                  >
                                    Cancel
                                  </Button>
                                  <Button
                                    type="primary"
                                    onClick={handleSaveEditedMessage}
                                    loading={isLoading}
                                    disabled={isThinking || isSendingMessage || !editMessageContent.trim()}
                                  >
                                    Save
                                  </Button>
                                </Flex>
                              </Flex>
                            </motion.div>
                          ) : (
                            <ChatMessage
                              message={message}
                              onRegenerateResponse={() => handleRegenerateResponse(message.id)}
                              onEditMessage={() => handleStartEditMessage(message)}
                            />
                          )}
                        </AnimatePresence>
                      </div>
                    ))}

                    {isThinking && (
                      <Flex
                        justify="start"
                        style={{ margin: '16px 0 60px 0' }}
                      >
                        <BouncingLoader />
                      </Flex>
                    )}
                  </>
                )}

                <div ref={messagesEndRef} />
              </Flex>

              <Flex
                justify="center"
                style={{
                  position: 'fixed',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  padding: '16px',
                  paddingLeft: sidebarCollapsed ? '16px' : '300px',
                  zIndex: 10,
                  transition: 'padding-left 0.3s ease',
                }}
              >
                <MessageInput
                  onSendMessage={handleSendMessage}
                  isLoading={isThinking || isSendingMessage}
                  disabled={!conversationId || isThinking || isSendingMessage || !!editingMessageId}
                />
              </Flex>
            </Flex>
          )}
        </Flex>
      </Flex>
    </>
  );
};

export default AIAssistant;