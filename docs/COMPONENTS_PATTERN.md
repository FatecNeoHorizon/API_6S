# REUSABLE COMPONENTS AND COMPONENT COMMUNICATION

## 1. Overview

The project uses reusable components organized in layers:

Page → Components → UI

### How it works:

- **Page**: orchestrates data and layout
- **Common components**: reusable building blocks
- **UI components**: base elements (Button, Input, Card)

---

## 2. Why use reusable components?

- Avoids duplication  
- Ensures visual consistency  
- Simplifies maintenance  
- Enables scalable UI composition  

---

## 3. Structure

```
src/components/
├── ui/
├── common/
```

---

## 4. Component communication

### Parent → Child (props)

```jsx
function Child({ title }) {
  return <h1>{title}</h1>;
}

function Parent() {
  return <Child title="Title from parent" />;
}
```

---

### Child → Parent (callback)

```jsx
function Child({ onSend }) {
  return <button onClick={() => onSend("value")}>Send</button>;
}

function Parent() {
  function handleReceive(value) {
    console.log(value);
  }

  return <Child onSend={handleReceive} />;
}
```

---

## 5. Page example

```jsx
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function LoginPage() {
  const [email, setEmail] = useState("");

  return (
    <div>
      <Input value={email} onChange={(e) => setEmail(e.target.value)} />
      <Button>Submit</Button>
    </div>
  );
}
```
