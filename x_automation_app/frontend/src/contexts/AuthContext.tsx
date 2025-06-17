"use client"

import React, { createContext, useContext, useState, ReactNode, useEffect, useCallback } from 'react';
// import { validateSession } from '@/lib/api'; // This will be created in a later step
import { toast } from 'sonner';

// --- Type Definitions ---

// A more specific type for userDetails can be created in types/index.ts later
type UserDetails = any;

interface UserSession {
  session: string;
  userDetails: UserDetails;
  proxy: string;
}

type AuthStatus = 'verifying' | 'authenticated' | 'unauthenticated';

interface AuthState {
  session: string | null;
  userDetails: UserDetails | null;
  proxy: string | null;
  authStatus: AuthStatus;
}

interface AuthContextType extends AuthState {
  login: (authData: UserSession) => void;
  logout: () => void;
}

// --- Constants ---
const AUTH_STORAGE_KEY = 'x-auth-session';

// --- Context ---

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// --- Provider Component ---

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [authState, setAuthState] = useState<AuthState>({
    session: null,
    userDetails: null,
    proxy: null,
    authStatus: 'verifying', // Default status on initial load
  });

  const logout = useCallback(() => {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    setAuthState({
      session: null,
      userDetails: null,
      proxy: null,
      authStatus: 'unauthenticated',
    });
  }, []);

  useEffect(() => {
    // This effect handles the initial session verification on app load
    const verifyUserSession = async () => {
      const storedSessionJSON = localStorage.getItem(AUTH_STORAGE_KEY);
      if (storedSessionJSON) {
        try {
          const storedSession: UserSession = JSON.parse(storedSessionJSON);
          // TODO: Replace with actual API call once `validateSession` is implemented in api.ts
          // For now, we'll simulate a successful validation.
          // await validateSession({ session: storedSession.session, proxy: storedSession.proxy });
          
          setAuthState({
            ...storedSession,
            authStatus: 'authenticated',
          });
        } catch (error) {
          toast.error("Your session has expired. Please log in again.");
          logout();
        }
      } else {
        setAuthState(s => ({ ...s, authStatus: 'unauthenticated' }));
      }
    };

    verifyUserSession();
  }, [logout]);

  useEffect(() => {
    // This effect listens for the global auth-error event to handle forced logouts
    const handleAuthError = () => {
      toast.error("Authentication error. You have been logged out.");
      logout();
    };

    window.addEventListener('auth-error', handleAuthError);

    return () => {
      window.removeEventListener('auth-error', handleAuthError);
    };
  }, [logout]);


  const login = (authData: UserSession) => {
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(authData));
    setAuthState({
      ...authData,
      authStatus: 'authenticated',
    });
  };

  const value = { ...authState, login, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// --- Custom Hook ---

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 