import { getAdminSessionToken } from "./adminSession";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const buildAuthHeaders = () => {
  const adminToken = getAdminSessionToken();

  if (!adminToken) return {};

  return {
    Authorization: `Bearer ${adminToken}`,
  };
};

async function request(path, options = {}) {
  const { headers: requestHeaders, ...requestOptions } = options;

  const response = await fetch(`${API_BASE_URL}${path}`, {
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
    const error = new Error(`Erro na API: ${response.status}`);
    error.status = response.status;
    error.data = responseBody;
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

  postForm: async (path, formData, options = {}) => {
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
      throw error;
    }

    return responseBody;
  },
};