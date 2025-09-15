# Frontend Integration Guide

This guide explains how to integrate the StudyBuddy frontend with the Python FastAPI backend.

## 🔗 Base Configuration

Update your frontend configuration to point to the Python backend:

```typescript
// config/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api';

export const apiConfig = {
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
};
```

## 🔐 Authentication Integration

### 1. Update Auth Service

```typescript
// services/authService.ts
import { apiConfig } from '../config/api';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  name: string;
  password: string;
  avatar?: string;
}

export interface GoogleAuthRequest {
  email: string;
  name: string;
  avatar?: string;
  googleId?: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  data: {
    user: {
      id: string;
      email: string;
      name: string;
      avatar?: string;
      provider: string;
    };
    token: string;
  };
}

class AuthService {
  private baseURL = apiConfig.baseURL;

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await fetch(`${this.baseURL}/auth/register`, {
      method: 'POST',
      headers: apiConfig.headers,
      body: JSON.stringify(data),
    });
    return response.json();
  }

  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: apiConfig.headers,
      body: JSON.stringify(data),
    });
    return response.json();
  }

  async googleAuth(data: GoogleAuthRequest): Promise<AuthResponse> {
    const response = await fetch(`${this.baseURL}/auth/google`, {
      method: 'POST',
      headers: apiConfig.headers,
      body: JSON.stringify(data),
    });
    return response.json();
  }

  async getCurrentUser(token: string): Promise<AuthResponse> {
    const response = await fetch(`${this.baseURL}/auth/me`, {
      headers: {
        ...apiConfig.headers,
        Authorization: `Bearer ${token}`,
      },
    });
    return response.json();
  }

  async logout(): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${this.baseURL}/auth/logout`, {
      method: 'POST',
      headers: apiConfig.headers,
    });
    return response.json();
  }
}

export const authService = new AuthService();
```

### 2. Update Auth Context

```typescript
// contexts/AuthContext.tsx
import { createContext, useContext, useEffect, useState } from 'react';
import { authService, AuthResponse } from '../services/authService';

interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  provider: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, name: string, password: string) => Promise<void>;
  googleAuth: (email: string, name: string, avatar?: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      loadUser(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const loadUser = async (userToken: string) => {
    try {
      const response = await authService.getCurrentUser(userToken);
      if (response.success) {
        setUser(response.data.user);
      } else {
        localStorage.removeItem('token');
        setToken(null);
      }
    } catch (error) {
      console.error('Failed to load user:', error);
      localStorage.removeItem('token');
      setToken(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await authService.login({ email, password });
    if (response.success) {
      setUser(response.data.user);
      setToken(response.data.token);
      localStorage.setItem('token', response.data.token);
    } else {
      throw new Error(response.message);
    }
  };

  const register = async (email: string, name: string, password: string) => {
    const response = await authService.register({ email, name, password });
    if (response.success) {
      setUser(response.data.user);
      setToken(response.data.token);
      localStorage.setItem('token', response.data.token);
    } else {
      throw new Error(response.message);
    }
  };

  const googleAuth = async (email: string, name: string, avatar?: string) => {
    const response = await authService.googleAuth({ email, name, avatar });
    if (response.success) {
      setUser(response.data.user);
      setToken(response.data.token);
      localStorage.setItem('token', response.data.token);
    } else {
      throw new Error(response.message);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, googleAuth, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

## 📚 Study Tasks Integration

### 1. Update Study Tasks Service

```typescript
// services/studyTasksService.ts
import { apiConfig } from '../config/api';

export interface StudyTask {
  id: string;
  user_id: string;
  subject: string;
  topic: string;
  description?: string;
  duration: number;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  date: string;
  time: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  created_at: string;
  updated_at: string;
}

export interface CreateStudyTaskRequest {
  subject: string;
  topic: string;
  description?: string;
  duration: number;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  date: string;
  time: string;
}

export interface UpdateStudyTaskRequest {
  subject?: string;
  topic?: string;
  description?: string;
  duration?: number;
  priority?: 'LOW' | 'MEDIUM' | 'HIGH';
  date?: string;
  time?: string;
  status?: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
}

class StudyTasksService {
  private baseURL = apiConfig.baseURL;

  private async request(endpoint: string, options: RequestInit = {}) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${this.baseURL}/study-tasks${endpoint}`, {
      ...options,
      headers: {
        ...apiConfig.headers,
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });
    return response.json();
  }

  async getTasks(params?: {
    date?: string;
    status?: string;
    subject?: string;
  }): Promise<{ success: boolean; data: { tasks: StudyTask[] } }> {
    const queryParams = new URLSearchParams();
    if (params?.date) queryParams.append('date', params.date);
    if (params?.status) queryParams.append('status', params.status);
    if (params?.subject) queryParams.append('subject', params.subject);

    return this.request(`?${queryParams.toString()}`);
  }

  async getTask(id: string): Promise<{ success: boolean; data: { task: StudyTask } }> {
    return this.request(`/${id}`);
  }

  async createTask(data: CreateStudyTaskRequest): Promise<{ success: boolean; data: { task: StudyTask } }> {
    return this.request('', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTask(id: string, data: UpdateStudyTaskRequest): Promise<{ success: boolean; data: { task: StudyTask } }> {
    return this.request(`/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteTask(id: string): Promise<{ success: boolean; message: string }> {
    return this.request(`/${id}`, {
      method: 'DELETE',
    });
  }

  async toggleTaskStatus(id: string): Promise<{ success: boolean; data: { task: StudyTask } }> {
    return this.request(`/${id}/toggle-status`, {
      method: 'PATCH',
    });
  }

  async getStats(): Promise<{ success: boolean; data: any }> {
    return this.request('/stats/overview');
  }
}

export const studyTasksService = new StudyTasksService();
```

### 2. Update Study Planner Component

```typescript
// components/StudyPlanner.tsx
import { useState, useEffect } from 'react';
import { studyTasksService, StudyTask, CreateStudyTaskRequest } from '../services/studyTasksService';

export default function StudyPlanner() {
  const [tasks, setTasks] = useState<StudyTask[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const response = await studyTasksService.getTasks();
      if (response.success) {
        setTasks(response.data.tasks);
      }
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const createTask = async (taskData: CreateStudyTaskRequest) => {
    try {
      const response = await studyTasksService.createTask(taskData);
      if (response.success) {
        setTasks(prev => [...prev, response.data.task]);
      }
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  const updateTask = async (id: string, taskData: Partial<CreateStudyTaskRequest>) => {
    try {
      const response = await studyTasksService.updateTask(id, taskData);
      if (response.success) {
        setTasks(prev => prev.map(task => 
          task.id === id ? response.data.task : task
        ));
      }
    } catch (error) {
      console.error('Failed to update task:', error);
    }
  };

  const deleteTask = async (id: string) => {
    try {
      const response = await studyTasksService.deleteTask(id);
      if (response.success) {
        setTasks(prev => prev.filter(task => task.id !== id));
      }
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };

  const toggleTaskStatus = async (id: string) => {
    try {
      const response = await studyTasksService.toggleTaskStatus(id);
      if (response.success) {
        setTasks(prev => prev.map(task => 
          task.id === id ? response.data.task : task
        ));
      }
    } catch (error) {
      console.error('Failed to toggle task status:', error);
    }
  };

  // ... rest of your component implementation
}
```

## 📝 AI Summarizer Integration

### 1. Update Summarizer Service

```typescript
// services/summarizerService.ts
import { apiConfig } from '../config/api';

export interface Summary {
  id: string;
  user_id: string;
  title: string;
  original_text: string;
  summary_text: string;
  original_length: number;
  summary_length: number;
  language: string;
  type: 'BULLET' | 'PARAGRAPH' | 'DETAILED';
  created_at: string;
  updated_at: string;
}

export interface CreateSummaryRequest {
  original_text: string;
  type: 'BULLET' | 'PARAGRAPH' | 'DETAILED';
  language?: string;
  title?: string;
}

class SummarizerService {
  private baseURL = apiConfig.baseURL;

  private async request(endpoint: string, options: RequestInit = {}) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${this.baseURL}/summaries${endpoint}`, {
      ...options,
      headers: {
        ...apiConfig.headers,
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });
    return response.json();
  }

  async getSummaries(params?: {
    page?: number;
    limit?: number;
    type?: string;
    language?: string;
  }): Promise<{ success: boolean; data: { summaries: Summary[]; pagination: any } }> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.type) queryParams.append('type', params.type);
    if (params?.language) queryParams.append('language', params.language);

    return this.request(`?${queryParams.toString()}`);
  }

  async getSummary(id: string): Promise<{ success: boolean; data: { summary: Summary } }> {
    return this.request(`/${id}`);
  }

  async createSummary(data: CreateSummaryRequest): Promise<{ success: boolean; data: { summary: Summary } }> {
    return this.request('', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateSummary(id: string, data: { title?: string; summary_text?: string }): Promise<{ success: boolean; data: { summary: Summary } }> {
    return this.request(`/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteSummary(id: string): Promise<{ success: boolean; message: string }> {
    return this.request(`/${id}`, {
      method: 'DELETE',
    });
  }

  async getStats(): Promise<{ success: boolean; data: any }> {
    return this.request('/stats/overview');
  }
}

export const summarizerService = new SummarizerService();
```

### 2. Update AI Summarizer Component

```typescript
// components/AISummarizer.tsx
import { useState, useEffect } from 'react';
import { summarizerService, Summary, CreateSummaryRequest } from '../services/summarizerService';

export default function AISummarizer() {
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [loading, setLoading] = useState(false);

  const generateSummary = async (text: string, type: 'BULLET' | 'PARAGRAPH' | 'DETAILED', language: string = 'english') => {
    setLoading(true);
    try {
      const response = await summarizerService.createSummary({
        original_text: text,
        type,
        language,
      });
      
      if (response.success) {
        setSummaries(prev => [response.data.summary, ...prev]);
        return response.data.summary;
      } else {
        throw new Error('Failed to generate summary');
      }
    } catch (error) {
      console.error('Summary generation failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const loadSummaries = async () => {
    try {
      const response = await summarizerService.getSummaries({ limit: 10 });
      if (response.success) {
        setSummaries(response.data.summaries);
      }
    } catch (error) {
      console.error('Failed to load summaries:', error);
    }
  };

  useEffect(() => {
    loadSummaries();
  }, []);

  // ... rest of your component implementation
}
```

## 🧠 Quiz Generator Integration

### 1. Update Quiz Service

```typescript
// services/quizService.ts
import { apiConfig } from '../config/api';

export interface Quiz {
  id: string;
  user_id: string;
  title: string;
  subject: string;
  topic?: string;
  description?: string;
  time_limit: number;
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
  is_active: boolean;
  created_at: string;
  updated_at: string;
  question_count?: number;
  result_count?: number;
}

export interface Question {
  id: string;
  type: 'MCQ' | 'TRUE_FALSE' | 'FILL_BLANK';
  question: string;
  options?: string[];
  correct_answer: string;
  explanation: string;
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
  topic?: string;
  order: number;
}

export interface CreateQuizRequest {
  title: string;
  subject: string;
  topic?: string;
  description?: string;
  time_limit: number;
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
  num_questions: number;
  question_types: ('MCQ' | 'TRUE_FALSE' | 'FILL_BLANK')[];
  content?: string;
}

export interface QuizSubmission {
  answers: Array<{
    questionId: string;
    answer: string;
    timeSpent: number;
  }>;
  time_spent: number;
}

class QuizService {
  private baseURL = apiConfig.baseURL;

  private async request(endpoint: string, options: RequestInit = {}) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${this.baseURL}/quizzes${endpoint}`, {
      ...options,
      headers: {
        ...apiConfig.headers,
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });
    return response.json();
  }

  async getQuizzes(params?: {
    page?: number;
    limit?: number;
    subject?: string;
    difficulty?: string;
  }): Promise<{ success: boolean; data: { quizzes: Quiz[]; pagination: any } }> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.subject) queryParams.append('subject', params.subject);
    if (params?.difficulty) queryParams.append('difficulty', params.difficulty);

    return this.request(`?${queryParams.toString()}`);
  }

  async getQuiz(id: string): Promise<{ success: boolean; data: { quiz: Quiz & { questions: Question[] } } }> {
    return this.request(`/${id}`);
  }

  async createQuiz(data: CreateQuizRequest): Promise<{ success: boolean; data: { quiz: Quiz; questions: Question[] } }> {
    return this.request('', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async submitQuiz(id: string, submission: QuizSubmission): Promise<{ success: boolean; data: any }> {
    return this.request(`/${id}/submit`, {
      method: 'POST',
      body: JSON.stringify(submission),
    });
  }

  async getQuizResults(id: string): Promise<{ success: boolean; data: { results: any[] } }> {
    return this.request(`/${id}/results`);
  }

  async deleteQuiz(id: string): Promise<{ success: boolean; message: string }> {
    return this.request(`/${id}`, {
      method: 'DELETE',
    });
  }

  async getStats(): Promise<{ success: boolean; data: any }> {
    return this.request('/stats/overview');
  }
}

export const quizService = new QuizService();
```

## 💬 Chat Integration

### 1. Update Chat Service

```typescript
// services/chatService.ts
import { apiConfig } from '../config/api';

export interface ChatSession {
  id: string;
  user_id: string;
  title: string;
  subject: string;
  created_at: string;
  updated_at: string;
  last_message?: string;
  last_message_time?: string;
  message_count?: number;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  type: 'USER' | 'BOT';
  content: string;
  subject?: string;
  helpful?: boolean;
  attachments: string[];
  created_at: string;
}

export interface CreateSessionRequest {
  title: string;
  subject: string;
}

export interface SendMessageRequest {
  content: string;
  subject?: string;
  attachments?: string[];
}

class ChatService {
  private baseURL = apiConfig.baseURL;

  private async request(endpoint: string, options: RequestInit = {}) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${this.baseURL}/chat${endpoint}`, {
      ...options,
      headers: {
        ...apiConfig.headers,
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });
    return response.json();
  }

  async getSessions(params?: {
    page?: number;
    limit?: number;
    subject?: string;
  }): Promise<{ success: boolean; data: { sessions: ChatSession[]; pagination: any } }> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.subject) queryParams.append('subject', params.subject);

    return this.request(`/sessions?${queryParams.toString()}`);
  }

  async getSession(id: string): Promise<{ success: boolean; data: { session: ChatSession & { messages: ChatMessage[] } } }> {
    return this.request(`/sessions/${id}`);
  }

  async createSession(data: CreateSessionRequest): Promise<{ success: boolean; data: { session: ChatSession } }> {
    return this.request('/sessions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async sendMessage(sessionId: string, data: SendMessageRequest): Promise<{ success: boolean; data: { userMessage: ChatMessage; botMessage: ChatMessage } }> {
    return this.request(`/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async rateMessage(messageId: string, helpful: boolean): Promise<{ success: boolean; message: string }> {
    return this.request(`/messages/${messageId}/rate`, {
      method: 'PATCH',
      body: JSON.stringify({ helpful }),
    });
  }

  async deleteSession(id: string): Promise<{ success: boolean; message: string }> {
    return this.request(`/sessions/${id}`, {
      method: 'DELETE',
    });
  }

  async getStats(): Promise<{ success: boolean; data: any }> {
    return this.request('/stats/overview');
  }
}

export const chatService = new ChatService();
```

## 📊 Dashboard Integration

### 1. Update Dashboard Service

```typescript
// services/dashboardService.ts
import { apiConfig } from '../config/api';

class DashboardService {
  private baseURL = apiConfig.baseURL;

  private async request(endpoint: string, options: RequestInit = {}) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        ...apiConfig.headers,
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });
    return response.json();
  }

  async getDashboardData(): Promise<{ success: boolean; data: any }> {
    return this.request('/user/dashboard');
  }

  async getProgressOverview(): Promise<{ success: boolean; data: any }> {
    return this.request('/progress/overview');
  }

  async getStudyProgressBySubject(period: string = 'week'): Promise<{ success: boolean; data: any }> {
    return this.request(`/progress/study-by-subject?period=${period}`);
  }

  async getQuizPerformance(period: string = 'week'): Promise<{ success: boolean; data: any }> {
    return this.request(`/progress/quiz-performance?period=${period}`);
  }

  async getStreakData(): Promise<{ success: boolean; data: any }> {
    return this.request('/progress/streak');
  }

  async updateStreak(): Promise<{ success: boolean; data: any }> {
    return this.request('/progress/update-streak', {
      method: 'POST',
    });
  }
}

export const dashboardService = new DashboardService();
```

## 🔧 Error Handling

### 1. Create Error Handler

```typescript
// utils/errorHandler.ts
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export async function handleAPIResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new APIError(
      errorData.message || 'An error occurred',
      response.status,
      errorData.code
    );
  }

  const data = await response.json();
  if (!data.success) {
    throw new APIError(data.message || 'Request failed', response.status);
  }

  return data;
}
```

### 2. Update Service Methods

```typescript
// Example: Update authService with error handling
import { handleAPIResponse, APIError } from '../utils/errorHandler';

class AuthService {
  async login(data: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.baseURL}/auth/login`, {
        method: 'POST',
        headers: apiConfig.headers,
        body: JSON.stringify(data),
      });
      
      return await handleAPIResponse<AuthResponse>(response);
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError('Network error', 0);
    }
  }
}
```

## 🚀 Environment Variables

Add these to your `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:3001/api
NEXT_PUBLIC_APP_NAME=StudyBuddy
```

## 📱 Testing the Integration

1. **Start the Python backend**:
   ```bash
   cd backend-python
   uvicorn main:app --reload --host 0.0.0.0 --port 3001
   ```

2. **Start your frontend**:
   ```bash
   npm run dev
   ```

3. **Test authentication**:
   - Register a new user
   - Login with credentials
   - Check if JWT token is stored

4. **Test features**:
   - Create study tasks
   - Generate summaries
   - Create quizzes
   - Start chat sessions

## 🔍 Debugging

### 1. Check Network Requests
- Open browser DevTools
- Go to Network tab
- Monitor API calls and responses

### 2. Check Backend Logs
```bash
# Docker Compose
docker-compose logs -f backend

# Direct
tail -f logs/app.log
```

### 3. Common Issues

**CORS Errors**:
- Ensure `FRONTEND_URL` is set correctly in backend
- Check if frontend URL matches exactly

**Authentication Errors**:
- Verify JWT token is being sent
- Check token expiration
- Ensure user is logged in

**API Errors**:
- Check request format
- Verify required fields
- Check backend logs for details

## 🎉 Success!

Your frontend should now be fully integrated with the Python FastAPI backend. All features should work seamlessly with real data persistence and AI capabilities.

