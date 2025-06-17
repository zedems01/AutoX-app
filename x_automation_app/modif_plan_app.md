# Implementation Plan: Decoupled & Persistent User Authentication

This document outlines the detailed implementation plan to refactor the authentication system. The goal is to decouple user authentication from the workflow lifecycle, persist user sessions for a better user experience, and only require login when absolutely necessary.

---

## **Part 1: Backend Refactoring**

The backend will be modified to treat authentication as a stateless service, allow workflows to start without a user session, and provide an endpoint for proactive session validation.

### [ ] **Phase 1.1: Make Authentication Endpoints Stateless**

**File:** `x_automation_app/backend/app/main.py`

[x] 1.1.1.  **Update API Payloads:**
    *   Modify `CompleteLoginPayload` to remove `thread_id` and include all necessary data for the stateless call.
        ```python
        class CompleteLoginPayload(BaseModel):
            login_data: str # From start_login
            two_fa_code: str
            proxy: str
        ```
    *   The `StartLoginPayload` is already stateless and correct.

[x] 1.1.2.  **Refactor `/auth/start-login`:**
    *   This endpoint becomes purely stateless. Its only job is to call the `x_utils.start_login` service and return the `login_data`.
    *   **Remove all logic related to creating a `thread_id` and updating the LangGraph state.**
    *   The response should be a simple JSON object: `{ "login_data": "..." }`.

[x] 1.1.3.  **Refactor `/auth/complete-login`:**
    *   This endpoint also becomes purely stateless.
    *   **Remove all logic related to `thread_id` and graph state.**
    *   It will call `x_utils.complete_login` with the data from the `CompleteLoginPayload`.
    *   On success, it will **return a complete authentication object** directly to the frontend. This is the new contract with the client.
        ```json
        // Example Success Response
        {
          "session": "the-session-token",
          "userDetails": { ... },
          "proxy": "http://user:pass@ip:port"
        }
        ```

### [ ] **Phase 1.2: Adjust Workflow Start Endpoint**

**File:** `x_automation_app/backend/app/main.py`

[x] 1.2.1.  **Update `StartWorkflowPayload`:**
    *   Remove the `thread_id` field.
    *   Add optional fields to accept a complete authentication context from an already logged-in user.
        ```python
        class StartWorkflowPayload(BaseModel):
            # NO thread_id
            is_autonomous_mode: bool
            # ... other existing fields ...

            # New optional fields for auth context
            session: Optional[str] = None
            user_details: Optional[dict] = None
            proxy: Optional[str] = None
        ```

[x] 1.2.2.  **Modify `/workflow/start` Endpoint Logic:**
    *   **Generate a new `thread_id`** inside this endpoint for every new workflow using `uuid.uuid4()`.
    *   **Remove the session validation guard clause.** The check for `current_state.values.get("session")` must be deleted.
    *   When initializing the `OverallState` for the new graph, directly inject the optional `session`, `user_details`, and `proxy` from the payload.
        ```python
        # Inside /workflow/start
        initial_state: OverallState = {
            # ... other initial fields ...
            "session": payload.session,
            "user_details": payload.user_details,
            "proxy": payload.proxy,
            # ...
        }
        graph.update_state(config, initial_state)
        ```
    *   **Return the new `thread_id`** to the frontend in the response, along with the initial state from the graph invocation.
        ```json
        // Example Success Response
        {
          "thread_id": "newly-generated-uuid-string",
          "initial_state": { ... } // Full OverallState object
        }
        ```

### [ ] **Phase 1.3: Implement Publicator Guard Clause**

**File:** `x_automation_app/backend/app/agents/publicator.py`

[x] 1.3.1.  **Add Check in `publicator_node`:**
    *   At the very beginning of the node's logic, insert the guard clause to ensure a session exists *only when* publishing is the goal.
    ```python
    # At the top of publicator_node function
    if state.get("output_destination") == "PUBLISH_X":
        if not state.get("session"):
            # This error will be caught by FastAPI and returned as a 500.
            # We add a separate reactive check for expired sessions.
            raise ValueError("Authentication session is required to publish on X. Please log in.")
    
    # ... rest of the existing publicator code ...
    ```

### [ ] **Phase 1.4: Add Proactive Session Validation Endpoint (New)**

**Goal:** Prevent a user with an expired session from starting a long workflow.

[x] 1.4.1.  **Create Service Function (`utils/x_utils.py`):**
    *   Implement a new function `verify_session(session: str, proxy: str, api_key: str = settings.X_API_KEY) -> dict`.
    *   This function will make a low-cost, read-only call to `twitterapi.io`:

    ```python
    # Get tweets from this endpoint
    # url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    # params = {"query": query, "query_type": "Latest"}
    # headers = {"X-API-Key": api_key}
    # with this query: "Real Madrid min_faves:500"
    # then retrieve the "id" of the first tweet
    # Look at the function tweet_advanced_search to search how to extract

    # Then use this endpoint to test the session

    import requests

    url = "https://api.twitterapi.io/twitter/like_tweet"

    payload = {
        "auth_session": "<string>",
        "tweet_id": "<string>",
        "proxy": "<string>"
    }
    headers = {
        "X-API-Key": "<api-key>",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    # response
    # {
    # "status": "<string>",      # Status of the request.success or error
    # "msg": "<string>"          # Message of the request.error message
    # }
    ```
    *   If the session is invalid, the API call will fail. The function should catch this and raise a specific `InvalidSessionError` (custom exception).

[x] 1.4.2.  **Create Validation Endpoint (`main.py`):**
    *   Implement a new endpoint: `POST /auth/validate-session`.
    *   It will accept a payload with `session` and `proxy`.
    *   It will call the `verify_session` service function within a `try...except` block.
    *   **On Success:** Return a `200 OK` with `{ "isValid": true, "userDetails": ... }`.
    *   **On Failure (`InvalidSessionError`):** Catch the specific error and return an `HTTPException` with status `401 Unauthorized`.

---

## **Part 2: Frontend Refactoring**

The frontend will be overhauled to manage a global, persistent authentication state, adapt its UI flow, and proactively validate stored sessions.

### **Phase 2.1: Create Global Authentication Context**

**New File:** `x_automation_app/frontend/src/contexts/AuthContext.tsx`

[x] 2.1.1.  **Define Context and Provider:**
    *   Create a new React Context to manage `session`, `userDetails`, `proxy`, and an authentication status flag (`'verifying'`, `'authenticated'`, `'unauthenticated'`).
    *   The provider will contain the state and `login`/`logout` methods.

[ ] 2.1.2.  **Implement Enhanced `localStorage` Persistence:**
    *   **On App Load:**
        *   The context will default to a `'verifying'` status.
        *   It will attempt to load the session object from `localStorage`.
        *   If a session is found, it will immediately call the new `POST /auth/validate-session` endpoint.
        *   If the API returns `200 OK`, switch status to `'authenticated'` and update user details.
        *   If the API returns `401 Unauthorized`, call the internal `logout()` function to clear state/storage and switch status to `'unauthenticated'`.
        *   If no session is found in `localStorage`, switch status to `'unauthenticated'`.
    *   The `login` function will save the complete auth object to `localStorage`.
    *   The `logout` function will clear the auth object from both the context state and `localStorage`.

### **Phase 2.2: Update Data Types and API Layer**

**[ ] 2.2.1 File:** `x_automation_app/frontend/src/types/index.ts`
*  **Update Payloads:** Modify `CompleteLoginPayload` and `StartWorkflowPayload` interfaces to match the backend changes. Add a `ValidateSessionPayload`.
*  **Create Auth Types:** Define an interface for the auth object (e.g., `UserSession`).

**[ ] 2.2.2 File:** `x_automation_app/frontend/src/lib/api.ts`
*  **Add `validateSession` function.**
*  **Update `completeLogin` and `startWorkflow`** with the new payload and response types.
*  **Implement Reactive Error Handling:**
    *   Modify the `handleResponse` function or wrap `fetch` calls.
    *   If a response returns a `401 Unauthorized` or `403 Forbidden` status, it should programmatically trigger the `logout` function from the `AuthContext` to clear the invalid session and redirect the user.

### **Phase 2.3: Integrate AuthProvider and Refactor UI**

**[ ] 2.3.1 File:** `x_automation_app/frontend/src/app/layout.tsx`
*   Wrap the entire application with the new `AuthProvider` to make the authentication state globally available.

**[ ] 2.3.2 Files:** `x_automation_app/frontend/src/app/login/**/*.tsx`
1.  **Remove `thread_id` logic.**
2.  Refactor forms to call the new stateless API functions.
3.  On successful login, call the `login` method from `AuthContext` with the data returned by the API.
4.  Redirect the user to the main workflow page (`/`) upon successful login.

**[ ] 2.3.3 File:** `x_automation_app/frontend/src/app/page.tsx`
1.  **Invert the UI logic:**
    *   The page should now be accessible to everyone.
    *   Use the `useAuth` hook to get the current authentication status. The UI can show a loading spinner while the status is `'verifying'`.
2.  **Modify "Start Workflow" Button Handler:**
    *   When clicked, check `if (output_destination === 'PUBLISH_X' && authStatus !== 'authenticated')`.
    *   If `true`, prevent the API call and instead show a login prompt (e.g., a modal or redirect to `/login`).
    *   If `false`, proceed to call the `startWorkflow` API function.
3.  **Enrich the Payload:** When calling `startWorkflow`, include the `session`, `userDetails`, and `proxy` from the `AuthContext` if the user is authenticated.
4.  **Handle the Response:** On a successful response from `startWorkflow`, extract the new `thread_id` and use it to navigate to the dashboard page (`/workflow/[threadId]`).
