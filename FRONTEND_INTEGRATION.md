# Frontend-Backend Integration Guide

This guide explains how to integrate the StudyBuddy frontend with the backend API.

## Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   pnpm install
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   DATABASE_URL="postgresql://username:password@localhost:5432/studybuddy?schema=public"
   JWT_SECRET="your-super-secret-jwt-key-here"
   OPENAI_API_KEY="your-openai-api-key"
   PORT=3001
   FRONTEND_URL="http://localhost:3000"
   ```

4. **Set up database:**
   ```bash
   npx prisma generate
   npx prisma migrate dev
   npx prisma db seed
   ```

5. **Start backend server:**
   ```bash
   npm run dev
   ```

The backend will be available at `http://localhost:3001`

## Frontend Integration

### 1. Update API Configuration

Create a new file `lib/api.ts` in your frontend:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api';

class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Network error' }));
      throw new Error(error.error || 'Request failed');
    }

    return response.json();
  }

  // Auth methods
  async register(data: { email: string; password: string; name: string }) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(data: { email: string; password: string }) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    if (response.success && response.data.token) {
      this.setToken(response.data.token);
    }
    
    return response;
  }

  async googleAuth(data: { email: string; name: string; avatar?: string }) {
    const response = await this.request('/auth/google', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    if (response.success && response.data.token) {
      this.setToken(response.data.token);
    }
    
    return response;
  }

  async getCurrentUser() {
    return this.request('/auth/me');
  }

  async logout() {
    this.clearToken();
    return this.request('/auth/logout', { method: 'POST' });
  }

  // Study tasks methods
  async getStudyTasks(params?: { date?: string; status?: string; subject?: string }) {
    const searchParams = new URLSearchParams();
    if (params?.date) searchParams.append('date', params.date);
    if (params?.status) searchParams.append('status', params.status);
    if (params?.subject) searchParams.append('subject', params.subject);
    
    return this.request(`/study-tasks?${searchParams.toString()}`);
  }

  async createStudyTask(data: any) {
    return this.request('/study-tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateStudyTask(id: string, data: any) {
    return this.request(`/study-tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteStudyTask(id: string) {
    return this.request(`/study-tasks/${id}`, {
      method: 'DELETE',
    });
  }

  async toggleTaskStatus(id: string) {
    return this.request(`/study-tasks/${id}/toggle-status`, {
      method: 'PATCH',
    });
  }

  // Summaries methods
  async getSummaries(params?: { page?: number; limit?: number; type?: string; language?: string }) {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.type) searchParams.append('type', params.type);
    if (params?.language) searchParams.append('language', params.language);
    
    return this.request(`/summaries?${searchParams.toString()}`);
  }

  async createSummary(data: { originalText: string; type: string; language?: string; title?: string }) {
    return this.request('/summaries', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Quiz methods
  async getQuizzes(params?: { page?: number; limit?: number; subject?: string; difficulty?: string }) {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.subject) searchParams.append('subject', params.subject);
    if (params?.difficulty) searchParams.append('difficulty', params.difficulty);
    
    return this.request(`/quizzes?${searchParams.toString()}`);
  }

  async createQuiz(data: any) {
    return this.request('/quizzes', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getQuiz(id: string) {
    return this.request(`/quizzes/${id}`);
  }

  async submitQuiz(id: string, data: { answers: any[]; timeSpent: number }) {
    return this.request(`/quizzes/${id}/submit`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Chat methods
  async getChatSessions(params?: { page?: number; limit?: number; subject?: string }) {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.subject) searchParams.append('subject', params.subject);
    
    return this.request(`/chat/sessions?${searchParams.toString()}`);
  }

  async createChatSession(data: { title: string; subject?: string }) {
    return this.request('/chat/sessions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getChatSession(id: string) {
    return this.request(`/chat/sessions/${id}`);
  }

  async sendMessage(sessionId: string, data: { content: string; subject?: string; attachments?: string[] }) {
    return this.request(`/chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Upload methods
  async uploadFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.request('/upload/file', {
      method: 'POST',
      headers: {}, // Let browser set Content-Type for FormData
      body: formData,
    });
  }

  // Progress methods
  async getProgressOverview() {
    return this.request('/progress/overview');
  }

  async getDashboardData() {
    return this.request('/user/dashboard');
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
```

### 2. Update Environment Variables

Add to your frontend `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:3001/api
```

### 3. Update Auth Modal

Replace the mock authentication in `components/auth-modal.tsx`:

```typescript
import { apiClient } from '@/lib/api';

// In your component:
const handleEmailAuth = async (e: React.FormEvent) => {
  e.preventDefault();
  setIsLoading(true);

  try {
    if (isSignUp) {
      await apiClient.register({ email, password, name });
    }
    
    const response = await apiClient.login({ email, password });
    
    if (response.success) {
      onLogin(response.data.user);
      onClose();
    }
  } catch (error) {
    console.error('Auth error:', error);
    // Handle error (show toast, etc.)
  } finally {
    setIsLoading(false);
  }
};

const handleGoogleLogin = async () => {
  setIsLoading(true);
  
  try {
    // Implement Google OAuth flow
    // For demo, you can use the mock data
    const mockUser = {
      id: "1",
      name: "Alex Johnson",
      email: "alex.johnson@gmail.com",
      avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
      provider: "google",
    };
    
    // In real implementation, get token from Google OAuth
    // const response = await apiClient.googleAuth(googleUserData);
    
    onLogin(mockUser);
    onClose();
  } catch (error) {
    console.error('Google auth error:', error);
  } finally {
    setIsLoading(false);
  }
};
```

### 4. Update Study Planner

Replace mock data in `components/study-planner.tsx`:

```typescript
import { apiClient } from '@/lib/api';

// Replace the mock tasks state with API calls
const [tasks, setTasks] = useState<StudyTask[]>([]);

// Load tasks on component mount
useEffect(() => {
  loadTasks();
}, [selectedDate]);

const loadTasks = async () => {
  try {
    const response = await apiClient.getStudyTasks({ date: selectedDate });
    if (response.success) {
      setTasks(response.data.tasks);
    }
  } catch (error) {
    console.error('Failed to load tasks:', error);
  }
};

const handleAddTask = async () => {
  try {
    const response = await apiClient.createStudyTask({
      ...newTask,
      date: selectedDate,
      time: "09:00",
    });
    
    if (response.success) {
      setTasks([...tasks, response.data.task]);
      // Reset form
      setNewTask({
        subject: "",
        topic: "",
        duration: 60,
        priority: "medium",
        description: "",
      });
      setIsAddTaskOpen(false);
    }
  } catch (error) {
    console.error('Failed to create task:', error);
  }
};

const toggleTaskStatus = async (taskId: string) => {
  try {
    const response = await apiClient.toggleTaskStatus(taskId);
    if (response.success) {
      setTasks(tasks.map(task => 
        task.id === taskId 
          ? { ...task, status: response.data.task.status }
          : task
      ));
    }
  } catch (error) {
    console.error('Failed to toggle task status:', error);
  }
};
```

### 5. Update AI Summarizer

Replace mock functionality in `components/ai-summarizer.tsx`:

```typescript
import { apiClient } from '@/lib/api';

const generateSummary = async () => {
  if (!inputText.trim()) return;

  setIsGenerating(true);
  setProgress(0);

  try {
    const response = await apiClient.createSummary({
      originalText: inputText,
      type: summaryType.toUpperCase(),
      language,
      title: `Summary ${recentSummaries.length + 1}`,
    });

    if (response.success) {
      setCurrentSummary(response.data.summary);
      setRecentSummaries([response.data.summary, ...recentSummaries]);
    }
  } catch (error) {
    console.error('Failed to generate summary:', error);
    // Show error message to user
  } finally {
    setIsGenerating(false);
    setProgress(0);
  }
};

// Load summaries on component mount
useEffect(() => {
  loadSummaries();
}, []);

const loadSummaries = async () => {
  try {
    const response = await apiClient.getSummaries({ limit: 5 });
    if (response.success) {
      setRecentSummaries(response.data.summaries);
    }
  } catch (error) {
    console.error('Failed to load summaries:', error);
  }
};
```

### 6. Update Quiz Generator

Replace mock functionality in `components/quiz-generator.tsx`:

```typescript
import { apiClient } from '@/lib/api';

const generateQuiz = async () => {
  setIsGenerating(true);

  try {
    const response = await apiClient.createQuiz({
      title: `${quizSettings.subject} Quiz`,
      subject: quizSettings.subject,
      topic: quizSettings.topic,
      description: `Quiz on ${quizSettings.topic}`,
      timeLimit: quizSettings.timeLimit,
      difficulty: quizSettings.difficulty.toUpperCase(),
      numQuestions: quizSettings.numQuestions,
      questionTypes: quizSettings.questionTypes,
      content: inputContent,
    });

    if (response.success) {
      setGeneratedQuiz(response.data.questions);
      setActiveTab("take");
    }
  } catch (error) {
    console.error('Failed to generate quiz:', error);
  } finally {
    setIsGenerating(false);
  }
};

const completeQuiz = async () => {
  try {
    const answers = generatedQuiz.map(question => ({
      questionId: question.id,
      answer: userAnswers[question.id] || "",
      timeSpent: 30, // Calculate actual time spent
    }));

    const response = await apiClient.submitQuiz(generatedQuiz[0]?.quizId || '', {
      answers,
      timeSpent: quizSettings.timeLimit * 60 - timeRemaining,
    });

    if (response.success) {
      setQuizResults(response.data.results);
      setIsQuizCompleted(true);
      setIsQuizActive(false);
      setActiveTab("results");
    }
  } catch (error) {
    console.error('Failed to submit quiz:', error);
  }
};
```

### 7. Update Doubt Solver

Replace mock functionality in `components/doubt-solver.tsx`:

```typescript
import { apiClient } from '@/lib/api';

const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

const handleSendMessage = async () => {
  if (!inputMessage.trim()) return;

  const userMessage: Message = {
    id: Date.now().toString(),
    type: "user",
    content: inputMessage,
    timestamp: new Date(),
    subject: selectedSubject,
  };

  setMessages((prev) => [...prev, userMessage]);
  setInputMessage("");
  setIsTyping(true);

  try {
    let sessionId = currentSessionId;
    
    // Create session if none exists
    if (!sessionId) {
      const sessionResponse = await apiClient.createChatSession({
        title: `Chat about ${selectedSubject}`,
        subject: selectedSubject,
      });
      
      if (sessionResponse.success) {
        sessionId = sessionResponse.data.session.id;
        setCurrentSessionId(sessionId);
      }
    }

    // Send message
    const response = await apiClient.sendMessage(sessionId!, {
      content: inputMessage,
      subject: selectedSubject,
    });

    if (response.success) {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: response.data.botMessage.content,
        timestamp: new Date(),
        subject: selectedSubject,
      };
      setMessages((prev) => [...prev, botMessage]);
    }
  } catch (error) {
    console.error('Failed to send message:', error);
    // Show error message
  } finally {
    setIsTyping(false);
  }
};

// Load chat sessions on component mount
useEffect(() => {
  loadChatSessions();
}, []);

const loadChatSessions = async () => {
  try {
    const response = await apiClient.getChatSessions({ limit: 5 });
    if (response.success) {
      setRecentChats(response.data.sessions);
    }
  } catch (error) {
    console.error('Failed to load chat sessions:', error);
  }
};
```

## Testing the Integration

1. **Start both servers:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   npm run dev

   # Terminal 2 - Frontend
   cd .. # (back to root)
   npm run dev
   ```

2. **Test the features:**
   - Register/Login with the auth modal
   - Create study tasks in the planner
   - Generate summaries with the AI summarizer
   - Create and take quizzes
   - Chat with the doubt solver

3. **Check the database:**
   ```bash
   cd backend
   npx prisma studio
   ```

## Troubleshooting

### Common Issues

1. **CORS Errors:** Make sure `FRONTEND_URL` in backend `.env` matches your frontend URL
2. **Database Connection:** Ensure PostgreSQL is running and `DATABASE_URL` is correct
3. **OpenAI API:** Make sure you have a valid `OPENAI_API_KEY`
4. **JWT Errors:** Ensure `JWT_SECRET` is set and consistent

### Debug Mode

Enable debug logging by setting `NODE_ENV=development` in your backend `.env` file.

## Next Steps

1. **Add Error Handling:** Implement proper error handling and user feedback
2. **Add Loading States:** Show loading indicators during API calls
3. **Add Offline Support:** Implement offline functionality with local storage
4. **Add Real-time Updates:** Use WebSockets for real-time features
5. **Add File Upload:** Implement file upload for document summarization
6. **Add Push Notifications:** Implement study reminders and notifications

This integration provides a solid foundation for connecting your frontend to the backend API. The backend handles all the complex logic while the frontend focuses on user experience.
