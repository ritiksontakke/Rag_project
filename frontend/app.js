/* =========================================================
   Multi Model RAG — frontend client
   Talks to the FastAPI backend
   ========================================================= */

const API_BASE =
  localStorage.getItem("rag_api_base") ||
  "https://multi-model-rag-3rt6.onrender.com/api/v1";

// const API_BASE =
//   "http://127.0.0.1:8000/api/v1"; 

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
    const payload = token
      .split(".")[1]
      .replace(/-/g, "+")
      .replace(/_/g, "/");

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

  if (Array.isArray(d)) {
    return d.map((x) => x.msg || JSON.stringify(x)).join(", ");
  }

  return JSON.stringify(d);
}

/* =========================================================
   AUTH
   ========================================================= */

let AUTH_TOKEN = null;
let CURRENT_USER_KEY = null;
let CURRENT_USER_SCOPE = null;
let PENDING_LOGIN = null;

function token() {
  return AUTH_TOKEN;
}

/*
 * Remove old shared history/token data from previous versions.
 *
 * IMPORTANT:
 * We intentionally DO NOT remove:
 * rag_chats:<user-specific-key>
 *
 * because those belong to individual users.
 */
try {
  localStorage.removeItem("rag_token");
  sessionStorage.removeItem("rag_token");

  // Old shared chat store.
  localStorage.removeItem("rag_chats");
} catch {}

/* ---------------- textarea ---------------- */

function autoGrowQuery() {
  const ta = $("query");

  if (!ta) return;

  ta.style.height = "auto";

  const max = 200;
  const next = Math.min(ta.scrollHeight, max);

  ta.style.height = Math.max(next, 48) + "px";
  ta.style.overflowY = ta.scrollHeight > max ? "auto" : "hidden";
}

/* ---------------- html escape ---------------- */

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
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

  if (PENDING_LOGIN) {
    const creds = PENDING_LOGIN;

    PENDING_LOGIN = null;

    $("login-email").value = creds.email;
    $("login-password").value = creds.password;

    return signIn(creds.email, creds.password);
  }

  const el = $("login-password");

  if (el) el.focus();
}

/* =========================================================
   AUTH SCREEN
   ========================================================= */

function showTab(which) {
  const login = which === "login";

  $("tab-login").classList.toggle("active", login);
  $("tab-signup").classList.toggle("active", !login);

  $("login-form").classList.toggle("hidden", !login);
  $("signup-form").classList.toggle("hidden", login);

  $("auth-heading").textContent =
    login ? "Welcome back" : "Create your account";

  $("auth-lead").textContent = login
    ? "Sign in to continue to your knowledge base."
    : "Register with your work email and department.";

  setMsg($("auth-msg"), "");
}

/* ---------------- signup ---------------- */

async function doSignup(e) {
  e.preventDefault();

  const msg = $("auth-msg");

  const body = {
    full_name: $("su-name").value.trim(),
    email: $("su-email").value.trim().toLowerCase(),
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
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      return setMsg(msg, errText(data, "Signup failed."));
    }

    const email = body.email;
    const password = body.password;

    PENDING_LOGIN = {
      email,
      password,
    };

    $("signup-form").reset();

    showTab("login");

    $("login-email").value = email;
    $("login-password").value = "";

    setMsg(msg, "");

    showSuccess(
      "Account created successfully",
      `Welcome ${escapeHtml(body.full_name)}! Your account is ready. Please log in to continue.`
    );
  } catch {
    setMsg(msg, "Cannot reach the API. Is the backend running?");
  }
}

/* ---------------- login ---------------- */

async function doLogin(e) {
  e.preventDefault();

  PENDING_LOGIN = null;

  return signIn(
    $("login-email").value.trim().toLowerCase(),
    $("login-password").value
  );
}

async function signIn(email, password) {
  const msg = $("auth-msg");

  setMsg(msg, "Signing in...", true);

  const form = new URLSearchParams();

  form.set("username", email);
  form.set("password", password);

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: form.toString(),
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      return setMsg(msg, errText(data, "Login failed."));
    }

    AUTH_TOKEN = data.access_token;

    $("login-password").value = "";

    setMsg(msg, "");

    enterApp();
  } catch {
    setMsg(msg, "Cannot reach the API. Is the backend running?");
  }
}

/* =========================================================
   LOGOUT
   ========================================================= */

// function logout() {
//   AUTH_TOKEN = null;

//   CURRENT_USER_KEY = null;
//   CURRENT_USER_SCOPE = null;

//   PENDING_LOGIN = null;

//   $("chat-list").innerHTML = "";
//   $("messages").innerHTML = "";

//   $("login-password").value = "";

//   $("app-screen").classList.add("hidden");
//   $("auth-screen").classList.remove("hidden");
// }

function logout() {

  // -----------------------------
  // Auth/session clear
  // -----------------------------

  AUTH_TOKEN = null;
  CURRENT_USER_KEY = null;
  CURRENT_USER_SCOPE = null;
  PENDING_LOGIN = null;

  // -----------------------------
  // Thread clear
  // -----------------------------

  THREAD_ID = null;

  // -----------------------------
  // Chat state clear
  // -----------------------------

  chatHistory = [];

  // -----------------------------
  // Clear browser storage
  // -----------------------------

  localStorage.clear();
  sessionStorage.clear();

  // -----------------------------
  // Clear UI
  // -----------------------------

  $("chat-list").innerHTML = "";
  $("messages").innerHTML = "";

  $("login-password").value = "";

  // -----------------------------
  // Return to login
  // -----------------------------

  $("app-screen").classList.add("hidden");
  $("auth-screen").classList.remove("hidden");
}

/* =========================================================
   APP SCREEN
   ========================================================= */

function enterApp() {
  const claims = decodeJwt(token());

  if (!claims) {
    return logout();
  }

  const name = claims.full_name || claims.email || "User";

  const role = (claims.role || "employee").toLowerCase();

  const dept = claims.department || "—";

  const email = String(
    claims.email || ""
  )
    .trim()
    .toLowerCase();

  const userId = String(
    claims.id || claims.sub || ""
  ).trim();

  /*
   * =======================================================
   * IMPORTANT HISTORY ISOLATION
   * =======================================================
   *
   * Every authenticated user gets a completely different
   * localStorage key.
   *
   * Example:
   *
   * User A:
   * rag_chats:v2:123:usera@gmail.com:hr
   *
   * User B:
   * rag_chats:v2:456:userb@gmail.com:it
   *
   * Therefore User A cannot display User B's chats.
   */

  CURRENT_USER_SCOPE = [
    "v2",
    userId || "no-id",
    email || "no-email",
    String(dept).trim().toLowerCase() || "no-dept",
  ]
    .map(encodeURIComponent)
    .join(":");

  CURRENT_USER_KEY = CURRENT_USER_SCOPE;

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

  const perms =
    ROLE_TOOLS[role] || ROLE_TOOLS.employee;

  $("perm-list").innerHTML = perms
    .map((p) => `<li>${p.replace(/_/g, " ")}</li>`)
    .join("");

  const canUpload = perms.includes("upload_document");

  $("upload-section").classList.toggle(
    "hidden",
    !canUpload
  );

  $("up-dept").value = dept;
  $("up-dept-label").textContent = dept;

  $("auth-screen").classList.add("hidden");
  $("app-screen").classList.remove("hidden");

  /*
   * IMPORTANT:
   * Render only AFTER CURRENT_USER_SCOPE has been created.
   */
  renderAll();
}

/* =========================================================
   CHAT SESSIONS
   ========================================================= */

/*
 * Store format:
 *
 * {
 *   ownerScope: "...",
 *   chats: [...],
 *   activeId: "..."
 * }
 */

/*
 * NEVER use:
 *
 * rag_chats
 * rag_chats:anon
 *
 * Those would be shared between users.
 */

function storeKey() {
  if (!CURRENT_USER_KEY) {
    return null;
  }

  return "rag_chats:" + CURRENT_USER_KEY;
}

function newId() {
  return (
    "c" +
    Date.now().toString(36) +
    Math.random().toString(36).slice(2, 6)
  );
}

function blankStore() {
  const id = newId();

  return {
    ownerScope: CURRENT_USER_SCOPE,

    chats: [
      {
        id,
        title: "New chat",
        messages: [],
      },
    ],

    activeId: id,
  };
}

/* =========================================================
   LOAD STORE
   ========================================================= */

function loadStore() {
  const key = storeKey();

  /*
   * No authenticated user:      content:
        `Document "${file.name}" ingested for ${dept}.\n\n${
          (data.data &&
            data.data.result) ||
          ""
        }
   * do not access localStorage history.
   */
  if (!key) {
    return blankStore();
  }

  let store;

  try {
    store = JSON.parse(
      localStorage.getItem(key) || "null"
    );
  } catch {
    store = null;
  }

  /*
   * If store doesn't belong to current user,
   * create a completely fresh store.
   */
  if (
    !store ||
    store.ownerScope !== CURRENT_USER_SCOPE ||
    !Array.isArray(store.chats) ||
    !store.chats.length
  ) {
    store = {
      ...blankStore(),
      ownerScope: CURRENT_USER_SCOPE,
    };

    saveStore(store);
  }

  /*
   * Make sure active chat belongs to this store.
   */
  if (
    !store.chats.some(
      (c) => c.id === store.activeId
    )
  ) {
    store.activeId = store.chats[0].id;

    saveStore(store);
  }

  return store;
}

/* =========================================================
   SAVE STORE
   ========================================================= */

function saveStore(store) {
  const key = storeKey();

  /*
   * Never save without authenticated user.
   */
  if (!key) {
    return;
  }

  /*
   * Always attach current owner.
   */
  store.ownerScope = CURRENT_USER_SCOPE;

  localStorage.setItem(
    key,
    JSON.stringify(store)
  );
}

/* =========================================================
   ACTIVE CHAT
   ========================================================= */

function activeChat(store) {
  return store.chats.find(
    (c) => c.id === store.activeId
  );
}

/* =========================================================
   NEW CHAT
   ========================================================= */

function newChat() {
  if (!CURRENT_USER_SCOPE) {
    return;
  }

  const store = loadStore();

  const chat = {
    id: newId(),
    title: "New chat",
    messages: [],
  };

  store.chats.unshift(chat);

  store.activeId = chat.id;

  saveStore(store);

  renderAll();
}

/* =========================================================
   SELECT CHAT
   ========================================================= */

function selectChat(id) {
  if (!CURRENT_USER_SCOPE) {
    return;
  }

  const store = loadStore();

  /*
   * Only select a chat that exists inside
   * current user's own store.
   */
  const exists = store.chats.some(
    (c) => c.id === id
  );

  if (!exists) {
    return;
  }

  store.activeId = id;

  saveStore(store);

  renderAll();
}

/* =========================================================
   DELETE CHAT
   ========================================================= */

function deleteChat(id, ev) {
  if (ev) {
    ev.stopPropagation();
  }

  if (!CURRENT_USER_SCOPE) {
    return;
  }

  const store = loadStore();

  store.chats = store.chats.filter(
    (c) => c.id !== id
  );

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

/* =========================================================
   RENAME CHAT
   ========================================================= */

function renameChat() {
  if (!CURRENT_USER_SCOPE) {
    return;
  }

  const store = loadStore();

  const chat = activeChat(store);

  if (!chat) {
    return;
  }

  const name = prompt(
    "Chat name",
    chat.title
  );

  if (name && name.trim()) {
    chat.title = name
      .trim()
      .slice(0, 40);

    saveStore(store);

    renderAll();
  }
}

/* =========================================================
   CLEAR CHAT
   ========================================================= */

function clearChat() {
  if (!CURRENT_USER_SCOPE) {
    return;
  }

  const store = loadStore();

  const chat = activeChat(store);

  if (!chat) {
    return;
  }

  chat.messages = [];

  saveStore(store);

  renderAll();
}

/* =========================================================
   PUSH MESSAGE
   ========================================================= */

function pushMsg(m) {
  if (!CURRENT_USER_SCOPE) {
    return;
  }

  const store = loadStore();

  const chat = activeChat(store);

  if (!chat) {
    return;
  }

  chat.messages.push(m);

  chat.messages =
    chat.messages.slice(-60);

  if (
    chat.title === "New chat" &&
    m.role === "user"
  ) {
    chat.title =
      m.content.slice(0, 38);
  }

  saveStore(store);

  renderAll();
}

/* =========================================================
   RENDER ALL
   ========================================================= */

function renderAll() {
  /*
   * If nobody is authenticated,
   * absolutely nothing from chat history
   * should be rendered.
   */
  if (!CURRENT_USER_SCOPE) {
    $("chat-list").innerHTML = "";
    $("messages").innerHTML = "";
    $("chat-title").textContent = "";

    return;
  }

  const store = loadStore();

  renderChatList(store);

  renderMessages(store);
}

/* =========================================================
   RENDER CHAT LIST
   ========================================================= */

function renderChatList(store) {
  /*
   * Extra owner check.
   */
  if (
    !store ||
    store.ownerScope !== CURRENT_USER_SCOPE
  ) {
    $("chat-list").innerHTML = "";
    return;
  }

  $("chat-list").innerHTML =
    store.chats
      .map(
        (c) => `
          <li
            class="${
              c.id === store.activeId
                ? "active"
                : ""
            }"
            onclick="selectChat('${c.id}')"
          >
            <span class="name">
              ${escapeHtml(c.title)}
            </span>

            <button
              class="del"
              title="Delete"
              onclick="deleteChat('${c.id}', event)"
            >
              ×
            </button>
          </li>
        `
      )
      .join("");

  const chat = activeChat(store);

  if (chat) {
    $("chat-title").textContent =
      chat.title;
  }
}

/* =========================================================
   RENDER MESSAGES
   ========================================================= */

function renderMessages(store) {
  const box = $("messages");

  /*
   * Extra owner protection.
   */
  if (
    !store ||
    store.ownerScope !== CURRENT_USER_SCOPE
  ) {
    box.innerHTML = "";
    return;
  }

  const chat = activeChat(store);

  if (!chat) {
    box.innerHTML = "";
    return;
  }

  const items = chat.messages;

  if (!items.length) {
    box.innerHTML =
      '<p class="empty">No messages yet. Ask something about your department documents.</p>';

    return;
  }

  box.innerHTML = items
    .map((m) => {
      const cls =
        m.role === "user"
          ? "user"
          : m.error
          ? "bot err"
          : "bot";

      const meta = m.department
        ? `<span class="meta">${escapeHtml(
            m.department
          )}</span>`
        : "";

      return `
        <div class="bubble ${cls}">
          ${escapeHtml(m.content)}
          ${meta}
        </div>
      `;
    })
    .join("");

  requestAnimationFrame(() => {
    box.scrollTo({
      top: box.scrollHeight,
      behavior: "auto",
    });
  });
}

/* =========================================================
   ASK
   ========================================================= */

async function doAsk(e) {
  e.preventDefault();

  /*
   * Never allow API/chat actions without user scope.
   */
  if (!CURRENT_USER_SCOPE) {
    return;
  }

  const input = $("query");

  const query = input.value.trim();

  if (!query) {
    return;
  }

  input.value = "";

  autoGrowQuery();

  pushMsg({
    role: "user",
    content: query,
  });

  const btn = $("send-btn");

  btn.disabled = true;

  pushMsg({
    role: "assistant",
    content: "Thinking...",
  });

  const replaceLast = (m) => {
    const store = loadStore();

    /*
     * Safety check again.
     */
    if (
      store.ownerScope !==
      CURRENT_USER_SCOPE
    ) {
      return;
    }

    const chat = activeChat(store);

    if (!chat) {
      return;
    }

    chat.messages.pop();

    if (m) {
      chat.messages.push(m);
    }

    saveStore(store);

    renderAll();
  };

  try {
    const res = await fetch(
      `${API_BASE}/knowledge/ask`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json",

          Authorization:
            `Bearer ${token()}`,
        },

        body: JSON.stringify({
          query: query,
        }),
      }
    );

    const data =
      await res.json().catch(
        () => ({})
      );

    if (res.status === 401) {
      replaceLast(null);

      return logout();
    }

    if (!res.ok) {
      replaceLast({
        role: "assistant",

        content: errText(
          data,
          "Request failed."
        ),

        error: true,
      });
    } else {
      replaceLast({
        role: "assistant",

        content:
          data.answer ||
          "(empty answer)",

        department:
          data.department,
      });
    }
  } catch {
    replaceLast({
      role: "assistant",

      content:
        "Cannot reach the API. Is the backend running?",

      error: true,
    });
  } finally {
    btn.disabled = false;
  }
}

/* =========================================================
   UPLOAD
   ========================================================= */

async function doUpload(e) {
  e.preventDefault();

  if (!CURRENT_USER_SCOPE) {
    return;
  }

  const msg = $("upload-msg");

  const file =
    $("up-file").files[0];

  const dept =
    $("up-dept").value.trim();

  if (!file) {
    return setMsg(
      msg,
      "Choose a PDF file."
    );
  }

  if (!dept) {
    return setMsg(
      msg,
      "Department is required."
    );
  }

  setMsg(
    msg,
    "Uploading and ingesting...",
    true
  );

  const form =
    new FormData();

  form.append(
    "department",
    dept
  );

  form.append(
    "file",
    file
  );

  try {
    const res = await fetch(
      `${API_BASE}/documents/upload`,
      {
        method: "POST",

        headers: {
          Authorization:
            `Bearer ${token()}`,
        },

        body: form,
      }
    );

    const data =
      await res.json().catch(
        () => ({})
      );

    if (res.status === 401) {
      return logout();
    }

    if (!res.ok) {
      return setMsg(
        msg,
        errText(
          data,
          "Upload failed."
        )
      );
    }

    setMsg(
      msg,
      "Uploaded successfully.",
      true
    );

    $("up-file").value = "";

    pushMsg({
      role: "assistant",
      content: "Your document uploaded successfully.",
      department: dept,
    });
  } catch {
    setMsg(
      msg,
      "Cannot reach the API."
    );
  }
}

/* =========================================================
   BOOT
   ========================================================= */

document.addEventListener(
  "DOMContentLoaded",
  () => {
    $("api-url").textContent =
      API_BASE;

    /*
     * No persisted session.
     * Every page refresh starts from login.
     */
    logout();

    const ta = $("query");

    ta.addEventListener(
      "input",
      autoGrowQuery
    );

    autoGrowQuery();

    ta.addEventListener(
      "keydown",
      (ev) => {
        if (
          ev.key === "Enter" &&
          !ev.shiftKey
        ) {
          ev.preventDefault();

          ta.form.requestSubmit();
        }
      }
    );
  }
);