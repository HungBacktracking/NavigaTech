import { useEffect } from 'react';
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
  
  useEffect(() => {
    if (!userId || !token) return;
    
    webSocketService.connect(userId, token);
    
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
    };
  }, [userId, token, messageApi, navigate]);
  
  return { contextHolder };
}

export default useNotifications;
