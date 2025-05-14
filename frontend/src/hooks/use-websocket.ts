import { useEffect } from "react";
import { webSocketService } from "../services/websocket";

export const useWebSocket = (userId: string | null, token: string | null) => {
  useEffect(() => {
    if (!userId || !token) return;
    
    webSocketService.connect(userId, token);
    
    return () => {
      webSocketService.disconnect();
    };
  }, [userId, token]);
  
  return webSocketService;
};
