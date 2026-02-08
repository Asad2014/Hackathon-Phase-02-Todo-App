'use client';

import React, { useState, useEffect, useRef, createContext, useContext, useCallback } from 'react';
import { deleteCookie, setCookie, getCookie } from 'cookies-next';

// Global state to hold the session data
type SessionUser = {
  user: {
    id: string;
    email: string;
    name: string;
  };
  session: {
    id: string;
    userId: string;
    expiresAt: Date;
  };
};

// Initialize with loading state
let globalSessionData: {
  data: SessionUser | null;
  error: any;
  isPending: boolean;
  isRefetching: boolean;
} = {
  data: null, // Will be checked from backend on mount
  error: null,
  isPending: true, // Initially loading
  isRefetching: false,
};

// Function to check current session from backend
async function checkSession(): Promise<{ data: SessionUser | null; error: any }> {
  try {
    // Check if we have a session token in cookies
    const token = getCookie('better-auth.session_token');

    if (!token) {
      return { data: null, error: null };
    }

    // Verify the token by making a request to the backend
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8007'}/auth/me`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      credentials: 'include',
    });

    if (!response.ok) {
      // Log the error for debugging
      const errorText = await response.text().catch(() => '');
      console.error('Session check failed:', response.status, errorText);

      // If session is invalid (e.g. user not found), clear the invalid token
      if (response.status === 401) {
        // Remove the invalid session token from cookies
        deleteCookie('better-auth.session_token');
        globalSessionData.data = null;
        notifySubscribers();
      }

      // If session is not valid, return null
      return { data: null, error: null };
    }

    const userData = await response.json();

    if (userData) {
      // Transform backend user data to our format
      const transformedData: SessionUser = {
        user: {
          id: userData.id,
          email: userData.email,
          name: userData.name || userData.email?.split('@')[0] || 'User',
        },
        session: {
          id: `session-${Date.now()}`,
          userId: userData.id,
          expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours from now
        },
      };

      return { data: transformedData, error: null };
    } else {
      return { data: null, error: null };
    }
  } catch (error) {
    console.error('Error checking session:', error);
    // If API is not available, return null (assume not authenticated)
    return { data: null, error: null };
  }
}

// Define the AuthContext type
type AuthContextType = {
  session: typeof globalSessionData;
  signIn: (credentials: { email: string; password: string }) => Promise<{ data: SessionUser | null; error: string | null }>;
  signUp: (userData: { email: string; name: string; password: string }) => Promise<{ data: SessionUser | null; error: string | null }>;
  signOut: () => Promise<void>;
};

// Create authentication context with undefined as default (forces usage inside provider)
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Array to hold subscribers that need to be notified when the session changes
const subscribers: ((sessionData: typeof globalSessionData) => void)[] = [];

// Function to notify all subscribers when session changes
function notifySubscribers() {
  for (const subscriber of subscribers) {
    subscriber(globalSessionData);
  }
}

// Mock authentication provider component
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState(globalSessionData);

  useEffect(() => {
    // Check the current session from backend on mount
    const initializeSession = async () => {
      const { data, error } = await checkSession();

      // Update global state with session data
      globalSessionData.data = data;
      globalSessionData.error = error;
      globalSessionData.isPending = false; // No longer loading

      // Notify all subscribers of the updated state
      notifySubscribers();
    };

    initializeSession();

    const subscriber = (newSessionData: typeof globalSessionData) => {
      setSession({...newSessionData}); // Force re-render by creating new object
    };

    subscribers.push(subscriber);

    // Cleanup: remove subscriber when component unmounts
    return () => {
      const index = subscribers.indexOf(subscriber);
      if (index > -1) {
        subscribers.splice(index, 1);
      }
    };
  }, []);

  const signIn = useCallback(async (credentials: { email: string; password: string }) => {
    try {
      // Call the backend auth API
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8007'}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          email: credentials.email,
          password: credentials.password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || 'Sign in failed';
        return { data: null, error: errorMessage };
      }

      const result = await response.json();
      const token = result.access_token;

      if (token) {
        // Store the token in cookies (simulating better-auth session token)
        setCookie('better-auth.session_token', token, {
          maxAge: 30 * 24 * 60 * 60, // 30 days
          sameSite: true,
          path: '/',
        });

        // Get user data from the /me endpoint to get complete user information
        const userResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8007'}/auth/me`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          credentials: 'include',
        });

        if (!userResponse.ok) {
          return { data: null, error: 'Could not fetch user data after login' };
        }

        const userResult = await userResponse.json();

        const userData = {
          user: {
            id: userResult.id,
            email: userResult.email,
            name: userResult.name || userResult.email?.split('@')[0] || "User",
          },
          session: {
            id: `session-${Date.now()}`,
            userId: userResult.id,
            expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours from now
          },
        };

        globalSessionData.data = userData;
        notifySubscribers();
        return { data: userData, error: null };
      } else {
        return { data: null, error: 'Login successful but no token returned' };
      }
    } catch (error: any) {
      return { data: null, error: error.message || 'Network error' };
    }
  }, []);

  const signUp = useCallback(async (userData: { email: string; name: string; password: string }) => {
    try {
      // Call the backend auth API
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8007'}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          email: userData.email,
          name: userData.name,
          password: userData.password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || 'Sign up failed';
        return { data: null, error: errorMessage };
      }

      const result = await response.json();
      const token = result.access_token;

      if (token) {
        // Store the token in cookies (simulating better-auth session token)
        setCookie('better-auth.session_token', token, {
          maxAge: 30 * 24 * 60 * 60, // 30 days
          sameSite: true,
          path: '/',
        });

        // Get user data from the /me endpoint to get complete user information
        const userResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8007'}/auth/me`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          credentials: 'include',
        });

        if (!userResponse.ok) {
          return { data: null, error: 'Could not fetch user data after registration' };
        }

        const userResult = await userResponse.json();

        const newUser = {
          user: {
            id: userResult.id,
            email: userResult.email,
            name: userResult.name || userResult.email?.split('@')[0] || "New User",
          },
          session: {
            id: `session-${Date.now()}`,
            userId: userResult.id,
            expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours from now
          },
        };

        globalSessionData.data = newUser;
        notifySubscribers();
        return { data: newUser, error: null };
      } else {
        return { data: null, error: 'Registration successful but no token returned' };
      }
    } catch (error: any) {
      return { data: null, error: error.message || 'Network error' };
    }
  }, []);

  const signOut = useCallback(async () => {
    try {
      // Get the token to include in the logout request
      const token = getCookie('better-auth.session_token');

      if (token) {
        // Call the backend auth API to sign out
        await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8007'}/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        });
      }

      // Clear the session data
      globalSessionData.data = null;
      notifySubscribers();

      // Delete the better-auth cookie
      deleteCookie('better-auth.session_token');

      return Promise.resolve();
    } catch (error) {
      // Clear session data even if API call fails
      globalSessionData.data = null;
      notifySubscribers();
      deleteCookie('better-auth.session_token');
      throw error;
    }
  }, []);

  const value = {
    session,
    signIn,
    signUp,
    signOut
  };

  return React.createElement(
    AuthContext.Provider,
    { value: value },
    children
  );
}

// Export functions for direct usage (needed for imports in components)
export async function signIn(credentials: { email: string; password: string }) {
  // Implementation will use global session data
  try {
    // Call the backend auth API
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8007'}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        email: credentials.email,
        password: credentials.password,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || 'Sign in failed';
      return { data: null, error: errorMessage };
    }

    const result = await response.json();
    const token = result.access_token;

    if (token) {
      // Store the token in cookies (simulating better-auth session token)
      setCookie('better-auth.session_token', token, {
        maxAge: 30 * 24 * 60 * 60, // 30 days
        sameSite: true,
        path: '/',
      });

      // Get user data from the /me endpoint to get complete user information
      const userResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8007'}/auth/me`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include',
      });

      if (!userResponse.ok) {
        return { data: null, error: 'Could not fetch user data after login' };
      }

      const userResult = await userResponse.json();

      const userData = {
        user: {
          id: userResult.id,
          email: userResult.email,
          name: userResult.name || userResult.email?.split('@')[0] || "User",
        },
        session: {
          id: `session-${Date.now()}`,
          userId: userResult.id,
          expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours from now
        },
      };

      globalSessionData.data = userData;
      notifySubscribers();
      return { data: userData, error: null };
    } else {
      return { data: null, error: 'Login successful but no token returned' };
    }
  } catch (error: any) {
    return { data: null, error: error.message || 'Network error' };
  }
}

export async function signUp(userData: { email: string; name: string; password: string }) {
  // Implementation will use global session data
  try {
    // Call the backend auth API
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8007'}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        email: userData.email,
        name: userData.name,
        password: userData.password,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || 'Sign up failed';
      return { data: null, error: errorMessage };
    }

    const result = await response.json();
    const token = result.access_token;

    if (token) {
      // Store the token in cookies (simulating better-auth session token)
      setCookie('better-auth.session_token', token, {
        maxAge: 30 * 24 * 60 * 60, // 30 days
        sameSite: true,
        path: '/',
      });

      const newUser = {
        user: {
          id: result.userId || result.user_id || result.id,
          email: result.email || userData.email,
          name: result.name || userData.name || userData.email.split('@')[0] || "New User",
        },
        session: {
          id: `session-${Date.now()}`,
          userId: result.userId || result.user_id || result.id,
          expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours from now
        },
      };

      globalSessionData.data = newUser;
      notifySubscribers();
      return { data: newUser, error: null };
    } else {
      return { data: null, error: 'Registration successful but no token returned' };
    }
  } catch (error: any) {
    return { data: null, error: error.message || 'Network error' };
  }
}

export async function signOut() {
  try {
    // Get the token to include in the logout request
    const token = getCookie('better-auth.session_token');

    if (token) {
      // Call the backend auth API to sign out
      await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8002'}/auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });
    }

    // Clear the session data
    globalSessionData.data = null;
    notifySubscribers();

    // Delete the better-auth cookie
    deleteCookie('better-auth.session_token');

    return Promise.resolve();
  } catch (error) {
    // Clear session data even if API call fails
    globalSessionData.data = null;
    notifySubscribers();
    deleteCookie('better-auth.session_token');
    throw error;
  }
}

// Custom hook to use authentication context
export function useSession() {
  const context = useContext(AuthContext);
  if (!context) {
    // Fallback for when not wrapped in AuthProvider - use global state directly
    const [session, setSession] = useState(globalSessionData);

    useEffect(() => {
      // Initialize session from backend if not already done
      if (globalSessionData.isPending) {
        const initializeSession = async () => {
          const { data, error } = await checkSession();

          // Update global state with session data
          globalSessionData.data = data;
          globalSessionData.error = error;
          globalSessionData.isPending = false; // No longer loading

          // Notify all subscribers of the updated state
          notifySubscribers();
        };

        initializeSession();
      }

      const subscriber = (newSessionData: typeof globalSessionData) => {
        setSession({...newSessionData}); // Force re-render by creating new object
      };

      subscribers.push(subscriber);

      // Cleanup: remove subscriber when component unmounts
      return () => {
        const index = subscribers.indexOf(subscriber);
        if (index > -1) {
          subscribers.splice(index, 1);
        }
      };
    }, []);

    return session;
  }

  return {
    data: context.session?.data,
    error: context.session?.error,
    isPending: context.session?.isPending,
    isRefetching: context.session?.isRefetching,
  };
}