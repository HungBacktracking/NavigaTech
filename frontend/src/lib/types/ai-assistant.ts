export enum ChatRole {
  USER = 'user',
  ASSISTANT = 'assistant',
}

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  timestamp: string;
}

export interface ChatConversation {
  id: string;
  title: string;
}
