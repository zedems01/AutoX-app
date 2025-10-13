import { login, demoLogin, validateSession, startWorkflow, validateStep } from '@/lib/api';
import type { LoginPayload, StartWorkflowPayload, ValidationPayload } from '@/types';

// Mock fetch globally
global.fetch = jest.fn();

describe('API Functions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  describe('login', () => {
    it('should login successfully with valid credentials', async () => {
      const mockResponse = {
        session: 'test-session-cookie',
        userDetails: { name: 'Test User', username: 'testuser' },
        proxy: 'http://proxy.com',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const payload: LoginPayload = {
        user_name: 'testuser',
        email: 'test@example.com',
        password: 'password123',
        proxy: 'http://proxy.com',
        totp_secret: 'secret',
      };

      const result = await login(payload);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/login'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle login errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Invalid credentials' }),
      });

      const payload: LoginPayload = {
        user_name: 'testuser',
        email: 'test@example.com',
        password: 'wrongpass',
        proxy: 'http://proxy.com',
        totp_secret: 'secret',
      };

      await expect(login(payload)).rejects.toThrow('Invalid credentials');
    });
  });

  describe('demoLogin', () => {
    it('should login with demo token', async () => {
      const mockResponse = {
        session: 'demo-session',
        userDetails: { name: 'Demo User', username: 'demo' },
        proxy: 'http://proxy.com',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await demoLogin('demo-token-123');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/demo-login'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ token: 'demo-token-123' }),
        })
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('validateSession', () => {
    it('should validate a valid session', async () => {
      const mockResponse = { isValid: true };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await validateSession({
        session: 'test-session',
        proxy: 'http://proxy.com',
      });

      expect(result).toEqual(mockResponse);
    });

    it('should dispatch auth-error event on 401', async () => {
      const dispatchEventSpy = jest.spyOn(window, 'dispatchEvent');

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Unauthorized' }),
      });

      await expect(
        validateSession({ session: 'invalid', proxy: 'http://proxy.com' })
      ).rejects.toThrow('Unauthorized');

      expect(dispatchEventSpy).toHaveBeenCalledWith(
        expect.objectContaining({ type: 'auth-error' })
      );
    });
  });

  describe('startWorkflow', () => {
    it('should start workflow successfully', async () => {
      const mockResponse = {
        thread_id: 'test-thread-id',
        initial_state: {
          is_autonomous_mode: true,
          has_user_provided_topic: false,
          current_step: 'workflow_started',
          messages: [],
          search_query: [],
          web_research_result: [],
          sources_gathered: [],
          initial_search_query_count: 0,
          max_research_loops: 3,
          research_loop_count: 0,
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const payload: StartWorkflowPayload = {
        is_autonomous_mode: true,
        has_user_provided_topic: false,
        session: 'test-session',
        proxy: 'http://proxy.com',
      };

      const result = await startWorkflow(payload);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/workflow/start'),
        expect.objectContaining({
          method: 'POST',
        })
      );
      expect(result.thread_id).toBe('test-thread-id');
    });
  });

  describe('validateStep', () => {
    it('should validate step with approval', async () => {
      const mockState = {
        current_step: 'test_step',
        is_autonomous_mode: false,
        has_user_provided_topic: true,
        messages: [],
        search_query: [],
        web_research_result: [],
        sources_gathered: [],
        initial_search_query_count: 0,
        max_research_loops: 3,
        research_loop_count: 0,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockState,
      });

      const payload: ValidationPayload = {
        thread_id: 'test-thread-id',
        validation_result: {
          action: 'approve',
        },
      };

      const result = await validateStep(payload);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/workflow/validate'),
        expect.objectContaining({
          method: 'POST',
        })
      );
      expect(result).toEqual(mockState);
    });
  });
});

