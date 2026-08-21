# Multi Model RAG — Frontend

Plain HTML + CSS + JavaScript, served by a small Python static server.
No build step, no npm.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | Auth screen (login / signup) + chat app with left sidebar |
| `style.css` | Dark design system (tokens, sidebar, chat bubbles) |
| `app.js` | API client: signup, login, JWT decode, chat, PDF upload |
| `serve.py` | `python frontend/serve.py` → http://127.0.0.1:5500 |

## Run locally

1. Start the backend from the project root:

```bash
uvicorn src.main:app --reload --port 8000
```

2. Start the frontend:

```bash
python frontend/serve.py
```

3. Open http://127.0.0.1:5500

## REQUIRED: enable CORS on the backend

The browser calls the API from a different port, so add this to `src/main.py`
right after `app = FastAPI(...)`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## What the UI does

- **Create account** → `POST /api/v1/auth/signup` (full_name, email, department, password, confirm_password)
- **Login** → `POST /api/v1/auth/login` (form-encoded `username`/`password`), stores the bearer token
- **Sidebar** shows full name, email, role, department, user id, and the tool
  permissions for that role (mirrors `src/access_control/permission.py`)
- **Chat** → `POST /api/v1/knowledge/ask` with `Authorization: Bearer <token>`;
  renders `answer` and tags each reply with the department
- **Upload PDF** (admin/manager only, hidden for employees) →
  `POST /api/v1/documents/upload` multipart with `department` + `file`
- 401 responses log the user out automatically; chat history is kept in
  `localStorage`

## Changing the API URL

Run this once in the browser console:

```js
localStorage.setItem("rag_api_base", "http://127.0.0.1:8000/api/v1");
```
