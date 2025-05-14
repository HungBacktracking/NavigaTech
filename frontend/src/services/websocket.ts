import { APP_CONFIG } from "../lib/app-config";
import { WebSocketNotification } from "../lib/types/websocket";

interface WebSocketCallbacks {
  onConnect?: () => void;
  onError?: (error: Event) => void;
  onDisconnect?: (event: CloseEvent) => void;
}

class WebSocketService {
  private socket: WebSocket | null = null;
  private listeners: ((notification: WebSocketNotification) => void)[] = [];
  private callbacks: WebSocketCallbacks = {};
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  
  connect(userId: string, token: string, callbacks?: WebSocketCallbacks) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      if (callbacks?.onConnect) callbacks.onConnect();
      return;
    }
    
    if (this.socket) {
      this.socket.close();
    }
    
    if (callbacks) {
      this.callbacks = callbacks;
    }
    
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    
    const backendUrl = APP_CONFIG.API_URL.replace(/^https?:\/\//, '').replace(/\/+$/, '');
    
    const urlParts = backendUrl.split('/');
    const hostPort = urlParts[0];
    
    const wsUrl = `${protocol}://${hostPort}/api/v1/ws/notifications/${userId}?token=${token}`;
    
    console.log('Attempting to connect WebSocket to URL:', wsUrl);
    
    this.socket = new WebSocket(wsUrl);
    
    this.socket.onopen = () => {
      console.log('WebSocket connection established to URL:', wsUrl);
      this.reconnectAttempts = 0;
      if (this.callbacks.onConnect) this.callbacks.onConnect();
    };
    
    this.socket.onmessage = (event) => {
      try {
        const notification = JSON.parse(event.data) as WebSocketNotification;
        console.log('Received notification:', notification);
        
        this.listeners.forEach(listener => listener(notification));
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    };
    
    this.socket.onclose = (event) => {
      console.log('WebSocket connection closed:', event.code, event.reason, 'Was clean:', event.wasClean);
      
      if (this.callbacks.onDisconnect) this.callbacks.onDisconnect(event);
      
      // Attempt to reconnect after delay if not closed normally and under max attempts
      if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in 5s`);
        setTimeout(() => {
          console.log('Reconnecting WebSocket...');
          this.connect(userId, token, this.callbacks);
        }, 5000);
      } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max WebSocket reconnect attempts reached');
      }
      
      this.socket = null;
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocket error occurred:', error);
      if (this.callbacks.onError) this.callbacks.onError(error);
    };
  }
  
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.listeners = [];
    this.callbacks = {};
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
