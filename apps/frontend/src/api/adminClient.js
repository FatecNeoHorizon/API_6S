import { waitForPendingConsentAcceptance } from "./pendingConsentInterceptor";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const SESSION_KEYS = [
  "session_uuid",
  "sessionUuid",
  "access_token",
  "accessToken",
  "token",
];

const getSessionToken = () => {
  if (!globalThis.window) {
    return null;
  }

  for (const key of SESSION_KEYS) {
    const sessionValue = sessionStorage.getItem(key);
    const localValue = localStorage.getItem(key);

    if (sessionValue) return sessionValue;
    if (localValue) return localValue;
  }

  return null;
};

const buildAuthHeaders = () => {
  const adminToken = getSessionToken();

  if (!adminToken) return {};

  return {
    Authorization: `Bearer ${adminToken}`,
  };
};

async function request(path, options = {}, retryAfterConsent = true) {
  const { headers: requestHeaders, ...requestOptions } = options;

  const url = `${API_BASE_URL}${path}`;

  try {
    const response = await fetch(url, {
      ...requestOptions,
      headers: {
        "Content-Type": "application/json",
        ...buildAuthHeaders(),
        ...requestHeaders,
      },
    });

    const contentType = response.headers.get("content-type");
    const responseBody = contentType?.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      console.warn("adminClient: resposta não-ok", { url, status: response.status, body: responseBody });
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
  } catch (fetchError) {
    // Erros de rede / CORS / extension failures podem chegar aqui
    console.error("adminClient: falha na requisição", { url, options: requestOptions, error: fetchError });
    throw fetchError;
  }
}

async function postFormRequest(path, formData, options = {}, retryAfterConsent = true) {
  const { headers: requestHeaders, ...requestOptions } = options;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...requestOptions,
    method: "POST",
    headers: {
      ...buildAuthHeaders(),
      ...requestHeaders,
    },
    body: formData,
  });

  const contentType = response.headers.get("content-type");
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
        return postFormRequest(path, formData, options, false);
      }
    }

    throw error;
  }

  return responseBody;
}

export const adminClient = {
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

  postForm: (path, formData, options = {}) => postFormRequest(path, formData, options),
};