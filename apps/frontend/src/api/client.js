import {
  clearClientSession,
  getRefreshToken,
  getSessionToken,
  saveClientSession,
} from "./consent";
import { waitForPendingConsentAcceptance } from "./pendingConsentInterceptor";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function parseResponseBody(response) {
  if (response.status === 204 || response.status === 205) {
    return null;
  }

  const contentType = response.headers.get("content-type");
  const contentLength = response.headers.get("content-length");

  if (contentLength === "0") {
    return null;
  }

  if (contentType?.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();
  return text || null;
}

async function request(path, options = {}, retryAfterConsent = true) {
  const token = getSessionToken();

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options?.method ?? "GET",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options?.headers,
    },
  });

  const responseBody = await parseResponseBody(response);

  if (!response.ok) {
    const error = new Error(`Erro na API: ${response.status}`);
    error.status = response.status;
    error.data = responseBody;

    if (retryAfterConsent && await shouldRefreshAuth(error, path)) {
      return request(path, options, false);
    }

    if (retryAfterConsent) {
      const shouldRetry = await waitForPendingConsentAcceptance(error);

      if (shouldRetry) {
        return request(path, options, false);
      }
    }

    throw error;
  }

  return responseBody;
}

async function shouldRefreshAuth(error, path) {
  if (path === "/auth/login" || path === "/auth/refresh") {
    return false;
  }

  if (error?.status !== 401) {
    return false;
  }

  const detail = error?.data?.detail;
  const refreshableDetails = new Set([
    "missing_authentication",
    "token_expired",
    "invalid_or_expired_session",
  ]);

  if (!refreshableDetails.has(detail)) {
    return false;
  }

  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    clearClientSession();
    return false;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    const responseBody = await parseResponseBody(response);

    if (!response.ok) {
      clearClientSession();
      return false;
    }

    saveClientSession(responseBody.access_token, {
      remember: localStorage.getItem("refresh_token") === refreshToken
        || localStorage.getItem("refreshToken") === refreshToken,
      refreshToken: responseBody.refresh_token,
    });

    return true;
  } catch {
    clearClientSession();
    return false;
  }
}

async function postFormRequest(
  path,
  formData,
  options = {},
  retryAfterConsent = true,
) {
  const token = getSessionToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    body: formData,
    // Do not set Content-Type for FormData; browser will set the correct boundary
    ...options,
    headers: {
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const responseBody = await parseResponseBody(response);

    const error = new Error(`Erro na API: ${response.status}`);
    error.status = response.status;
    error.data = responseBody;

    if (retryAfterConsent) {
      const shouldRetry = await waitForPendingConsentAcceptance(error);
      if (shouldRetry) {
        return postFormRequest(path, formData, options, false);
      }
    }

    throw error;
  }

  return parseResponseBody(response);
}

export const apiClient = {
  get: (path, options = {}) =>
    request(path, {
      method: "GET",
      ...options,
    }),

  post: (path, body, options = {}) =>
    request(path, {
      method: "POST",
      body: JSON.stringify(body),
      ...options,
    }),

  put: (path, body, options = {}) =>
    request(path, {
      method: "PUT",
      body: JSON.stringify(body),
      ...options,
    }),

  patch: (path, body, options = {}) =>
    request(path, {
      method: "PATCH",
      body: JSON.stringify(body),
      ...options,
    }),

  delete: (path, options = {}) =>
    request(path, {
      method: "DELETE",
      ...options,
    }),
  // Send FormData (file uploads). Caller must provide a FormData instance as `body`.
  postForm: (path, formData, options = {}) => postFormRequest(path, formData, options),
};
