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
  const [streamingMessage, setStreamingMessage] = useState('');
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

  const handleStreamedMessage = (content: string) => {
    if (!content.trim() || !conversationId) return;
    
    setIsThinking(true);
    setStreamingMessage('');
    
    // Add user message to the UI immediately
    queryClient.setQueryData(['conversation', conversationId], (oldData: any) => {
      const tempUserMessage = { 
        id: 'temp-user-id', 
        role: ChatRole.USER, 
        content, 
        timestamp: new Date().toISOString() 
      };
      
      if (!oldData) return [tempUserMessage];
      return [...oldData, tempUserMessage];
    });
    
    scrollToBottom();
    
    // Start streaming the AI response
    const { stream, events } = aiAssistantApi.streamMessage(conversationId, content);
    
    events.onMessage((chunk) => {
      setStreamingMessage((prev) => prev + chunk);
      scrollToBottom();
    });
    
    events.onComplete((fullResponse) => {
      setIsThinking(false);
      setStreamingMessage('');
      
      // Refresh the conversation to get the updated messages with proper IDs
      queryClient.invalidateQueries({ queryKey: ['conversation', conversationId] });
    });
    
    events.onError((errorMsg) => {
      setIsThinking(false);
      setStreamingMessage('');
      messageApi.error(`Error: ${errorMsg}`);
      
      // Refresh the conversation
      queryClient.invalidateQueries({ queryKey: ['conversation', conversationId] });
    });
    
    stream.catch((error) => {
      console.error("Error in stream:", error);
      setIsThinking(false);
      setStreamingMessage('');
      messageApi.error("Error generating response. Please try again.");
    });
  };

  useEffect(() => {
    if (conversation?.length) {
      scrollToBottom();
    }
  }, [conversation]);

  const handleSendMessage = (content: string) => {
    if (!content.trim() || !conversationId) return;
    handleStreamedMessage(content);
  };

  const scrollToBottom = () => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleSendSamplePrompt = (prompt: string) => {
    if (conversationId) {
      handleStreamedMessage(prompt);
    }
  };

  // Render streaming message if it exists
  const renderStreamingMessage = () => {
    if (!streamingMessage) return null;
    
    return (
      <div key="streaming-message">
        <AnimatePresence>
          <ChatMessage
            message={{
              id: 'streaming-id',
              role: ChatRole.ASSISTANT,
              content: streamingMessage,
              timestamp: new Date().toISOString()
            }}
          />
        </AnimatePresence>
      </div>
    );
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
                  isLoading={isThinking}
                  disabled={!conversationId || isThinking}
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
                          />
                        </AnimatePresence>
                      </div>
                    ))}

                    {/* Show streaming message content */}
                    {renderStreamingMessage()}

                    {isThinking && !streamingMessage && (
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
                  isLoading={isThinking}
                  disabled={!conversationId || isThinking}
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