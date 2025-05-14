import { APP_CONFIG } from "../lib/app-config";
import { WebSocketNotification } from "../lib/types/websocket";

interface WebSocketCallbacks {
  onConnect?: () => void;
  onError?: (error: Event) => void;
  onDisconnect?: (event: CloseEvent) => void;
  onMessage?: (notification: WebSocketNotification) => void;
}

class WebSocketService {
  private socket: WebSocket | null = null;
  private listeners: ((notification: WebSocketNotification) => void)[] = [];
  private callbacks: WebSocketCallbacks = {};
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 10; // Increased maximum reconnect attempts
  private reconnectDelay: number = 1000; // Start with 1 second delay
  private userId: string | null = null;
  private token: string | null = null;
  private connectionStatus: 'connecting' | 'connected' | 'disconnected' = 'disconnected';
  private reconnectTimer: NodeJS.Timeout | null = null;
  private lastHeartbeatTime: number = 0;
  private heartbeatCheckInterval: NodeJS.Timeout | null = null;
  
  connect(userId: string, token: string, callbacks?: WebSocketCallbacks) {
    this.userId = userId;
    this.token = token;
    
    if (this.connectionStatus === 'connected') {
      console.log('WebSocket already connected');
      if (callbacks?.onConnect) callbacks.onConnect();
      return;
    }
    
    // Clear any pending reconnect
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.socket) {
      try {
        this.socket.close();
      } catch (e) {
        console.error('Error closing existing socket:', e);
      }
      this.socket = null;
    }
    
    if (callbacks) {
      this.callbacks = callbacks;
    }
    
    this.connectionStatus = 'connecting';
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    
    const backendUrl = APP_CONFIG.API_URL.replace(/^https?:\/\//, '').replace(/\/+$/, '');
    const urlParts = backendUrl.split('/');
    const hostPort = urlParts[0];
    
    const wsUrl = `${protocol}://${hostPort}/api/v1/ws/notifications/${userId}?token=${token}`;
    
    console.log(`Connecting to WebSocket: ${wsUrl.replace(/token=([^&]+)/, 'token=****')}`);
    
    try {
      this.socket = new WebSocket(wsUrl);
      
      // Set connection timeout
      const connectionTimeout = setTimeout(() => {
        if (this.connectionStatus === 'connecting') {
          console.error('WebSocket connection timeout');
          this.socket?.close();
          // Will trigger onclose event which handles reconnection
        }
      }, 10000); // 10 second connection timeout
      
      this.socket.onopen = () => {
        clearTimeout(connectionTimeout);
        console.log('WebSocket connection established successfully');
        this.connectionStatus = 'connected';
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000; // Reset reconnect delay on successful connection
        this.lastHeartbeatTime = Date.now(); // Initialize heartbeat time
        this.startHeartbeatCheck(); // Start monitoring heartbeats
        if (this.callbacks.onConnect) this.callbacks.onConnect();
      };
      
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Received WebSocket message:', data);
          
          // Handle connection confirmation message
          if (data.type === 'connection' && data.status === 'connected') {
            console.log('Received connection confirmation');
            return;
          }
          
          // Handle heartbeat message
          if (data.type === 'heartbeat') {
            this.lastHeartbeatTime = Date.now();
            console.log('Received heartbeat from server');
            // Send pong response
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
              try {
                this.socket.send('pong');
              } catch (error) {
                console.error('Error sending pong response:', error);
              }
            }
            return;
          }
          
          // Process notification
          const notification = data as WebSocketNotification;
          
          // Call the specific onMessage callback if provided
          if (this.callbacks.onMessage) {
            this.callbacks.onMessage(notification);
          }
          
          // Call all listeners
          this.listeners.forEach(listener => {
            try {
              listener(notification);
            } catch (error) {
              console.error('Error in notification listener:', error);
            }
          });
        } catch (error) {
          console.error('Error processing WebSocket message:', error, 'Raw data:', event.data);
        }
      };
      
      this.socket.onclose = (event) => {
        clearTimeout(connectionTimeout);
        this.stopHeartbeatCheck();
        this.connectionStatus = 'disconnected';
        console.log(`WebSocket connection closed: code=${event.code}, reason=${event.reason || 'none'}, clean=${event.wasClean}`);
        
        if (this.callbacks.onDisconnect) {
          try {
            this.callbacks.onDisconnect(event);
          } catch (e) {
            console.error('Error in onDisconnect callback:', e);
          }
        }
        
        // Don't reconnect if closed normally or we don't have credentials anymore
        if (event.code === 1000 || !this.userId || !this.token) {
          this.socket = null;
          return;
        }
        
        // Attempt to reconnect with exponential backoff
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          const delay = Math.min(this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1), 30000); // Cap at 30 seconds
          
          console.log(`WebSocket reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
          
          this.reconnectTimer = setTimeout(() => {
            console.log(`Attempting WebSocket reconnection #${this.reconnectAttempts}`);
            this.connect(this.userId!, this.token!, this.callbacks);
          }, delay);
        } else {
          console.error('Maximum WebSocket reconnection attempts reached');
          this.socket = null;
        }
      };
      
      this.socket.onerror = (error) => {
        console.error('WebSocket error occurred:', error);
        if (this.callbacks.onError) {
          try {
            this.callbacks.onError(error);
          } catch (e) {
            console.error('Error in onError callback:', e);
          }
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.connectionStatus = 'disconnected';
      
      // Schedule reconnect
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        const delay = Math.min(this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1), 30000);
        console.log(`Scheduling reconnect after error in ${delay}ms`);
        
        this.reconnectTimer = setTimeout(() => {
          this.connect(userId, token, callbacks);
        }, delay);
      }
    }
  }
  
  startHeartbeatCheck() {
    // Stop any existing interval
    this.stopHeartbeatCheck();
    
    // Start a new check interval
    this.heartbeatCheckInterval = setInterval(() => {
      const now = Date.now();
      const timeSinceLastHeartbeat = now - this.lastHeartbeatTime;
      
      // If we haven't received a heartbeat in 90 seconds (3x the expected interval),
      // consider the connection dropped and force a reconnect
      if (timeSinceLastHeartbeat > 90000) {
        console.warn(`No heartbeat received in ${timeSinceLastHeartbeat}ms, forcing reconnect`);
        this.socket?.close();
        // The onclose handler will handle reconnection
      }
    }, 10000); // Check every 10 seconds
  }
  
  stopHeartbeatCheck() {
    if (this.heartbeatCheckInterval) {
      clearInterval(this.heartbeatCheckInterval);
      this.heartbeatCheckInterval = null;
    }
  }
  
  disconnect() {
    this.stopHeartbeatCheck();
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    this.userId = null;
    this.token = null;
    
    if (this.socket) {
      try {
        this.socket.close(1000, "Client disconnecting");
      } catch (e) {
        console.error('Error closing WebSocket:', e);
      }
      this.socket = null;
    }
    
    this.connectionStatus = 'disconnected';
    this.listeners = [];
    this.callbacks = {};
    console.log('WebSocket disconnected by client');
  }
  
  addListener(callback: (notification: WebSocketNotification) => void) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(listener => listener !== callback);
    };
  }

  isConnected(): boolean {
    return this.connectionStatus === 'connected';
  }
  
  getStatus(): 'connecting' | 'connected' | 'disconnected' {
    return this.connectionStatus;
  }
  
  // Method to manually trigger a reconnection if needed
  reconnect() {
    if (this.userId && this.token && this.connectionStatus !== 'connected') {
      console.log('Manually triggering WebSocket reconnection');
      this.connect(this.userId, this.token, this.callbacks);
    }
  }
}

export const webSocketService = new WebSocketService();

export default webSocketService;
