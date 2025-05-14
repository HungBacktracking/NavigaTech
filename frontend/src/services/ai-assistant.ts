import api from "../lib/clients/axios/api";
import { ChatConversation, ChatMessage, ChatRole } from "../lib/types/ai-assistant";


export const aiAssistantApi = {
  getConversations: async (): Promise<ChatConversation[]> => {
    const response = await api.get("/chat/sessions");
    console.log("Conversations response:", response.data);
    return response.data;
  },

  getConversation: async (id: string): Promise<ChatMessage[]> => {
    const response = await api.get(`/chat/sessions/${id}/messages`);
    console.log("Conversation messages response:", response.data);
    return response.data;
  },

  createConversation: async (title: string = "New conversation"): Promise<ChatConversation> => {
    const response = await api.post("/chat/sessions", { title });
    console.log("Create conversation response:", response.data);
    return response.data;
  },

  updateConversationTitle: async (id: string, title: string): Promise<ChatConversation> => {
    throw new Error("Endpoint not available for updating conversation title");
  },

  deleteConversation: async (id: string): Promise<{ success: boolean }> => {
    throw new Error("Endpoint not available for deleting conversation");
  },

  getMessages: async (id: string): Promise<ChatMessage[]> => {
    const response = await api.get(`/chat/sessions/${id}/messages`);
    return response.data;
  },

  // Send a new message
  sendMessage: async (conversationId: string, content: string): Promise<{userMessage: ChatMessage, aiMessage: ChatMessage}> => {
    const aiContent = await api.post(`/chat/sessions/${conversationId}/generate-response`, {
      content,
    });
    
    const userMessageResponse = await api.post(`/chat/sessions/${conversationId}/messages`, {
      role: ChatRole.USER,
      content,
    });
    
    const aiMessageResponse = await api.post(`/chat/sessions/${conversationId}/messages`, {
      role: ChatRole.ASSISTANT,
      content: aiContent.data,
    });
      
    return {
      userMessage: userMessageResponse.data,
      aiMessage: aiMessageResponse.data,
    };
  },

  // Stream a message from the AI assistant
  streamMessage: (conversationId: string, content: string): {
    stream: Promise<{fullResponse: string}>;
    events: {
      onMessage: (callback: (chunk: string) => void) => void;
      onComplete: (callback: (fullResponse: string) => void) => void;
      onError: (callback: (error: string) => void) => void;
    }
  } => {
    let messageCallback: (chunk: string) => void = () => {};
    let completeCallback: (fullResponse: string) => void = () => {};
    let errorCallback: (error: string) => void = () => {};
    
    const stream = new Promise<{fullResponse: string}>(async (resolve, reject) => {
      let fullResponse = '';
      
      try {
        // Save the user message first
        await api.post(`/chat/sessions/${conversationId}/messages`, {
          role: ChatRole.USER,
          content,
        });
        
        // Use actual fetch API for SSE since axios doesn't support it well
        const response = await fetch(`${api.defaults.baseURL}/chat/sessions/${conversationId}/generate-response`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({ content }),
        });
        
        if (!response.ok || !response.body) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            break;
          }
          
          // Decode the chunk and add to buffer
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;
          
          // Process SSE format (data: content\n\n)
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || ''; // Keep the last incomplete chunk for next iteration
          
          for (const line of lines) {
            // Parse event type and data
            const eventMatch = line.match(/^event: (.+)$/m);
            const dataMatch = line.match(/^data: (.*)$/m);
            
            const eventType = eventMatch ? eventMatch[1] : 'message';
            let data = dataMatch ? dataMatch[1] : '';
            
            if (eventType === 'error') {
              errorCallback(data || 'Unknown error');
              reject(new Error(data || 'Stream error'));
              return;
            } else if (eventType === 'done') {
              // Stream complete
              await api.post(`/chat/sessions/${conversationId}/messages`, {
                role: ChatRole.ASSISTANT,
                content: fullResponse,
              });
              
              completeCallback(fullResponse);
              resolve({ fullResponse });
              return;
            } else if (eventType === 'message' && data) {
              // Handle escaped newlines
              data = data.replace(/\\n/g, '\n');
              fullResponse += data;
              messageCallback(data);
            }
          }
        }
        
        // If we get here without a done event, ensure we still complete
        await api.post(`/chat/sessions/${conversationId}/messages`, {
          role: ChatRole.ASSISTANT,
          content: fullResponse,
        });
        
        completeCallback(fullResponse);
        resolve({ fullResponse });
      } catch (error) {
        console.error('Streaming error:', error);
        errorCallback(error instanceof Error ? error.message : String(error));
        reject(error);
      }
    });
    
    return {
      stream,
      events: {
        onMessage: (callback) => { messageCallback = callback; },
        onComplete: (callback) => { completeCallback = callback; },
        onError: (callback) => { errorCallback = callback; }
      }
    };
  },

  getSamplePrompts: async (): Promise<string[]> => {
    throw new Error("Sample prompts are not provided by the backend");
  },
};
