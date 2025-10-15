import {
  LoginPayload,
  LoginResponse,
  StartWorkflowPayload,
  StartWorkflowResponse,
  ValidateSessionPayload,
  ValidationPayload,
  OverallState,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function handleResponse<T>(response: Response): Promise<T> {
  if (response.status === 401) {
    // Dispatch a custom event to trigger logout
    window.dispatchEvent(new CustomEvent('auth-error'));
    const errorData = await response.json().catch(() => ({ detail: "Unauthorized" }));
    throw new Error(errorData.detail);
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "An unknown error occurred." }));
    throw new Error(errorData.detail || "Server returned an error");
  }
  return response.json();
}

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  // console.log("Payload for X login:", JSON.stringify(payload))
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<LoginResponse>(response);
}

export async function demoLogin(token: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/demo-login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });
  return handleResponse<LoginResponse>(response);
}

export async function validateSession(payload: ValidateSessionPayload): Promise<{ isValid: boolean }> {
  const response = await fetch(`${API_BASE_URL}/auth/validate-session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<{ isValid: boolean }>(response);
}

export async function startWorkflow(payload: StartWorkflowPayload): Promise<StartWorkflowResponse> {
  // console.log("Trying to start workflow with payload:", JSON.stringify(payload));
  const response = await fetch(`${API_BASE_URL}/workflow/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<StartWorkflowResponse>(response);
}

export async function validateStep(payload: ValidationPayload): Promise<OverallState> {
  const response = await fetch(`${API_BASE_URL}/workflow/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<OverallState>(response);
}

export async function stopWorkflow(threadId: string): Promise<{ success: boolean }> {
  const response = await fetch(`${API_BASE_URL}/workflow/stop`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ thread_id: threadId }),
  });
  return handleResponse<{ success: boolean }>(response);
}
