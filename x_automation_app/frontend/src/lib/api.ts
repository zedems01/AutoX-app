import {
  CompleteLoginPayload,
  CompleteLoginResponse,
  OverallState,
  StartLoginPayload,
  StartLoginResponse,
  StartWorkflowPayload,
  ValidationPayload,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "An unknown error occurred." }));
    throw new Error(errorData.detail || "Server returned an error");
  }
  return response.json();
}

export async function startLogin(payload: StartLoginPayload): Promise<StartLoginResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/start-login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<StartLoginResponse>(response);
}

export async function completeLogin(payload: CompleteLoginPayload): Promise<CompleteLoginResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/complete-login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<CompleteLoginResponse>(response);
}

export async function startWorkflow(payload: StartWorkflowPayload): Promise<OverallState> {
  const response = await fetch(`${API_BASE_URL}/workflow/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<OverallState>(response);
}

export async function validateStep(payload: ValidationPayload): Promise<OverallState> {
  const response = await fetch(`${API_BASE_URL}/workflow/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<OverallState>(response);
}
