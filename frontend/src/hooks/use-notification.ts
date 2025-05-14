import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { notification } from 'antd';
import { webSocketService } from '../services/websocket';

interface NotificationHookProps {
  userId: string | null;
  token: string | null;
  handleSuccess?: (notification: any) => void;
  handleFailure?: (notification: any) => void;
}

export function useSocketNotifications({ userId, token, handleSuccess, handleFailure }: NotificationHookProps) {
  const navigate = useNavigate();
  const [notiApi, contextHolder] = notification.useNotification();
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
        const isCompleted = notification.status === 'completed';
        const isFailed = notification.status === 'failed';
        
        if (isCompleted) {
          notiApi.success({
            message: `Job analysis completed successfully!`,
            description: `Your job analysis is ready. Click here to view the results.`,
            onClick: () => {
              handleSuccess && handleSuccess(notification);
            },
            duration: 5,
            showProgress: true,
            pauseOnHover: true,
            key: `job-analysis-${notification.job_id}`
          });
        } else if (isFailed) {
          notiApi.error({
            message: `Job analysis failed!`,
            description: `There was an error processing your job analysis. Please try again.`,
            onClick: () => {
              handleFailure && handleFailure(notification);
            },
            duration: 5,
            showProgress: true,
            pauseOnHover: true,
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
  }, [userId, token, notiApi, navigate]);
  
  return { contextHolder, connectionStatus };
}

export default useSocketNotifications;
