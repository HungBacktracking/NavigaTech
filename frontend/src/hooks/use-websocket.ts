import { useEffect, useState, useCallback } from "react";
import { webSocketService } from "../services/websocket";
import { WebSocketNotification } from "../lib/types/websocket";

export const useWebSocket = (userId: string | null, token: string | null) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastNotification, setLastNotification] = useState<WebSocketNotification | null>(null);
  
  const connect = useCallback(() => {
    if (!userId || !token) return;
    
    webSocketService.connect(userId, token, {
      onConnect: () => {
        console.log("WebSocket connected in hook");
        setIsConnected(true);
      },
      onDisconnect: () => {
        console.log("WebSocket disconnected in hook");
        setIsConnected(false);
      },
      onError: (error) => {
        console.error("WebSocket error in hook:", error);
        setIsConnected(false);
      },
      onMessage: (notification) => {
        console.log("Notification received in hook:", notification);
        setLastNotification(notification);
      }
    });
  }, [userId, token]);
  
  const disconnect = useCallback(() => {
    webSocketService.disconnect();
    setIsConnected(false);
  }, []);
  
  // Handle reconnection
  const reconnect = useCallback(() => {
    disconnect();
    setTimeout(() => {
      connect();
    }, 100);
  }, [connect, disconnect]);
  
  useEffect(() => {
    if (!userId || !token) return;
    
    // Initial connection
    connect();
    
    // Check connection status periodically and reconnect if needed
    const checkInterval = setInterval(() => {
      if (!webSocketService.isConnected() && userId && token) {
        console.log("WebSocket not connected, attempting reconnection");
        reconnect();
      }
    }, 30000); // Check every 30 seconds
    
    // Cleanup on unmount
    return () => {
      clearInterval(checkInterval);
      disconnect();
    };
  }, [userId, token, connect, disconnect, reconnect]);
  
  return {
    isConnected,
    lastNotification,
    addListener: webSocketService.addListener.bind(webSocketService),
    reconnect,
    status: webSocketService.getStatus()
  };
};
