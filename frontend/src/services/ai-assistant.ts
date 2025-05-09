import { ChatConversation, ChatConversationDetails, ChatMessage, ChatRole } from "../lib/types/ai-assistant";

const mockConversations: ChatConversationDetails[] = [
  {
    id: "1",
    title: "Tạo CV cho Frontend Developer và phỏng vấn",
    messages: [
      {
        id: "1-1",
        role: ChatRole.USER,
        content: "Làm thế nào để tạo một CV nổi bật cho vị trí frontend developer?",
        timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: "1-2",
        role: ChatRole.ASSISTANT,
        content: "# CV cho Frontend Developer\n\n## Cấu trúc chính\n- **Thông tin cá nhân**: Tên, email, GitHub, LinkedIn\n- **Tóm tắt chuyên môn**: 2-3 câu về kinh nghiệm và kỹ năng nổi bật\n- **Kỹ năng kỹ thuật**: Frontend frameworks, languages, tools\n\n> \"CV hiệu quả nên tập trung vào thành tựu có thể đo lường được.\"\n\n### Kỹ năng then chốt\n\n| Loại | Kỹ năng |\n|------|---------|\n| Languages | JavaScript, TypeScript, HTML5, CSS3 |\n| Frameworks | React, Vue, Angular |\n| Tools | Webpack, Git, Jest |\n\n### Ví dụ mô tả kinh nghiệm\n``` \nCông ty XYZ | 2022 - Hiện tại\nSenior Frontend Developer\n\n• Phát triển UI với React, tăng conversions 23%\n• Tối ưu hiệu suất, giảm thời gian tải 40%\n```\n\n### Code snippet ví dụ\n```jsx\nfunction ProductCard({ product, onAddToCart }) {\n  return (\n    <div className=\"card\">\n      <img src={product.imageUrl} alt={product.title} />\n      <h3>{product.title}</h3>\n      <p className=\"price\">${product.price}</p>\n      <button onClick={() => onAddToCart(product)}>\n        Thêm vào giỏ\n      </button>\n    </div>\n  );\n}\n```",
        timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000 + 5 * 60 * 1000).toISOString(),
      }
    ],
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000 + 5 * 60 * 1000).toISOString(),
  },
  {
    id: "2",
    title: "Phỏng vấn Backend Java",
    messages: [
      {
        id: "2-1",
        role: ChatRole.USER,
        content: "Làm thế nào để chuẩn bị cho phỏng vấn vị trí backend developer java/spring?",
        timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: "2-2",
        role: ChatRole.ASSISTANT,
        content: "# Chuẩn bị phỏng vấn Backend Java/Spring\n\n## Quy trình phỏng vấn\n```mermaid\nflowchart LR\n    A[Screening] --> B[Technical Assessment]\n    B --> C[Technical Interview]\n    C --> D[System Design]\n    D --> E[Culture Fit]\n```\n\n## Java Core\n- **OOP**: Encapsulation, Inheritance, Polymorphism\n- **Collections**: ArrayList vs LinkedList, HashMap vs HashSet\n- **Stream API & Lambdas**: Functional programming features\n\n## Spring Framework\n```java\n@RestController\n@RequestMapping(\"/api/users\")\npublic class UserController {\n    private final UserService userService;\n    \n    @Autowired\n    public UserController(UserService userService) {\n        this.userService = userService;\n    }\n    \n    @GetMapping(\"/{id}\")\n    public ResponseEntity<User> getUserById(@PathVariable Long id) {\n        return userService.findById(id)\n                .map(ResponseEntity::ok)\n                .orElseThrow(() -> new ResourceNotFoundException(\"User not found\"));\n    }\n}\n```\n\n## System Design\n- **Microservices Architecture**: Service boundaries, communication\n- **Database Design**: Normalization, indexing, transactions\n- **API Design**: REST principles, versioning, security",
        timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000 + 7 * 60 * 1000).toISOString(),
      }
    ],
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000 + 7 * 60 * 1000).toISOString(),
  },
  {
    id: "3",
    title: "Chiến lược tìm việc Data Engineer",
    messages: [
      {
        id: "3-1",
        role: ChatRole.USER,
        content: "Tôi muốn tìm việc data engineer, bạn có thể chia sẻ chiến lược tìm việc hiệu quả không?",
        timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: "3-2",
        role: ChatRole.ASSISTANT,
        content: "# Chiến lược tìm việc Data Engineer\n\n## 1. Thị trường hiện tại\n📊 **Thống kê nhanh**\n- Mức lương trung bình: $120-150K (US) / 30-60 triệu VND (VN)\n- Kỹ năng hot: Big Data, Cloud platforms, ETL pipelines\n\n## 2. Chuẩn bị hồ sơ\n### CV cho Data Engineer\n- **Technical Skills**: Python, Spark, Kafka, AWS/GCP\n- **Project highlights**: Data pipelines, ETL workflows\n- **Metrics**: Data volume processed, performance improvements\n\n### Portfolio Example\n```\ndata-engineering-portfolio/\n├── etl-pipeline/\n├── data-quality/\n└── streaming-analytics/\n```\n\n## 3. Kênh tìm việc\n| Platform | Chiến lược |\n|----------|------------|\n| LinkedIn | Đăng bài technical, tương tác với data community |\n| TopCV, ITViec | Cập nhật CV hàng tuần |\n| Tech Events | Tham gia meetups về data |\n\n## 4. Tracking ứng tuyển\n```python\n# Job Application Tracker\nclass JobTracker:\n    def __init__(self):\n        self.applications = []\n    \n    def add_application(self, company, position, date):\n        self.applications.append({\n            \"company\": company,\n            \"position\": position,\n            \"date\": date,\n            \"status\": \"Applied\"\n        })\n```",
        timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000 + 10 * 60 * 1000).toISOString(),
      }
    ],
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000 + 10 * 60 * 1000).toISOString(),
  }
];

const mockSamplePrompts = [
  "How to build a standout resume for a frontend developer role?",
  "What questions should I prepare for a Java developer interview?",
  "How can I improve my LinkedIn profile to attract recruiters?",
  "What skills are in high demand for data science positions?",
  "What are the best ways to negotiate salary for a tech position?",
  "How can I prepare for a coding interview at a FAANG company?",
  "What are the key differences between junior and senior developer roles?",
  "How to explain employment gaps in my resume?",
  "What certifications are most valuable for cloud engineers?"
];

// Utility function to generate unique IDs
const generateId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substring(2, 9);
};

// Helper function to generate more contextually relevant AI responses
const generateAIResponse = (userMessage: string): string => {
  const lowerCaseMessage = userMessage.toLowerCase();
  
  // CV and resume related responses
  if (lowerCaseMessage.includes('cv') || lowerCaseMessage.includes('resume')) {
    return `# Resume & CV Tips

## Key Components for a Modern CV
- **Clean, ATS-friendly design** with clear sections
- **Quantifiable achievements** rather than duties
- **Skills section** highlighting relevant technologies
- **Project showcase** with clear outcomes

\`\`\`markdown
# Jane Doe
## Frontend Developer
📍 Ho Chi Minh City | 📧 jane.doe@example.com | 🔗 linkedin.com/in/janedoe

### Professional Experience
**ABC Company | Senior Frontend Developer | 2021-Present**
- Redesigned customer dashboard leading to 35% increase in user engagement
- Reduced application load time by 42% through code optimization
\`\`\`

### Technical CV Checklist
- [ ] GitHub link with pinned projects
- [ ] Portfolio website
- [ ] Skills relevance to job description
- [ ] Metrics and impact statements

Would you like me to help you build a specific section of your CV or review an existing one?`;
  }
  
  // Interview preparation
  if (lowerCaseMessage.includes('interview') || lowerCaseMessage.includes('phỏng vấn')) {
    return `# Interview Preparation Guide

## Technical Interview Structure
1. **Introduction & Background** (5-10 mins)
2. **Technical Questions** (20-30 mins)
3. **Coding Challenge** (30-45 mins)
4. **System Design** (for senior roles)
5. **Your Questions** (10-15 mins)

### STAR Method for Behavioral Questions
- **Situation**: Set the context
- **Task**: Describe your responsibility
- **Action**: Explain what you did
- **Result**: Share the outcome

\`\`\`javascript
// Common JavaScript Interview Question
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
\`\`\`

### Interview Checklist
- [ ] Research company and products
- [ ] Prepare answers to common questions
- [ ] Review your projects for discussion
- [ ] Prepare questions to ask interviewer

What specific type of interview would you like to prepare for?`;
  }
  
  // Job search strategy
  if (lowerCaseMessage.includes('job search') || lowerCaseMessage.includes('tìm việc')) {
    return `# Effective Job Search Strategy

## Multi-Channel Approach
- **Job Platforms**: LinkedIn, TopCV, ITViec, JobHopin
- **Direct Applications**: Company career pages
- **Networking**: Tech events, LinkedIn connections
- **Recruiters**: Build relationships with specialized tech recruiters

\`\`\`mermaid
graph TD
A[Job Search Strategy] --> B[Online Presence]
A --> C[Application Process]
A --> D[Networking]
B --> E[LinkedIn Profile]
B --> F[GitHub Portfolio]
C --> G[Tailored Applications]
C --> H[Follow-up System]
D --> I[Tech Events]
D --> J[Online Communities]
\`\`\`

### Weekly Job Search Template
| Day | Focus Area | Tasks |
|-----|------------|-------|
| Mon | Research | Identify 5-10 target companies |
| Tue | Applications | Submit 3-5 tailored applications |
| Wed | Networking | Connect with 3 industry professionals |
| Thu | Skills | Work on portfolio project |
| Fri | Follow-up | Check application status, send follow-ups |

What specific aspect of your job search would you like to improve?`;
  }
  
  // Career development
  if (lowerCaseMessage.includes('career') || lowerCaseMessage.includes('phát triển')) {
    return `# Career Development in Tech

## Career Pathing
- **Specialist Path**: Deep technical expertise in one area
- **Management Path**: Team and project leadership
- **Hybrid Path**: Technical leadership (e.g., Tech Lead)

### Skill Development Framework
1. **Assess** current skill level
2. **Set** specific learning goals
3. **Learn** through structured resources
4. **Apply** skills in real projects
5. **Teach** to reinforce knowledge

\`\`\`python
# Career planning as code
career_plan = {
    'short_term': {
        'skills': ['React Advanced', 'System Design'],
        'projects': ['Portfolio Redesign', 'Open Source Contribution'],
        'timeline': '6 months'
    },
    'mid_term': {
        'skills': ['Leadership', 'Architecture'],
        'role': 'Senior Developer',
        'timeline': '1-2 years'
    },
    'long_term': {
        'role': 'Tech Lead',
        'timeline': '3-5 years'
    }
}
\`\`\`

Would you like to discuss a specific career transition or skill development plan?`;
  }
  
  // Default response for other queries
  return `Thank you for your message. I'd be happy to help with that.

Let me know if you need more specific information about:

- Resume and CV optimization
- Technical interview preparation
- Job search strategies
- Career development planning
- Technical skills assessment
- Workplace challenges

Feel free to ask follow-up questions for more detailed assistance!`;
};

export const aiAssistantApi = {
  getConversations: async (): Promise<ChatConversation[]> => {
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(mockConversations.map(({ messages, ...rest }) => rest));
      }, 1000);
    });
  },
  
  getConversation: async (id: string): Promise<ChatConversationDetails> => {
    const conversation = mockConversations.find(conv => conv.id === id);
    if (!conversation) {
      throw new Error('Conversation not found');
    }
    
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ ...conversation });
      }, 1000);
    });
  },

  createConversation: async (title: string = "New conversation"): Promise<ChatConversationDetails> => {
    const now = new Date().toISOString();
    const newConversation: ChatConversationDetails = {
      id: generateId(),
      title,
      messages: [],
      createdAt: now,
      updatedAt: now,
    };

    mockConversations.unshift(newConversation);
    
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ ...newConversation });
      }, 500);
    });
  },

  updateConversationTitle: async (id: string, title: string): Promise<ChatConversationDetails> => {
    const conversationIndex = mockConversations.findIndex(conv => conv.id === id);
    if (conversationIndex === -1) {
      throw new Error('Conversation not found');
    }

    mockConversations[conversationIndex].title = title;
    mockConversations[conversationIndex].updatedAt = new Date().toISOString();
    
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ ...mockConversations[conversationIndex] });
      }, 500);
    });
  },

  deleteConversation: async (id: string): Promise<{ success: boolean }> => {
    const conversationIndex = mockConversations.findIndex(conv => conv.id === id);
    if (conversationIndex === -1) {
      throw new Error('Conversation not found');
    }

    mockConversations.splice(conversationIndex, 1);
    
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ success: true });
      }, 500);
    });
  },

  // Load messages with lazy loading (pagination)
  getMessages: async (conversationId: string, options: { 
    limit?: number;
    before?: string; // message ID to fetch messages before this one
  } = {}): Promise<ChatMessage[]> => {
    const conversation = mockConversations.find(conv => conv.id === conversationId);
    if (!conversation) {
      throw new Error('Conversation not found');
    }

    const { limit = 10, before } = options;
    let messages = [...conversation.messages];
    
    // Sort messages by timestamp (newest first)
    messages.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    
    // Implement pagination
    if (before) {
      const messageIndex = messages.findIndex(msg => msg.id === before);
      if (messageIndex !== -1) {
        messages = messages.slice(messageIndex + 1);
      }
    }
    
    // Limit the number of messages
    messages = messages.slice(0, limit);
    
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(messages);
      }, 800);
    });
  },

  // Send a new message
  sendMessage: async (conversationId: string, content: string): Promise<{userMessage: ChatMessage, aiMessage: ChatMessage}> => {
    const conversationIndex = mockConversations.findIndex(conv => conv.id === conversationId);
    if (conversationIndex === -1) {
      throw new Error('Conversation not found');
    }

    const now = new Date();
    
    const userMessage: ChatMessage = {
      id: generateId(),
      role: ChatRole.USER,
      content,
      timestamp: now.toISOString(),
    };

    if (!mockConversations[conversationIndex]) {
      mockConversations[conversationIndex] = {
        id: conversationId,
        title: "New conversation",
        messages: [],
        createdAt: now.toISOString(),
        updatedAt: now.toISOString(),
      };
    }
    
    mockConversations[conversationIndex].messages.push(userMessage);
    mockConversations[conversationIndex].updatedAt = now.toISOString();
    
    return new Promise(resolve => {
      setTimeout(() => {
        const aiMessage: ChatMessage = {
          id: generateId(),
          role: ChatRole.ASSISTANT,
          content: generateAIResponse(content),
          timestamp: new Date().toISOString(),
        };
        
        if (mockConversations[conversationIndex]) {
          mockConversations[conversationIndex].messages.push(aiMessage);
          mockConversations[conversationIndex].updatedAt = new Date().toISOString();
        }
        
        resolve({ userMessage, aiMessage });
      }, 1500);
    });
  },

  regenerateResponse: async (messageId: string, conversationId: string): Promise<ChatMessage> => {
    const conversationIndex = mockConversations.findIndex(conv => conv.id === conversationId);
    if (conversationIndex === -1) {
      throw new Error('Conversation not found');
    }
    
    const messages = mockConversations[conversationIndex].messages;
    const messageIndex = messages.findIndex(msg => msg.id === messageId);
    if (messageIndex === -1) {
      throw new Error('Message not found');
    }
    
    // Find the previous user message
    let userMessageIndex = messageIndex - 1;
    while (userMessageIndex >= 0 && messages[userMessageIndex].role !== ChatRole.USER) {
      userMessageIndex--;
    }
    
    if (userMessageIndex === -1) {
      throw new Error('No corresponding user message found');
    }
    
    const userMessage = messages[userMessageIndex].content;
    
    // Remove all messages after the user message
    mockConversations[conversationIndex].messages = messages.slice(0, userMessageIndex + 1);
    
    // Generate a new response
    return new Promise(resolve => {
      setTimeout(() => {
        const aiResponse: ChatMessage = {
          id: generateId(),
          role: ChatRole.ASSISTANT,
          content: generateAIResponse(userMessage),
          timestamp: new Date().toISOString(),
        };
        
        mockConversations[conversationIndex].messages.push(aiResponse);
        mockConversations[conversationIndex].updatedAt = new Date().toISOString();

        resolve(aiResponse);
      }, 1500);
    });
  },

  // Edit user message
  editUserMessage: async (conversationId: string, messageId: string, newContent: string): Promise<{ editedMessage: ChatMessage, deletedMessageIds: string[] }> => {
    const conversationIndex = mockConversations.findIndex(conv => conv.id === conversationId);
    if (conversationIndex === -1) {
      throw new Error('Conversation not found');
    }
    
    const conversation = mockConversations[conversationIndex];
    const messageIndex = conversation.messages.findIndex(msg => msg.id === messageId);
    
    if (messageIndex === -1) {
      throw new Error('Message not found');
    }
    
    const message = conversation.messages[messageIndex];
    if (message.role !== ChatRole.USER) {
      throw new Error('Can only edit user messages');
    }
    
    // Update the message
    conversation.messages[messageIndex].content = newContent;
    conversation.messages[messageIndex].timestamp = new Date().toISOString();
    conversation.updatedAt = new Date().toISOString();
    
    // Save edited message
    const editedMessage = {...conversation.messages[messageIndex]};
    
    // Keep track of deleted message IDs
    const deletedMessageIds: string[] = [];
    for (let i = messageIndex + 1; i < conversation.messages.length; i++) {
      deletedMessageIds.push(conversation.messages[i].id);
    }
    
    // Remove all messages that came after this one
    const messagesToKeep = conversation.messages.slice(0, messageIndex + 1);
    conversation.messages = messagesToKeep;
    conversation.messageCount = messagesToKeep.length;
    
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ 
          editedMessage,
          deletedMessageIds 
        });
      }, 500);
    });
  },

  getSamplePrompts: async (): Promise<string[]> => {
    const randomPrompts = mockSamplePrompts.sort(() => 0.5 - Math.random()).slice(0, 4);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(randomPrompts);
      }, 500);
    });
  },
};
