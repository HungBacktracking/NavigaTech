import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { message } from 'antd';
import { webSocketService } from '../services/websocket';

interface NotificationHookProps {
  userId: string | null;
  token: string | null;
}

export function useNotifications({ userId, token }: NotificationHookProps) {
  const navigate = useNavigate();
  const [messageApi, contextHolder] = message.useMessage();
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'error' | 'disconnected'>('disconnected');
  
  useEffect(() => {
    if (!userId || !token) return;
    
    setConnectionStatus('connecting');
    
    const abortController = new AbortController();
    
    const onConnect = () => {
      setConnectionStatus('connected');
    };
    
    const onError = (error: any) => {
      console.error('WebSocket connection error:', error);
      setConnectionStatus('error');
    };
    
    const onDisconnect = () => {
      setConnectionStatus('disconnected');
    };
    
    webSocketService.connect(userId, token, {
      onConnect,
      onError,
      onDisconnect
    });
    
    const removeListener = webSocketService.addListener((notification) => {
      if (notification.job_id && notification.status) {
        const isCompleted = notification.status === 'COMPLETED';
        const isFailed = notification.status === 'FAILED';
        
        if (isCompleted) {
          messageApi.success({
            content: 'Job analysis completed successfully!',
            duration: 8,
            onClick: () => {
              navigate(`/job-analysis/${notification.job_id}`);
            },
            key: `job-analysis-${notification.job_id}`
          });
        } else if (isFailed) {
          messageApi.error({
            content: `Job analysis failed: ${notification.error || 'Unknown error'}`,
            duration: 8,
            key: `job-analysis-${notification.job_id}`
          });
        }
      }
    });
    
    return () => {
      removeListener();
      webSocketService.disconnect();
      abortController.abort();
    };
  }, [userId, token, messageApi, navigate]);
  
  return { contextHolder, connectionStatus };
}

export default useNotifications;
