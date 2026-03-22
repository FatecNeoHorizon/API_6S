# API CALL PATTERN IN THE FRONTEND

## 1. Overview

In this project, API calls follow a layered architecture:

Page → Service → Client → Backend

### How it works:

- **Page (UI)**: handles interface and user interaction.
- **Service (domain)**: contains business-specific functions (e.g., login, fetch users).
- **Client (HTTP)**: centralizes all HTTP calls.
- **Backend**: API that responds to requests.

This pattern avoids direct `fetch()` usage in pages, improving organization and scalability.

---

## 2. Why use this pattern?

- Centralizes API communication  
- Avoids duplicated code  
- Simplifies maintenance  
- Enables easy authentication integration  
- Standardizes error handling  
- Prepares the system for growth  

---

## 3. Structure

```
src/api/
├── client.js
├── auth.js
├── health.js
```

---

## 4. Client example

```js
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Error ${response.status}`);
  }

  return response.json();
}

export const apiClient = {
  get: (path) => request(path, { method: "GET" }),
  post: (path, body) =>
    request(path, {
      method: "POST",
      body: JSON.stringify(body),
    }),
};
```

---

## 5. Service example

```js
import { apiClient } from "./client";

export function login(payload) {
  return apiClient.post("/auth/login", payload);
}
```

---

## 6. Page usage example

```jsx
import { useState } from "react";
import { login } from "@/api/auth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleLogin() {
    try {
      const response = await login({ email, password });
      console.log("Login successful:", response);
    } catch (error) {
      console.error("Login error:", error);
    }
  }

  return (
    <div>
      <input value={email} onChange={(e) => setEmail(e.target.value)} />
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button onClick={handleLogin}>Login</button>
    </div>
  );
}
```
