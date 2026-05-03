const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    throw new Error(`Erro na API: ${response.status}`);
  }

  const contentType = response.headers.get("content-type");

  if (contentType && contentType.includes("application/json")) {
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
  postForm: async (path, formData, options = {}) => {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      body: formData,
      // Do not set Content-Type for FormData; browser will set the correct boundary
      ...(options || {}),
    });

    if (!response.ok) {
      throw new Error(`Erro na API: ${response.status}`);
    }

    const contentType = response.headers.get("content-type");

    if (contentType && contentType.includes("application/json")) {
      return response.json();
    }

    return response.text();
  },
};