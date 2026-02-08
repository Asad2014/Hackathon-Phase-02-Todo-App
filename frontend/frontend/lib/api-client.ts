import { getCookie } from 'cookies-next';
import { useSession } from './auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

interface ApiClientOptions extends RequestInit {
  requireAuth?: boolean;
}

export const apiClient = async <T>(
  endpoint: string,
  options: ApiClientOptions = {}
): Promise<T> => {
  const { requireAuth = true, headers, ...restOptions } = options;

  // Replace {user_id} placeholder with actual user ID if available
  let processedEndpoint = endpoint;
  if (processedEndpoint.includes('{user_id}') || processedEndpoint.includes(':user_id')) {
    const token = getCookie('better-auth.session_token');
    if (token) {
      // Extract user ID from token - in a real implementation you'd decode the JWT
      // For now, we'll rely on the session context
    }
  }

  const url = `${API_BASE_URL}${processedEndpoint}`;

  // Prepare headers
  const requestHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(headers as Record<string, string>),
  };

  // Add JWT token if authentication is required
  if (requireAuth) {
    const token = getCookie('better-auth.session_token');
    if (token) {
      requestHeaders['Authorization'] = `Bearer ${token}`;
    }
  }

  try {
    const response = await fetch(url, {
      headers: requestHeaders,
      ...restOptions,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    // Handle empty responses
    if (response.status === 204 || response.headers.get('content-length') === '0') {
      return {} as T;
    }

    return await response.json();
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
};

// Enhanced API methods with user ID integration
export const tasksApi = {
  getAll: (userId: string) => apiClient<Task[]>(`/api/${userId}/tasks`),

  getById: (userId: string, id: string) => apiClient<Task>(`/api/${userId}/tasks/${id}`),

  create: (userId: string, taskData: Partial<Omit<Task, 'id' | 'userId'>>) =>
    apiClient<Task>(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(taskData),
    }),

  update: (userId: string, id: string, taskData: Partial<Task>) =>
    apiClient<Task>(`/api/${userId}/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    }),

  delete: (userId: string, id: string) =>
    apiClient(`/api/${userId}/tasks/${id}`, {
      method: 'DELETE',
    }),
};

// Specific API methods
export const authApi = {
  login: (credentials: { email: string; password: string }) =>
    apiClient('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
      requireAuth: false,
    }),

  register: (userData: { email: string; password: string; name: string }) =>
    apiClient('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
      requireAuth: false,
    }),
};

// Task type definition
export interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
  due_date?: string;
}