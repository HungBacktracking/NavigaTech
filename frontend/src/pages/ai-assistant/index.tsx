import { useState, useEffect, useRef } from 'react';
import { Flex, Spin, Alert, message } from 'antd';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { ChatRole } from '../../lib/types/ai-assistant';
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
    queryFn: () => conversationId ? aiAssistantApi.getConversation(conversationId) : undefined,
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

  useEffect(() => {
    if (conversation?.length) {
      scrollToBottom();
    }
  }, [conversation]);

  const handleSendMessage = (content: string) => {
    if (!content.trim() || !conversationId) return;

    sendMessage({ conversationId, content });
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
      <Flex align="center" justify="center">
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
          ) : conversationId && conversation?.length === 0 ? (
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
                  disabled={!conversationId || isThinking || isSendingMessage}
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
                    {conversation?.map((message) => (
                      <div key={message.id}>
                        <AnimatePresence>
                          <ChatMessage
                            message={message}
                            // onRegenerateResponse={() => handleRegenerateResponse(message.id)}
                            // onEditMessage={() => handleStartEditMessage(message)}
                          />
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
                  disabled={!conversationId || isThinking || isSendingMessage}
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