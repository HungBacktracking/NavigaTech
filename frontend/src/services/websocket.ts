import { WebSocketNotification } from "../lib/types/websocket";

class WebSocketService {
  private socket: WebSocket | null = null;
  private listeners: ((notification: WebSocketNotification) => void)[] = [];
  
  connect(userId: string, token: string) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }
    
    if (this.socket) {
      this.socket.close();
    }
    
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const baseUrl = window.location.host;
    const wsUrl = `${protocol}://${baseUrl}/api/ws/notifications/${userId}?token=${token}`;
    
    this.socket = new WebSocket(wsUrl);
    
    this.socket.onopen = () => {
      console.log('WebSocket connection established');
    };
    
    this.socket.onmessage = (event) => {
      try {
        const notification = JSON.parse(event.data) as WebSocketNotification;
        console.log('Received notification:', notification);
        
        // Notify all listeners
        this.listeners.forEach(listener => listener(notification));
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    };
    
    this.socket.onclose = (event) => {
      console.log('WebSocket connection closed:', event.code, event.reason);
      
      // Attempt to reconnect after 5 seconds if not closed normally
      if (event.code !== 1000) {
        setTimeout(() => {
          console.log('Attempting to reconnect WebSocket...');
          this.connect(userId, token);
        }, 5000);
      }
      
      this.socket = null;
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }
  
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
  
  addListener(callback: (notification: WebSocketNotification) => void) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(listener => listener !== callback);
    };
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }

}

export const webSocketService = new WebSocketService();

export default webSocketService;