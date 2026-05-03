import { waitForPendingConsentAcceptance } from "./pendingConsentInterceptor";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}, retryAfterConsent = true) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options?.method ?? "GET",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  const contentType = response.headers.get("content-type")
  const responseBody = contentType?.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const error = new Error(`Erro na API: ${response.status}`);
    error.status = response.status;
    error.data = responseBody;

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

async function postFormRequest(path, formData, options = {}, retryAfterConsent = true) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    body: formData,
    // Do not set Content-Type for FormData; browser will set the correct boundary
    ...options,
  });

  if (!response.ok) {
    const contentType = response.headers.get("content-type");
    const responseBody = contentType?.includes("application/json")
      ? await response.json()
      : await response.text();

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

  const contentType = response.headers.get("content-type");

  if (contentType?.includes("application/json")) {
    return response.json();
  }

  return response.text();
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