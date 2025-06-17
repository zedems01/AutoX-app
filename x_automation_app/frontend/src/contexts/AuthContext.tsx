"use client"

import React, { createContext, useContext, useState, ReactNode } from 'react';

// --- Type Definitions ---

// A more specific type for userDetails can be created in types/index.ts later
type UserDetails = any;

type AuthStatus = 'verifying' | 'authenticated' | 'unauthenticated';

interface AuthState {
  session: string | null;
  userDetails: UserDetails | null;
  proxy: string | null;
  authStatus: AuthStatus;
}

interface AuthContextType extends AuthState {
  login: (authData: { session: string; userDetails: UserDetails; proxy: string }) => void;
  logout: () => void;
}

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

  // Login function updates state to authenticated
  const login = (authData: { session: string; userDetails: UserDetails; proxy: string }) => {
    setAuthState({
      session: authData.session,
      userDetails: authData.userDetails,
      proxy: authData.proxy,
      authStatus: 'authenticated',
    });
    // Persistence to localStorage will be added in the next step
  };

  // Logout function clears the state
  const logout = () => {
    setAuthState({
      session: null,
      userDetails: null,
      proxy: null,
      authStatus: 'unauthenticated',
    });
    // Clearing localStorage will be added in the next step
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