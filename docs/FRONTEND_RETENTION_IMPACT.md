# Frontend Impact Analysis: Access Log Retention Policy

## Overview

This document analyzes potential impacts of the 90-day access log retention policy on the frontend application, including session management, error handling, and user experience considerations.

---

## 🎯 Session Management

### Current Frontend Behavior

The frontend (`apps/frontend/src/`) manages sessions through:

1. **Token Storage**
   - Access token: Short-lived (15 minutes by default)
   - Refresh token: 7 days retention
   - Stored in browser memory/localStorage

2. **Token Retrieval** (`src/api/client.js`)
   ```javascript
   const token = getSessionToken();  // From consent.js
   ```

3. **Automatic Refresh** (via `pendingConsentInterceptor.js`)
   - Refreshes on 401 Unauthorized response
   - Handles pending consent flow

### Retention Policy Impact: NONE ✅

**Reason**: The frontend's JWT tokens have independent lifecycles:
- Access tokens expire in 15 minutes (backend enforces)
- Refresh tokens expire in 7 days (backend enforces)
- Neither depends on TB_SESSION records

**Session database deletion (SOFT DELETE)** won't affect:
- Active user sessions (deleted only after 90+ days of inactivity)
- Token validation (performed via JWT verification)
- Session refresh operations (use JWT refresh token)

---

## 🔐 Authentication Flow

### Login Flow Analysis

```
User Input (email/password)
         ↓
POST /auth/login
         ↓
Backend validates credentials → Creates TB_SESSION record
         ↓
Backend returns access_token + refresh_token
         ↓
Frontend stores tokens in memory
         ↓
Frontend uses access_token in Authorization header
```

### Retention Policy Impact: NONE ✅

**Reason**: 
- Frontend doesn't directly query or depend on TB_SESSION table
- Backend JWT validation is stateless (verification key, not database lookup)
- Soft-delete (set DELETED_AT) happens only after 90 days of inactivity

**What changes**:
- Very old inactive sessions will be marked as deleted
- Active sessions (refreshed within 90 days) will NOT be affected
- Session validation still works via JWT verification

---

## 🔄 Token Refresh

### Refresh Token Endpoint

Current implementation (`src/api/client.js` → `POST /auth/refresh`):

```javascript
export function refreshToken(payload) {
  return apiClient.post("/auth/refresh", payload);
}
```

### Retention Policy Impact: NONE ✅

**Reason**:
- Refresh endpoint validates JWT signature, not database lookup
- Token expiration is controlled by JWT exp claim
- Backend checks TB_SESSION during refresh, but will only find active sessions
- Soft-deleted sessions (90+ days) would be skipped anyway

**What happens if user's old session is soft-deleted**:
- If user hasn't logged in for 90+ days → old session is marked deleted
- User tries to refresh with old token → endpoint looks up TB_SESSION
- Query filters: `WHERE DELETED_AT IS NULL` → returns nothing
- User is logged out (correct behavior)
- User must login again (expected)

---

## 📊 Data Export & Session History

### Export Endpoints

The backend provides data export functionality:
- `GET /auth/me/export` - User personal data + session history
- Uses `get_sessions_for_export()` repository function

### Retention Policy Impact: POSSIBLE ⚠️

**Potential Issue**:
- User's session history export might not show sessions older than 90 days
- Soft-deleted sessions have `DELETED_AT` set, but not hard-deleted
- Export query should specifically handle this

**Current Query** (from user_repository.py):
```python
# Check if export query filters deleted sessions
SELECT ... FROM TB_SESSION 
WHERE USER_ID = %s
  AND DELETED_AT IS NULL  # This would exclude soft-deleted sessions!
```

**Frontend Impact**:
- ✅ No UI changes needed
- ⚠️ User's exported data will not include sessions older than 90 days
- ⚠️ This is actually CORRECT for LGPD compliance (shouldn't export deleted data)

**Recommended Frontend Notes**:
- Add UI hint: "Session history shows last 90 days"
- In data export success message: "Session history from last 90 days included"

---

## 🚨 Error Handling

### Current Error Scenarios

Frontend error handling (`src/api/client.js`):

```javascript
if (!response.ok) {
    const error = new Error(`Erro na API: ${response.status}`);
    error.status = response.status;
    error.data = responseBody;
    throw error;
}
```

### Retention Policy Impact: NONE ✅

**Reason**:
- Cleanup is automatic, doesn't generate new errors
- Failed cleanups are logged server-side, not returned to frontend
- API endpoints remain stable

**Potential errors (server-side, not visible to frontend)**:
- Failed to delete old auth attempts (server logs it)
- Failed to soft-delete old sessions (server logs it)
- These are handled gracefully in service layer

---

## 🔐 JWT Security & Token Validation

### JWT Validation Process

Current security model (from `src/config/auth_security.py`):
1. Token signature verified with JWT_SECRET_KEY
2. Claims checked (exp, sub, iat, etc.)
3. Session ID validation (if needed)

### Retention Policy Impact: NONE ✅

**Reason**:
- JWT validation is **cryptographic** (signature-based), not **database-dependent**
- Backend doesn't need to look up JWT tokens in database
- Soft-deleting sessions won't invalidate valid JWT tokens

**Edge case**: Session revocation
- Frontend: Not aware sessions were revoked
- Backend: May reject refresh if session is soft-deleted
- Result: User gets 401, logs out (correct behavior)

---

## 📱 Session Persistence

### Frontend Session Storage

Current implementation uses:
- React state for authentication context
- localStorage for persistence (check `src/hooks/`)

### Retention Policy Impact: NONE ✅

**Reason**:
- Frontend session storage is separate from backend database
- Cleanup only affects backend's TB_SESSION table
- Frontend stores JWT tokens, not database references

**What persists in frontend**:
- JWT access token (in memory)
- JWT refresh token (in memory/storage)
- User profile information (from `GET /auth/me`)

**What's deleted on backend**:
- TB_SESSION records (database soft-delete)
- TB_AUTH_ATTEMPT records (database hard-delete)

---

## 🎯 Pending Consent Integration

### Current Flow

The consent middleware (`src/api/pendingConsentInterceptor.js`) handles:
```javascript
// Waits for pending consent acceptance before retrying request
const shouldRetry = await waitForPendingConsentAcceptance(error);
```

### Retention Policy Impact: NONE ✅

**Reason**:
- Consent logic is independent of session retention
- TB_CONSENT_LOG has its own retention (append-only, not deleted)
- Auth flow is unchanged

---

## 📋 Recommended Frontend Changes

### 1. Add Session History Disclaimer

**File**: `apps/frontend/src/pages/Profile.jsx` or similar

```jsx
export function SessionHistory() {
  return (
    <div>
      <h2>Session History</h2>
      <p className="text-sm text-muted-foreground">
        ℹ️ Showing session history from the last 90 days (LGPD compliance).
        Older sessions are automatically deleted according to retention policy.
      </p>
      {/* ... sessions list ... */}
    </div>
  );
}
```

### 2. Update Data Export Messaging

**File**: `apps/frontend/src/pages/DataExport.jsx`

```jsx
export function DataExportInfo() {
  return (
    <div className="alert alert-info">
      <p>
        Your data export includes information from the last 90 days.
        Authentication logs older than 90 days are automatically deleted
        in compliance with LGPD data protection requirements.
      </p>
      <ul className="mt-2 text-sm">
        <li>✓ Personal profile data: All</li>
        <li>✓ Session history: Last 90 days</li>
        <li>✓ Consent history: All</li>
        <li>✓ Access logs: Last 90 days</li>
      </ul>
    </div>
  );
}
```

### 3. Add Logout Handling for Soft-Deleted Sessions

**File**: `apps/frontend/src/api/client.js`

```javascript
async function request(path, options = {}, retryAfterConsent = true) {
  const token = getSessionToken();

  const response = await fetch(`${API_BASE_URL}${path}`, {
    // ... existing code ...
  });

  if (response.status === 401) {
    // Could mean: token expired, session deleted, or invalid refresh
    console.warn('Session appears to be invalid - may have been deleted due to inactivity');
    // Clear token and redirect to login
    clearSessionToken();
    window.location.href = '/login';
  }

  // ... rest of handler ...
}
```

### 4. Test Scenarios for Frontend

**Manual Testing Checklist**:

- [ ] User with active session (< 90 days) can refresh token
- [ ] User exports data sees "last 90 days" note
- [ ] Session history only shows recent sessions
- [ ] Login/logout flow unchanged
- [ ] Error handling on 401/403 unchanged
- [ ] Consent flow unchanged
- [ ] Pending consent enforcement unchanged

---

## 🚫 What Does NOT Change

### Frontend-Facing APIs

| Endpoint | Impact | Notes |
|----------|--------|-------|
| `POST /auth/login` | None | User can always login |
| `POST /auth/refresh` | None | Refresh works if session exists |
| `GET /auth/me` | None | Returns user profile always |
| `POST /auth/logout` | None | Always invalidates session |
| `POST /auth/forgot-password` | None | Independent of sessions |
| `POST /auth/reset-password` | None | Independent of sessions |
| `GET /auth/me/export` | Minor* | May not include 90+ day old data |
| `GET /auth/sessions` | Minor* | Won't show soft-deleted sessions |

*Minor impact: Data will be excluded, but this is correct behavior

---

## 🔗 Related Documentation

- [LOG_RETENTION_POLICY.md](./LOG_RETENTION_POLICY.md) - Complete retention policy details
- [LGPD.md](./LGPD.md) - Overall LGPD compliance architecture
- [AUTH_ARCHITECTURE.md](./AUTH_ARCHITECTURE.md) - Authentication system design
- [backend code](../apps/backend/) - Implementation details

---

## ✅ Summary

| Aspect | Impact | Severity | Action |
|--------|--------|----------|--------|
| Session Authentication | None | ✅ | No changes needed |
| Token Validation | None | ✅ | No changes needed |
| Login/Logout Flow | None | ✅ | No changes needed |
| Token Refresh | None | ✅ | No changes needed |
| Consent Flow | None | ✅ | No changes needed |
| Data Export | Minor | ⚠️ | Add UI note about 90-day limit |
| Session History | Minor | ⚠️ | Update to show 90-day note |
| Error Handling | None | ✅ | No changes needed |
| JWT Security | None | ✅ | No changes needed |

**Conclusion**: The retention policy is **completely backend-driven** and requires only **minor UI enhancements** for user transparency. No breaking changes to existing frontend functionality.

---

**Last Updated**: May 25, 2026  
**Status**: Implementation-Ready  
**Review Date**: August 25, 2026 (after 90-day retention cycle)
