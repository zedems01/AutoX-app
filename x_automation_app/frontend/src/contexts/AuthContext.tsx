"use client"

import React, { createContext, useContext, useState, ReactNode, useEffect, useCallback } from 'react';
import { usePathname } from 'next/navigation';
import { validateSession } from '@/lib/api';
import { toast } from 'sonner';
import { UserDetails, UserSession } from '@/types';


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

const AUTH_STORAGE_KEY = 'x-auth-session';


const AuthContext = createContext<AuthContextType | undefined>(undefined);


interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const pathname = usePathname()
  const [authState, setAuthState] = useState<AuthState>({
    session: null,
    userDetails: null,
    proxy: null,
    authStatus: 'verifying',
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
    console.log('[Auth] AuthProvider mounted. Verifying session...');

    // Do not run session check on the demo login page
    if (pathname === "/demo-login") {
      console.log('[Auth] On demo page, skipping session verification.');
      setAuthState((s) => ({ ...s, authStatus: 'unauthenticated' }));
      return;
    }

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
        setTimeout(() => {
          setAuthState(s => ({ ...s, authStatus: 'unauthenticated' }));
        }, 0);
      }
    };

    verifyUserSession();
  }, [logout, pathname]);

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


export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 