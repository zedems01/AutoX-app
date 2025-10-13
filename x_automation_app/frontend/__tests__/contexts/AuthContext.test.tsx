import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import * as api from '@/lib/api';

jest.mock('@/lib/api');

// Test component that uses the auth context
const TestComponent = () => {
  const { session, userDetails, authStatus, login, logout } = useAuth();
  return (
    <div>
      <div data-testid="auth-status">{authStatus}</div>
      <div data-testid="session">{session || 'null'}</div>
      <div data-testid="username">{userDetails?.username || 'null'}</div>
      <button onClick={() => login({
        session: 'test-session',
        userDetails: { username: 'testuser' },
        proxy: 'http://proxy.com'
      })}>
        Login
      </button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('should initialize with verifying status', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('auth-status')).toHaveTextContent('verifying');
  });

  it('should update to unauthenticated when no session exists', async () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('unauthenticated');
    });
  });

  it('should login and save session to localStorage', async () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const loginButton = screen.getByText('Login');
    
    await act(async () => {
      loginButton.click();
    });

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated');
      expect(screen.getByTestId('session')).toHaveTextContent('test-session');
      expect(screen.getByTestId('username')).toHaveTextContent('testuser');
    });

    const storedData = localStorage.getItem('x-auth-session');
    expect(storedData).toBeTruthy();
    const parsed = JSON.parse(storedData!);
    expect(parsed.session).toBe('test-session');
  });

  it('should logout and clear localStorage', async () => {
    // First login
    localStorage.setItem('x-auth-session', JSON.stringify({
      session: 'test-session',
      userDetails: { username: 'testuser' },
      proxy: 'http://proxy.com'
    }));

    (api.validateSession as jest.Mock).mockResolvedValue({ isValid: true });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated');
    });

    const logoutButton = screen.getByText('Logout');
    
    await act(async () => {
      logoutButton.click();
    });

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('unauthenticated');
      expect(screen.getByTestId('session')).toHaveTextContent('null');
      expect(localStorage.getItem('x-auth-session')).toBeNull();
    });
  });

  it('should validate session on mount with valid session', async () => {
    localStorage.setItem('x-auth-session', JSON.stringify({
      session: 'valid-session',
      userDetails: { username: 'validuser' },
      proxy: 'http://proxy.com'
    }));

    (api.validateSession as jest.Mock).mockResolvedValue({ isValid: true });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated');
      expect(screen.getByTestId('username')).toHaveTextContent('validuser');
    });

    expect(api.validateSession).toHaveBeenCalledWith({
      session: 'valid-session',
      proxy: 'http://proxy.com'
    });
  });

  it('should logout when session validation fails', async () => {
    localStorage.setItem('x-auth-session', JSON.stringify({
      session: 'invalid-session',
      userDetails: { username: 'testuser' },
      proxy: 'http://proxy.com'
    }));

    (api.validateSession as jest.Mock).mockResolvedValue({ isValid: false });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('unauthenticated');
      expect(localStorage.getItem('x-auth-session')).toBeNull();
    });
  });

  it('should handle auth-error event and logout', async () => {
    localStorage.setItem('x-auth-session', JSON.stringify({
      session: 'test-session',
      userDetails: { username: 'testuser' },
      proxy: 'http://proxy.com'
    }));

    (api.validateSession as jest.Mock).mockResolvedValue({ isValid: true });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated');
    });

    // Dispatch auth-error event
    await act(async () => {
      window.dispatchEvent(new CustomEvent('auth-error'));
    });

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('unauthenticated');
      expect(localStorage.getItem('x-auth-session')).toBeNull();
    });
  });

  it('should throw error when useAuth is used outside provider', () => {
    // Suppress console.error for this test
    const spy = jest.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useAuth must be used within an AuthProvider');

    spy.mockRestore();
  });
});

