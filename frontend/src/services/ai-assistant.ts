import api from "../lib/clients/axios/api";
import { ChatConversation, ChatMessage, ChatRole } from "../lib/types/ai-assistant";


export const aiAssistantApi = {
  getConversations: async (): Promise<ChatConversation[]> => {
    const response = await api.get("/sessions");
    console.log("Conversations response:", response.data);
    return response.data;
  },

  getConversation: async (id: string): Promise<ChatMessage[]> => {
    const response = await api.get(`/sessions/${id}/messages`);
    console.log("Conversation messages response:", response.data);
    return response.data;
  },

  createConversation: async (title: string = "New conversation"): Promise<ChatConversation> => {
    const response = await api.post("/sessions", { title });
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
    const response = await api.get(`/sessions/${id}/messages`);
    return response.data;
  },

  // Send a new message
  sendMessage: async (conversationId: string, content: string): Promise<{userMessage: ChatMessage, aiMessage: ChatMessage}> => {
    const aiContent = await api.post(`/sessions/${conversationId}/generate-response`, {
      content,
    });
    
    const userMessageResponse = await api.post(`/sessions/${conversationId}/messages`, {
      role: ChatRole.USER,
      content,
    });
    
    const aiMessageResponse = await api.post(`/sessions/${conversationId}/messages`, {
      role: ChatRole.ASSISTANT,
      content: aiContent.data,
    });
      
    return {
      userMessage: userMessageResponse.data,
      aiMessage: aiMessageResponse.data,
    };
  },

  getSamplePrompts: async (): Promise<string[]> => {
    throw new Error("Sample prompts are not provided by the backend");
  },
};
