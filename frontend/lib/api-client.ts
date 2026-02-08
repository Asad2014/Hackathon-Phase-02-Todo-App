import { getCookie } from 'cookies-next';

/* ======================================================
   API Base URL
====================================================== */
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8007'; // Default to 8007 to match backend

/* ======================================================
   Generic API Client
====================================================== */
interface ApiClientOptions extends RequestInit {
  requireAuth?: boolean;
}

export const apiClient = async <T>(
  endpoint: string,
  options: ApiClientOptions = {}
): Promise<T> => {
  const { requireAuth = true, headers, ...restOptions } = options;

  const url = `${API_BASE_URL}${endpoint}`;

  const requestHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(headers as Record<string, string>),
  };

  // Attach JWT automatically
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

    if (
      response.status === 204 ||
      response.headers.get('content-length') === '0'
    ) {
      return {} as T;
    }

    return await response.json();
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
};

/* ======================================================
   Auth API
====================================================== */
export const authApi = {
  login: (credentials: { email: string; password: string }) =>
    apiClient('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
      requireAuth: false,
    }),

  register: (userData: { email: string; password: string; name: string }) =>
    apiClient('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
      requireAuth: false,
    }),
};

/* ======================================================
   Tasks API
====================================================== */
export const tasksApi = {
  getAll: async (userId: string) => {
    // Use regular API for all users
    return apiClient<Task[]>(`/api/${userId}/tasks`);
  },

  getById: (userId: string, id: string) =>
    apiClient<Task>(`/api/${userId}/tasks/${id}`),

  create: async (userId: string, taskData: Partial<Omit<Task, 'id' | 'user_id'>>) => {
    // Use regular API for all users
    return apiClient<Task>(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  },

  update: async (userId: string, id: string, taskData: Partial<Task>) => {
    // Use regular API for all users
    return apiClient<Task>(`/api/${userId}/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  },

  delete: async (userId: string, id: string) => {
    // Use regular API for all users
    return apiClient(`/api/${userId}/tasks/${id}`, {
      method: 'DELETE',
    });
  },
};

/* ======================================================
   Task Type
====================================================== */
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