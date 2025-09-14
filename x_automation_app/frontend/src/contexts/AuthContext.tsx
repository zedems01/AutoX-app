"use client"

import React, { createContext, useContext, useState, ReactNode, useEffect, useCallback } from 'react';
import { validateSession } from '@/lib/api';
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
    console.log('[Auth] Logging out and clearing session.');
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
    console.log('[Auth] AuthProvider mounted. Verifying session...');
    const verifyUserSession = async () => {
      const storedSessionJSON = localStorage.getItem(AUTH_STORAGE_KEY);
      if (storedSessionJSON) {
        console.log('[Auth] Found session in localStorage. Validating...');
        try {
          const storedSession: UserSession = JSON.parse(storedSessionJSON);
          const { isValid } = await validateSession({ session: storedSession.session, proxy: storedSession.proxy });
          
          if (isValid) {
            console.log('[Auth] Session is valid. User authenticated.');
            setAuthState({
              ...storedSession,
              authStatus: 'authenticated',
            });
          } else {
            console.log('[Auth] Session is invalid. Logging out.');
            toast.error("Your session is invalid. Please log in again.", { duration: 15000 });
            logout();
          }
        } catch (error) {
          console.error('[Auth] Error verifying session:', error);
          toast.error("Your session has expired. Please log in again.", { duration: 15000 });
          logout();
        }
      } else {
        console.log('[Auth] No session found in localStorage. User unauthenticated.');
        setAuthState(s => ({ ...s, authStatus: 'unauthenticated' }));
      }
    };

    verifyUserSession();
  }, [logout]);

  useEffect(() => {
    // This effect listens for the global auth-error event to handle forced logouts
    const handleAuthError = () => {
      console.log('[Auth] Global auth-error event received. Forcing logout.');
      toast.error("Authentication error. You have been logged out.", { duration: 15000 });
      logout();
    };

    window.addEventListener('auth-error', handleAuthError);

    return () => {
      window.removeEventListener('auth-error', handleAuthError);
    };
  }, [logout]);


  const login = (authData: UserSession) => {
    console.log('[Auth] Logging in. Saving session to localStorage:', authData);
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