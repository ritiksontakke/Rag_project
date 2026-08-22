/* =========================================================
   Multi Model RAG — frontend client
   Talks to the FastAPI backend (default http://127.0.0.1:8000)
   ========================================================= */

const API_BASE =
  localStorage.getItem("rag_api_base") || "https://multi-model-rag-3rt6.onrender.com/api/v1";

const ROLE_TOOLS = {
  employee: ["search_documents", "get_document", "list_documents"],
  manager: [
    "upload_document",
    "search_documents",
    "get_document",
    "list_documents",
    "update_document",
    "delete_document",
  ],
  admin: [
    "upload_document",
    "search_documents",
    "get_document",
    "list_documents",
    "update_document",
    "delete_document",
  ],
};

/* ---------------- helpers ---------------- */

const $ = (id) => document.getElementById(id);

function setMsg(el, text, ok = false) {
  el.textContent = text || "";
  el.classList.toggle("ok", ok);
}

function decodeJwt(token) {
  try {
    const payload = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(decodeURIComponent(escape(atob(payload))));
  } catch {
    return null;
  }
}

function errText(data, fallback) {
  const d = data && data.detail;
  if (!d) return fallback;
  if (typeof d === "string") return d;
  if (d.message) return d.message;
  if (Array.isArray(d)) return d.map((x) => x.msg || JSON.stringify(x)).join(", ");
  return JSON.stringify(d);
}

function token() {
  return localStorage.getItem("rag_token");
}

function autoGrowQuery() {
  const ta = $("query");
  if (!ta) return;
  ta.style.height = "auto";
  const max = 200;
  const next = Math.min(ta.scrollHeight, max);
  ta.style.height = Math.max(next, 48) + "px";
  ta.style.overflowY = ta.scrollHeight > max ? "auto" : "hidden";
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

/* ---------------- success popup ---------------- */

function showSuccess(title, text) {
  $("success-title").textContent = title;
  $("success-text").innerHTML = text;
  $("success-modal").classList.remove("hidden");
}

function closeSuccess() {
  $("success-modal").classList.add("hidden");
  const el = $("login-password");
  if (el) el.focus();
}

/* ---------------- auth screen ---------------- */

function showTab(which) {
  const login = which === "login";
  $("tab-login").classList.toggle("active", login);
  $("tab-signup").classList.toggle("active", !login);
  $("login-form").classList.toggle("hidden", !login);
  $("signup-form").classList.toggle("hidden", login);
  $("auth-heading").textContent = login ? "Welcome back" : "Create your account";
  $("auth-lead").textContent = login
    ? "Sign in to continue to your knowledge base."
    : "Register with your work email and department.";
  setMsg($("auth-msg"), "");
}

async function doSignup(e) {
  e.preventDefault();
  const msg = $("auth-msg");

  const body = {
    full_name: $("su-name").value.trim(),
    email: $("su-email").value.trim(),
    department: $("su-dept").value.trim(),
    password: $("su-password").value,
    confirm_password: $("su-confirm").value,
  };

  if (body.password !== body.confirm_password) {
    return setMsg(msg, "Passwords do not match.");
  }

  setMsg(msg, "Creating account...", true);

  try {
    const res = await fetch(`${API_BASE}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));

    if (!res.ok) return setMsg(msg, errText(data, "Signup failed."));

    const email = body.email;
    $("signup-form").reset();
    showTab("login");
    $("login-email").value = email;
    setMsg(msg, "");
    showSuccess(
      "Account created successfully",
      `Welcome ${escapeHtml(body.full_name)}! Your account is ready. Please log in to continue.`
    );
  } catch {
    setMsg(msg, "Cannot reach the API. Is the backend running?");
  }
}

async function doLogin(e) {
  e.preventDefault();
  const msg = $("auth-msg");
  setMsg(msg, "Signing in...", true);

  // backend uses OAuth2PasswordRequestForm -> form encoded
  const form = new URLSearchParams();
  form.set("username", $("login-email").value.trim());
  form.set("password", $("login-password").value);

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    });
    const data = await res.json().catch(() => ({}));

    if (!res.ok) return setMsg(msg, errText(data, "Login failed."));

    localStorage.setItem("rag_token", data.access_token);
    setMsg(msg, "");
    enterApp();
  } catch {
    setMsg(msg, "Cannot reach the API. Is the backend running?");
  }
}

function logout() {
  localStorage.removeItem("rag_token");
  $("app-screen").classList.add("hidden");
  $("auth-screen").classList.remove("hidden");
}

/* ---------------- app screen ---------------- */

function enterApp() {
  const claims = decodeJwt(token());
  if (!claims) return logout();

  const name = claims.full_name || claims.email || "User";
  const role = (claims.role || "employee").toLowerCase();
  const dept = claims.department || "—";

  $("u-name").textContent = name;
  $("u-email").textContent = claims.email || "—";
  $("u-role").textContent = role;
  $("u-dept").textContent = dept;
  $("u-id").textContent = claims.id || claims.sub || "—";
  $("avatar").textContent = name
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const perms = ROLE_TOOLS[role] || ROLE_TOOLS.employee;
  $("perm-list").innerHTML = perms
    .map((p) => `<li>${p.replace(/_/g, " ")}</li>`)
    .join("");

  const canUpload = perms.includes("upload_document");
  $("upload-section").classList.toggle("hidden", !canUpload);
  $("up-dept").value = dept;
  $("up-dept-label").textContent = dept;


  $("auth-screen").classList.add("hidden");
  $("app-screen").classList.remove("hidden");

  renderAll();
}

/* ---------------- chat sessions ---------------- */
/* store: { chats: [{ id, title, messages: [] }], activeId } */

const STORE_KEY = "rag_chats";

function newId() {
  return "c" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
}

function blankStore() {
  const id = newId();
  return { chats: [{ id, title: "New chat", messages: [] }], activeId: id };
}

function loadStore() {
  let store;
  try {
    store = JSON.parse(localStorage.getItem(STORE_KEY) || "null");
  } catch {
    store = null;
  }
  if (!store || !Array.isArray(store.chats) || !store.chats.length) {
    store = blankStore();
    saveStore(store);
  }
  if (!store.chats.some((c) => c.id === store.activeId)) {
    store.activeId = store.chats[0].id;
  }
  return store;
}

function saveStore(store) {
  localStorage.setItem(STORE_KEY, JSON.stringify(store));
}

function activeChat(store) {
  return store.chats.find((c) => c.id === store.activeId);
}

function newChat() {
  const store = loadStore();
  const chat = { id: newId(), title: "New chat", messages: [] };
  store.chats.unshift(chat);
  store.activeId = chat.id;
  saveStore(store);
  renderAll();
}

function selectChat(id) {
  const store = loadStore();
  store.activeId = id;
  saveStore(store);
  renderAll();
}

function deleteChat(id, ev) {
  if (ev) ev.stopPropagation();
  const store = loadStore();
  store.chats = store.chats.filter((c) => c.id !== id);
  if (!store.chats.length) {
    const fresh = blankStore();
    store.chats = fresh.chats;
    store.activeId = fresh.activeId;
  } else if (store.activeId === id) {
    store.activeId = store.chats[0].id;
  }
  saveStore(store);
  renderAll();
}

function renameChat() {
  const store = loadStore();
  const chat = activeChat(store);
  const name = prompt("Chat name", chat.title);
  if (name && name.trim()) {
    chat.title = name.trim().slice(0, 40);
    saveStore(store);
    renderAll();
  }
}

function clearChat() {
  const store = loadStore();
  activeChat(store).messages = [];
  saveStore(store);
  renderAll();
}

function pushMsg(m) {
  const store = loadStore();
  const chat = activeChat(store);
  chat.messages.push(m);
  chat.messages = chat.messages.slice(-60);
  if (chat.title === "New chat" && m.role === "user") {
    chat.title = m.content.slice(0, 38);
  }
  saveStore(store);
  renderAll();
}

function renderAll() {
  const store = loadStore();
  renderChatList(store);
  renderMessages(store);
}

function renderChatList(store) {
  $("chat-list").innerHTML = store.chats
    .map(
      (c) => `<li class="${c.id === store.activeId ? "active" : ""}" onclick="selectChat('${c.id}')">
        <span class="name">${escapeHtml(c.title)}</span>
        <button class="del" title="Delete" onclick="deleteChat('${c.id}', event)">×</button>
      </li>`
    )
    .join("");
  const chat = activeChat(store);
  $("chat-title").textContent = chat.title;
}

function renderMessages(store) {
  const box = $("messages");
  const items = activeChat(store).messages;

  if (!items.length) {
    box.innerHTML =
      '<p class="empty">No messages yet. Ask something about your department documents.</p>';
    return;
  }

  box.innerHTML = items
    .map((m) => {
      const cls = m.role === "user" ? "user" : m.error ? "bot err" : "bot";
      const meta = m.department ? `<span class="meta">${escapeHtml(m.department)}</span>` : "";
      return `<div class="bubble ${cls}">${escapeHtml(m.content)}${meta}</div>`;
    })
    .join("");

  requestAnimationFrame(() => {
    box.scrollTo({ top: box.scrollHeight, behavior: "auto" });
  });
}

async function doAsk(e) {
  e.preventDefault();
  const input = $("query");
  const query = input.value.trim();
  if (!query) return;

  input.value = "";
  autoGrowQuery();
  pushMsg({ role: "user", content: query });

  const btn = $("send-btn");
  btn.disabled = true;
  pushMsg({ role: "assistant", content: "Thinking..." });

  const replaceLast = (m) => {
    const store = loadStore();
    const chat = activeChat(store);
    chat.messages.pop();
    if (m) chat.messages.push(m);
    saveStore(store);
    renderAll();
  };

  try {
    const res = await fetch(`${API_BASE}/knowledge/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
      body: JSON.stringify({ query }),
    });
    const data = await res.json().catch(() => ({}));

    if (res.status === 401) {
      replaceLast(null);
      return logout();
    }

    if (!res.ok) {
      replaceLast({
        role: "assistant",
        content: errText(data, "Request failed."),
        error: true,
      });
    } else {
      replaceLast({
        role: "assistant",
        content: data.answer || "(empty answer)",
        department: data.department,
      });
    }
  } catch {
    replaceLast({
      role: "assistant",
      content: "Cannot reach the API. Is the backend running?",
      error: true,
    });
  } finally {
    btn.disabled = false;
  }
}

/* ---------------- upload ---------------- */

async function doUpload(e) {
  e.preventDefault();
  const msg = $("upload-msg");
  const file = $("up-file").files[0];
  const dept = $("up-dept").value.trim();

  if (!file) return setMsg(msg, "Choose a PDF file.");
  if (!dept) return setMsg(msg, "Department is required.");

  setMsg(msg, "Uploading and ingesting...", true);

  const form = new FormData();
  form.append("department", dept);
  form.append("file", file);

  try {
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token()}` },
      body: form,
    });
    const data = await res.json().catch(() => ({}));

    if (res.status === 401) return logout();
    if (!res.ok) return setMsg(msg, errText(data, "Upload failed."));

    setMsg(msg, "Uploaded successfully.", true);
    $("up-file").value = "";
    pushMsg({
      role: "assistant",
      content: `Document "${file.name}" ingested for ${dept}.\n\n${
        (data.data && data.data.result) || ""
      }`,
      department: dept,
    });
  } catch {
    setMsg(msg, "Cannot reach the API.");
  }
}

/* ---------------- boot ---------------- */

document.addEventListener("DOMContentLoaded", () => {
  $("api-url").textContent = API_BASE;

  const t = token();
  const claims = t ? decodeJwt(t) : null;
  const expired = claims && claims.exp && claims.exp * 1000 < Date.now();

  if (claims && !expired) enterApp();
  else if (t) logout();

  const ta = $("query");
  ta.addEventListener("input", autoGrowQuery);
  autoGrowQuery();
  ta.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" && !ev.shiftKey) {
      ev.preventDefault();
      ta.form.requestSubmit();
    }
  });
});
