const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const PENDING_CONSENT_EVENT = "app:pending-consent";

const SESSION_KEYS = [
  "session_uuid",
  "sessionUuid",
  "access_token",
  "accessToken",
  "token",
];

function getSessionToken() {
  for (const key of SESSION_KEYS) {
    const sessionValue = sessionStorage.getItem(key);
    const localValue = localStorage.getItem(key);

    if (sessionValue) return sessionValue;
    if (localValue) return localValue;
  }

  return null;
}

function buildJsonHeaders(headers = {}) {
  const token = getSessionToken();

  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...headers,
  };
}

function buildFormHeaders(headers = {}) {
  const token = getSessionToken();

  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...headers,
  };
}

async function parseResponse(response) {
  const contentType = response.headers.get("content-type");

  if (contentType && contentType.includes("application/json")) {
    return response.json();
  }

  return response.text();
}

function notifyPendingConsent(payload) {
  if (typeof window === "undefined") return;

  window.dispatchEvent(
    new CustomEvent(PENDING_CONSENT_EVENT, {
      detail: payload,
    }),
  );
}

function createApiError(response, payload) {
  const error = new Error(`Erro na API: ${response.status}`);
  error.status = response.status;
  error.payload = payload;

  return error;
}

async function request(path, options = {}) {
  const { headers = {}, ...restOptions } = options;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...restOptions,
    headers: buildJsonHeaders(headers),
  });

  const payload = await parseResponse(response);

  if (!response.ok) {
    if (response.status === 403 && payload?.detail === "pending_consent") {
      notifyPendingConsent(payload);
    }

    throw createApiError(response, payload);
  }

  return payload;
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
  postForm: async (path, formData, options = {}) => {
    const { headers = {}, ...restOptions } = options;

    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      body: formData,
      // Do not set Content-Type for FormData; browser will set the correct boundary.
      ...restOptions,
      headers: buildFormHeaders(headers),
    });

    const payload = await parseResponse(response);

    if (!response.ok) {
      if (response.status === 403 && payload?.detail === "pending_consent") {
        notifyPendingConsent(payload);
      }

      throw createApiError(response, payload);
    }

    return payload;
  },
};