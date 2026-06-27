# STRIDE Threat Model Assessment: Shopping Assistant Agent

This document details the security threat model for the `shopping-assistant` agent using the STRIDE methodology.

---

## 1. System Boundaries & Data Flow

### Entry Points
* **Web UI / API**: Customers interact with the assistant via FastAPI endpoints (`/chat` or `/query`) or through the interactive playground.
* **LLM Orchestration**: The `root_agent` receives user inputs and orchestrates execution using the Gemini model.

### Data Storage
* **In-Memory Store (`REDEEMED_CODES_STORE`)**: A transient global dictionary tracking which discount codes have been claimed.
* **Static Configs**: Hardcoded dictionaries defining registered users (`REGISTERED_USER_IDS`) and valid codes (`VALID_DISCOUNT_CODES`).

---

## 2. STRIDE Evaluation

### 1. Spoofing (Identity Spoofing)
* **Risk**: High
* **Vulnerability**: The `redeem_discount_code` tool verifies the caller's identity solely based on a user-provided string (`user_id`).
* **Impact**: Anyone can spoof any registered user (e.g. by passing `user123`) to redeem their single-use discount code.
* **Mitigation**: Implement robust user authentication (e.g., OAuth2, JWT tokens verified in tool context) rather than trusting user-provided inputs.

### 2. Tampering (Data/Parameters Tampering)
* **Risk**: Medium
* **Vulnerability**: Discount state is managed via an in-memory dictionary `REDEEMED_CODES_STORE`. In a multi-threaded FastAPI application, there is no thread locking or synchronization.
* **Impact**: Concurrent requests using the same code can trigger a race condition (TOCTOU), allowing a single-use code to be redeemed multiple times before the state is updated.
* **Mitigation**: Use atomic operations or locking mechanisms (such as Redis or a persistent database transaction with transaction isolation) to prevent concurrent double-redemptions.

### 3. Repudiation
* **Risk**: High
* **Vulnerability**: There is no audit logging or persistent transaction ledger. All redemptions are kept in memory and disappear when the process restarts.
* **Impact**: Users can claim they never redeemed a code, and the system cannot cryptographically verify or prove that the transaction happened.
* **Mitigation**: Log all successful redemptions to a secure, write-only audit trail database or Cloud Logging with structured metadata.

### 4. Information Disclosure
* **Risk**: Critical
* **Vulnerability**:
  1. The API key for Gemini is hardcoded in the source code file `app/agent.py` (`api_key="AIzaSyD-mock-key-value-12345"`).
  2. Unhandled errors in custom tools may leak stack traces or internal store schemas to the LLM, which might output them in chat responses.
* **Impact**: Source code credential leakage and leakage of internal system structures to the chat interface.
* **Mitigation**:
  1. Remove hardcoded keys and load secrets from environment variables or GCP Secret Manager.
  2. Catch exceptions inside tools and return clean, user-friendly error messages instead of leaking technical details.

### 5. Denial of Service (DoS)
* **Risk**: Medium
* **Vulnerability**: No rate-limiting or query budget constraints are implemented on user endpoints or tool executions.
* **Impact**: An attacker can flood the `/chat` endpoint, causing excessive billing charges for the Gemini API or exhausting server resources.
* **Mitigation**: Configure rate-limiters at the API gateway or FastAPI application layer.

### 6. Elevation of Privilege
* **Risk**: Low
* **Vulnerability**: The current model has flat permissions; any registered user can call the only available tool.
* **Impact**: Low, but if admin tools are added in the future, lack of Role-Based Access Control (RBAC) could allow regular users to run privileged commands.
* **Mitigation**: Implement proper authorization checks (RBAC) in `ToolContext` before executing sensitive tool logic.

---

## 3. Actionable Security Recommendations

1. **Secret Management**: Move the API key out of [app/agent.py](file:///C:/Users/ayush_6ot02l6/shopping-assistant-secure-agent/shopping-assistant/app/agent.py) to a `.env` file or Secret Manager.
2. **Authentication**: Require token-based verification for `user_id` inside the redemption tool.
3. **State Persistence**: Transition the in-memory redemption store to a persistent database using transactions to prevent race conditions and loss of state.
4. **Rate Limiting**: Set up rate limiting to prevent API budget exhaustion.
