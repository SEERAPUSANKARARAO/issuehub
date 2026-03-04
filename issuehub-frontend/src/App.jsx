import { useState, useEffect, createContext, useContext, useCallback } from "react";

// ─── CONFIG ───────────────────────────────────────────────────────────────────
const API_BASE = "http://localhost:8000/api";

// ─── AUTH CONTEXT ─────────────────────────────────────────────────────────────
const AuthContext = createContext(null);
const useAuth = () => useContext(AuthContext);

// ─── API HELPER ───────────────────────────────────────────────────────────────
const api = async (path, method = "GET", body = null, token = null) => {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || data?.error?.message || "Request failed");
  return data;
};

// ─── STYLES ───────────────────────────────────────────────────────────────────
const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0a0a0f; --surface: #111118; --surface2: #1a1a24; --border: #2a2a3a;
    --accent: #6c63ff; --accent3: #43e97b; --text: #e8e8f0; --muted: #6b6b80;
    --danger: #ff4d6d; --warn: #ffb347; --radius: 12px;
    --font: 'Syne', sans-serif; --mono: 'DM Mono', monospace;
  }
  body { background: var(--bg); color: var(--text); font-family: var(--font); min-height: 100vh; }
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

  .app { display: flex; min-height: 100vh; }
  .sidebar {
    width: 240px; min-height: 100vh; background: var(--surface);
    border-right: 1px solid var(--border); display: flex; flex-direction: column;
    padding: 24px 0; position: fixed; top: 0; left: 0; z-index: 100;
  }
  .main { margin-left: 240px; flex: 1; min-height: 100vh; }
  .content { padding: 32px; max-width: 1100px; }

  .logo { padding: 0 20px 28px; border-bottom: 1px solid var(--border); margin-bottom: 16px; display: flex; align-items: center; gap: 10px; }
  .logo-icon { width: 36px; height: 36px; background: var(--accent); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 800; color: #fff; }
  .logo-text { font-size: 18px; font-weight: 800; letter-spacing: -0.5px; }

  .nav-section { padding: 0 12px; margin-bottom: 8px; }
  .nav-label { font-size: 10px; font-weight: 700; letter-spacing: 2px; color: var(--muted); text-transform: uppercase; padding: 0 8px; margin-bottom: 6px; }
  .nav-item { display: flex; align-items: center; gap: 10px; padding: 9px 12px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; color: var(--muted); transition: all 0.15s; border: none; background: none; width: 100%; text-align: left; }
  .nav-item:hover { background: var(--surface2); color: var(--text); }
  .nav-item.active { background: rgba(108,99,255,0.15); color: var(--accent); }
  .nav-item .icon { font-size: 16px; width: 20px; text-align: center; }

  .sidebar-bottom { margin-top: auto; padding: 16px 12px 0; border-top: 1px solid var(--border); }
  .user-chip { display: flex; align-items: center; gap: 10px; padding: 10px 12px; background: var(--surface2); border-radius: 10px; }
  .avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--accent); display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; color: #fff; flex-shrink: 0; }
  .user-info { flex: 1; min-width: 0; }
  .user-name { font-size: 12px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .user-role { font-size: 10px; color: var(--muted); font-family: var(--mono); }
  .logout-btn { background: none; border: none; color: var(--muted); cursor: pointer; font-size: 16px; padding: 4px; border-radius: 6px; transition: all 0.15s; }
  .logout-btn:hover { color: var(--danger); background: rgba(255,77,109,0.1); }

  .page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 28px; gap: 16px; }
  .page-title { font-size: 26px; font-weight: 800; letter-spacing: -0.5px; }
  .page-subtitle { font-size: 13px; color: var(--muted); margin-top: 3px; font-family: var(--mono); }

  .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }

  .projects-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
  .project-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; cursor: pointer; transition: all 0.2s; position: relative; overflow: hidden; }
  .project-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--accent); transform: scaleX(0); transition: transform 0.2s; transform-origin: left; }
  .project-card:hover { border-color: var(--accent); transform: translateY(-2px); }
  .project-card:hover::before { transform: scaleX(1); }
  .project-name { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
  .project-key { font-size: 10px; font-family: var(--mono); color: var(--accent); background: rgba(108,99,255,0.12); padding: 2px 7px; border-radius: 4px; display: inline-block; margin-bottom: 8px; }
  .project-desc { font-size: 12px; color: var(--muted); line-height: 1.5; font-family: var(--mono); }
  .project-id { font-size: 10px; color: var(--border); font-family: var(--mono); margin-top: 14px; letter-spacing: 1px; }

  .issue-row { display: flex; align-items: center; gap: 12px; padding: 14px 16px; border-bottom: 1px solid var(--border); cursor: pointer; transition: background 0.15s; }
  .issue-row:last-child { border-bottom: none; }
  .issue-row:hover { background: var(--surface2); }
  .issue-row.selected { background: rgba(108,99,255,0.08); }
  .issue-title { font-size: 13px; font-weight: 600; flex: 1; }
  .issue-meta { font-size: 11px; color: var(--muted); font-family: var(--mono); }

  .badge { display: inline-flex; align-items: center; padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; font-family: var(--mono); white-space: nowrap; }
  .badge-open { background: rgba(67,233,123,0.12); color: var(--accent3); border: 1px solid rgba(67,233,123,0.2); }
  .badge-in_progress { background: rgba(255,179,71,0.12); color: var(--warn); border: 1px solid rgba(255,179,71,0.2); }
  .badge-closed { background: rgba(107,107,128,0.15); color: var(--muted); border: 1px solid var(--border); }
  .badge-high { background: rgba(255,77,109,0.12); color: var(--danger); border: 1px solid rgba(255,77,109,0.2); }
  .badge-medium { background: rgba(255,179,71,0.12); color: var(--warn); border: 1px solid rgba(255,179,71,0.2); }
  .badge-low { background: rgba(67,233,123,0.12); color: var(--accent3); border: 1px solid rgba(67,233,123,0.2); }

  .btn { display: inline-flex; align-items: center; gap: 6px; padding: 9px 16px; border-radius: 8px; font-size: 13px; font-weight: 700; font-family: var(--font); cursor: pointer; border: none; transition: all 0.15s; white-space: nowrap; }
  .btn-primary { background: var(--accent); color: #fff; }
  .btn-primary:hover { background: #7c75ff; transform: translateY(-1px); }
  .btn-ghost { background: transparent; color: var(--muted); border: 1px solid var(--border); }
  .btn-ghost:hover { color: var(--text); border-color: var(--accent); }
  .btn-danger { background: rgba(255,77,109,0.12); color: var(--danger); border: 1px solid rgba(255,77,109,0.2); }
  .btn-danger:hover { background: rgba(255,77,109,0.2); }
  .btn-sm { padding: 5px 10px; font-size: 11px; }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

  .form-group { margin-bottom: 18px; }
  .form-label { display: block; font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: var(--muted); margin-bottom: 7px; }
  .form-input, .form-textarea, .form-select { width: 100%; background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; color: var(--text); font-size: 13px; font-family: var(--font); transition: border-color 0.15s; outline: none; appearance: none; }
  .form-input:focus, .form-textarea:focus, .form-select:focus { border-color: var(--accent); }
  .form-textarea { resize: vertical; min-height: 80px; line-height: 1.5; }
  .form-select option { background: var(--surface2); }
  .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .form-hint { font-size: 10px; color: var(--muted); font-family: var(--mono); margin-top: 4px; }

  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 20px; animation: fadeIn 0.15s ease; }
  .modal { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; width: 100%; max-width: 480px; max-height: 90vh; overflow-y: auto; animation: slideUp 0.2s ease; }
  .modal-header { padding: 20px 24px 16px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
  .modal-title { font-size: 16px; font-weight: 800; }
  .modal-close { background: none; border: none; color: var(--muted); cursor: pointer; font-size: 20px; padding: 2px 6px; border-radius: 6px; }
  .modal-close:hover { color: var(--text); background: var(--surface2); }
  .modal-body { padding: 20px 24px; }
  .modal-footer { padding: 16px 24px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 8px; }

  .auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: radial-gradient(ellipse at 30% 50%, rgba(108,99,255,0.08) 0%, transparent 60%), radial-gradient(ellipse at 70% 50%, rgba(255,101,132,0.05) 0%, transparent 60%), var(--bg); }
  .auth-box { width: 100%; max-width: 400px; padding: 20px; }
  .auth-card { background: var(--surface); border: 1px solid var(--border); border-radius: 20px; padding: 36px; }
  .auth-logo-icon { width: 52px; height: 52px; background: var(--accent); border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 800; color: #fff; margin: 0 auto 12px; }
  .auth-title { font-size: 22px; font-weight: 800; text-align: center; margin-bottom: 6px; }
  .auth-sub { font-size: 12px; color: var(--muted); text-align: center; margin-bottom: 28px; font-family: var(--mono); }
  .auth-switch { text-align: center; margin-top: 20px; font-size: 12px; color: var(--muted); }
  .auth-switch button { background: none; border: none; color: var(--accent); cursor: pointer; font-weight: 700; font-family: var(--font); }

  .filters { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-bottom: 20px; }
  .filter-select { background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 7px 12px; color: var(--text); font-size: 12px; font-family: var(--font); outline: none; cursor: pointer; transition: border-color 0.15s; appearance: none; }
  .filter-select:focus { border-color: var(--accent); }

  .detail-panel { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px; }
  .detail-title { font-size: 20px; font-weight: 800; margin-bottom: 12px; line-height: 1.3; }
  .detail-desc { font-size: 13px; color: var(--muted); line-height: 1.7; font-family: var(--mono); white-space: pre-wrap; }
  .detail-meta { display: flex; gap: 8px; flex-wrap: wrap; margin: 16px 0; align-items: center; }
  .detail-actions { display: flex; gap: 8px; margin-top: 16px; }

  .comment-item { padding: 14px 0; border-bottom: 1px solid var(--border); }
  .comment-item:last-child { border-bottom: none; }
  .comment-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
  .comment-body { font-size: 13px; line-height: 1.6; color: var(--muted); font-family: var(--mono); }
  .comment-user { font-size: 12px; font-weight: 700; }

  .empty-state { text-align: center; padding: 60px 20px; }
  .empty-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.4; }
  .empty-title { font-size: 16px; font-weight: 700; margin-bottom: 6px; }
  .empty-sub { font-size: 12px; color: var(--muted); font-family: var(--mono); }

  .toast-container { position: fixed; bottom: 24px; right: 24px; z-index: 9999; display: flex; flex-direction: column; gap: 8px; }
  .toast { background: var(--surface2); border: 1px solid var(--border); border-radius: 10px; padding: 12px 16px; font-size: 13px; font-weight: 600; animation: slideInRight 0.2s ease; display: flex; align-items: center; gap: 8px; min-width: 240px; max-width: 320px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); }
  .toast-success { border-left: 3px solid var(--accent3); }
  .toast-error { border-left: 3px solid var(--danger); }

  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
  @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
  @keyframes slideInRight { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }

  .divider { height: 1px; background: var(--border); margin: 20px 0; }
  .flex { display: flex; }
  .items-center { align-items: center; }
  .gap-2 { gap: 8px; }
  .text-muted { color: var(--muted); }
  .text-sm { font-size: 12px; font-family: var(--mono); }
  .back-btn { background: none; border: none; color: var(--muted); cursor: pointer; font-size: 13px; font-family: var(--font); display: flex; align-items: center; gap: 6px; margin-bottom: 20px; padding: 0; }
  .back-btn:hover { color: var(--text); }
  .spinner { width: 18px; height: 18px; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.6s linear infinite; display: inline-block; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .loading-center { display: flex; justify-content: center; align-items: center; padding: 60px; }
  .error-msg { background: rgba(255,77,109,0.1); border: 1px solid rgba(255,77,109,0.2); border-radius: 8px; padding: 10px 14px; color: var(--danger); font-size: 12px; margin-bottom: 16px; font-family: var(--mono); }
  .section-title { font-size: 13px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: var(--muted); margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }

  @media (max-width: 768px) {
    .sidebar { display: none; }
    .main { margin-left: 0; }
    .form-row { grid-template-columns: 1fr; }
    .projects-grid { grid-template-columns: 1fr; }
  }
`;

// ─── TOAST ────────────────────────────────────────────────────────────────────
const ToastContext = createContext(null);
const useToast = () => useContext(ToastContext);

function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const add = useCallback((msg, type = "success") => {
    const id = Date.now();
    setToasts(t => [...t, { id, msg, type }]);
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 3500);
  }, []);
  return (
    <ToastContext.Provider value={add}>
      {children}
      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`toast toast-${t.type}`}>
            {t.type === "success" ? "✓" : "✗"} {t.msg}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

// ─── MODAL ────────────────────────────────────────────────────────────────────
function Modal({ title, onClose, children, footer }) {
  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <div className="modal-title">{title}</div>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>
  );
}

// ─── AUTH PAGE ────────────────────────────────────────────────────────────────
function AuthPage({ onAuth }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const toast = useToast();

  const submit = async () => {
    setError("");
    if (!form.email || !form.password) { setError("Email and password are required"); return; }
    setLoading(true);
    try {
      if (mode === "signup") {
        if (!form.name.trim()) { setError("Name is required"); setLoading(false); return; }
        // UserCreate: { name, email, password }
        await api("/auth/signup", "POST", {
          name: form.name,
          email: form.email,
          password: form.password,
        });
        toast("Account created! Please log in.", "success");
        setMode("login");
      } else {
        // UserLogin: { email, password }
        const data = await api("/auth/login", "POST", {
          email: form.email,
          password: form.password,
        });
        onAuth(data.access_token, form.email);
        toast("Welcome back!", "success");
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const f = k => e => setForm(p => ({ ...p, [k]: e.target.value }));
  const onKey = e => e.key === "Enter" && submit();

  return (
    <div className="auth-page">
      <div className="auth-box">
        <div className="auth-card">
          <div style={{ textAlign: "center", marginBottom: 28 }}>
            <div className="auth-logo-icon">IH</div>
          </div>
          <div className="auth-title">{mode === "login" ? "Welcome back" : "Create account"}</div>
          <div className="auth-sub">{mode === "login" ? "Sign in to IssueHub" : "Start tracking issues today"}</div>
          {error && <div className="error-msg">{error}</div>}
          {mode === "signup" && (
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input className="form-input" placeholder="John Doe" value={form.name} onChange={f("name")} onKeyDown={onKey} />
            </div>
          )}
          <div className="form-group">
            <label className="form-label">Email</label>
            <input className="form-input" type="email" placeholder="john@example.com" value={form.email} onChange={f("email")} onKeyDown={onKey} />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input className="form-input" type="password" placeholder="••••••••" value={form.password} onChange={f("password")} onKeyDown={onKey} />
          </div>
          <button className="btn btn-primary" style={{ width: "100%", justifyContent: "center" }} onClick={submit} disabled={loading}>
            {loading ? <span className="spinner" /> : mode === "login" ? "Sign In" : "Create Account"}
          </button>
          <div className="auth-switch">
            {mode === "login" ? "Don't have an account? " : "Already have an account? "}
            <button onClick={() => { setMode(mode === "login" ? "signup" : "login"); setError(""); }}>
              {mode === "login" ? "Sign up" : "Log in"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── PROJECTS PAGE ────────────────────────────────────────────────────────────
function ProjectsPage({ onSelectProject }) {
  const { token } = useAuth();
  const toast = useToast();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ name: "", key: "", description: "" });
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try { setProjects(await api("/projects/", "GET", null, token)); }
    catch (e) { toast(e.message, "error"); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { load(); }, [load]);

  const create = async () => {
    setError("");
    if (!form.name.trim()) { setError("Project name is required"); return; }
    if (!form.key.trim()) { setError("Project key is required (e.g. BUG, FE, API)"); return; }
    setCreating(true);
    try {
      // ProjectCreate: { name, key, description }
      await api("/projects/", "POST", {
        name: form.name,
        key: form.key.toUpperCase(),
        description: form.description,
      }, token);
      toast("Project created!", "success");
      setShowModal(false);
      setForm({ name: "", key: "", description: "" });
      load();
    } catch (e) {
      setError(e.message);
    } finally { setCreating(false); }
  };

  return (
    <div className="content">
      <div className="page-header">
        <div>
          <div className="page-title">Projects</div>
          <div className="page-subtitle">{projects.length} projects</div>
        </div>
        <button className="btn btn-primary" onClick={() => { setShowModal(true); setError(""); }}>＋ New Project</button>
      </div>

      {loading ? (
        <div className="loading-center"><div className="spinner" /></div>
      ) : projects.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📁</div>
          <div className="empty-title">No projects yet</div>
          <div className="empty-sub">Create your first project to get started</div>
          <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => setShowModal(true)}>Create Project</button>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map(p => (
            <div key={p.id} className="project-card" onClick={() => onSelectProject(p)}>
              <div className="flex items-center gap-2" style={{ marginBottom: 6 }}>
                <div className="avatar" style={{ width: 28, height: 28, fontSize: 11, borderRadius: 8 }}>
                  {p.name.charAt(0).toUpperCase()}
                </div>
                <div className="project-name">{p.name}</div>
              </div>
              <div className="project-key">{p.key}</div>
              <div className="project-desc">{p.description || "No description"}</div>
              <div className="project-id">ID: #{p.id}</div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <Modal title="Create Project" onClose={() => setShowModal(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowModal(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={create} disabled={creating}>
              {creating ? <span className="spinner" /> : "Create"}
            </button>
          </>}>
          {error && <div className="error-msg">{error}</div>}
          <div className="form-group">
            <label className="form-label">Project Name</label>
            <input className="form-input" placeholder="e.g. Bug Tracker" value={form.name}
              onChange={e => setForm(p => ({ ...p, name: e.target.value }))} />
          </div>
          <div className="form-group">
            <label className="form-label">Project Key</label>
            <input className="form-input" placeholder="e.g. BUG" value={form.key}
              onChange={e => setForm(p => ({ ...p, key: e.target.value.toUpperCase() }))}
              maxLength={10} />
            <div className="form-hint">Short unique identifier for this project (e.g. BUG, FE, API)</div>
          </div>
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea className="form-textarea" placeholder="What is this project about?" value={form.description}
              onChange={e => setForm(p => ({ ...p, description: e.target.value }))} />
          </div>
        </Modal>
      )}
    </div>
  );
}

// ─── ISSUES PAGE ──────────────────────────────────────────────────────────────
function IssuesPage({ project, onBack }) {
  const { token } = useAuth();
  const toast = useToast();
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [filters, setFilters] = useState({ status: "", priority: "" });
  const [showCreate, setShowCreate] = useState(false);
  const [showEdit, setShowEdit] = useState(false);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState("");
  const [posting, setPosting] = useState(false);

  const loadIssues = useCallback(async () => {
    setLoading(true);
    try {
      const q = new URLSearchParams();
      if (filters.status) q.set("status", filters.status);
      if (filters.priority) q.set("priority", filters.priority);
      // GET /api/issues/project/{project_id}
      const data = await api(`/issues/project/${project.id}?${q}`, "GET", null, token);
      setIssues(data);
    } catch (e) { toast(e.message, "error"); }
    finally { setLoading(false); }
  }, [token, project.id, filters]);

  useEffect(() => { loadIssues(); }, [loadIssues]);

  const loadComments = async (issueId) => {
    try {
      // GET /api/comments/issue/{issue_id}
      setComments(await api(`/comments/issue/${issueId}`, "GET", null, token));
    } catch { setComments([]); }
  };

  const selectIssue = (issue) => {
    setSelected(issue);
    loadComments(issue.id);
  };

  const deleteIssue = async (id) => {
    if (!window.confirm("Delete this issue?")) return;
    try {
      // DELETE /api/issues/{issue_id}
      await api(`/issues/${id}`, "DELETE", null, token);
      toast("Issue deleted", "success");
      setSelected(null);
      loadIssues();
    } catch (e) { toast(e.message, "error"); }
  };

  const postComment = async () => {
    if (!commentText.trim() || !selected) return;
    setPosting(true);
    try {
      // POST /api/comments/issue/{issue_id}  body: { body: string }
      await api(`/comments/issue/${selected.id}`, "POST", { body: commentText }, token);
      setCommentText("");
      loadComments(selected.id);
      toast("Comment added", "success");
    } catch (e) { toast(e.message, "error"); }
    finally { setPosting(false); }
  };

  return (
    <div className="content">
      <button className="back-btn" onClick={onBack}>← Back to Projects</button>
      <div className="page-header">
        <div>
          <div className="page-title">{project.name}</div>
          <div className="page-subtitle">
            <span style={{ color: "var(--accent)", marginRight: 8 }}>{project.key}</span>
            {issues.length} issues
          </div>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>＋ New Issue</button>
      </div>

      <div className="filters">
        <span className="text-sm text-muted">Filter:</span>
        <select className="filter-select" value={filters.status}
          onChange={e => setFilters(p => ({ ...p, status: e.target.value }))}>
          <option value="">All Status</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="closed">Closed</option>
        </select>
        <select className="filter-select" value={filters.priority}
          onChange={e => setFilters(p => ({ ...p, priority: e.target.value }))}>
          <option value="">All Priority</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        {(filters.status || filters.priority) && (
          <button className="btn btn-ghost btn-sm" onClick={() => setFilters({ status: "", priority: "" })}>Clear</button>
        )}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: selected ? "1fr 1fr" : "1fr", gap: 16 }}>
        {/* Issue List */}
        <div className="card">
          {loading ? (
            <div className="loading-center"><div className="spinner" /></div>
          ) : issues.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🐞</div>
              <div className="empty-title">No issues found</div>
              <div className="empty-sub">Create your first issue or adjust filters</div>
            </div>
          ) : (
            issues.map(issue => (
              <div key={issue.id}
                className={`issue-row ${selected?.id === issue.id ? "selected" : ""}`}
                onClick={() => selectIssue(issue)}>
                <div style={{ flex: 1 }}>
                  <div className="issue-title">{issue.title}</div>
                  <div className="issue-meta" style={{ marginTop: 4 }}>#{issue.id}</div>
                </div>
                <span className={`badge badge-${issue.priority}`}>{issue.priority}</span>
                <span className={`badge badge-${issue.status}`}>{issue.status?.replace("_", " ")}</span>
              </div>
            ))
          )}
        </div>

        {/* Issue Detail + Comments */}
        {selected && (
          <div className="detail-panel">
            <button className="btn btn-ghost btn-sm" style={{ marginBottom: 16 }}
              onClick={() => setSelected(null)}>✕ Close</button>
            <div className="detail-title">{selected.title}</div>
            <div className="detail-meta">
              <span className={`badge badge-${selected.status}`}>{selected.status?.replace("_", " ")}</span>
              <span className={`badge badge-${selected.priority}`}>{selected.priority} priority</span>
            </div>
            {selected.description && <div className="detail-desc">{selected.description}</div>}
            <div className="text-sm text-muted" style={{ marginTop: 10 }}>
              Reporter ID: {selected.reporter_id}
            </div>
            <div className="detail-actions">
              <button className="btn btn-ghost btn-sm" onClick={() => setShowEdit(true)}>✎ Edit</button>
              <button className="btn btn-danger btn-sm" onClick={() => deleteIssue(selected.id)}>🗑 Delete</button>
            </div>

            <div className="divider" />
            <div className="section-title">💬 Comments ({comments.length})</div>

            {comments.length === 0
              ? <div className="text-sm text-muted" style={{ marginBottom: 12 }}>No comments yet</div>
              : comments.map(c => (
                <div key={c.id} className="comment-item">
                  <div className="comment-header">
                    <div className="avatar" style={{ width: 24, height: 24, fontSize: 10 }}>
                      {String(c.author_id || "?").charAt(0)}
                    </div>
                    {/* comments.py uses author_id, not user_id */}
                    <span className="comment-user">User #{c.author_id}</span>
                  </div>
                  <div className="comment-body">{c.body}</div>
                </div>
              ))
            }

            <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
              <input className="form-input" placeholder="Add a comment…" value={commentText}
                onChange={e => setCommentText(e.target.value)}
                onKeyDown={e => e.key === "Enter" && postComment()} />
              <button className="btn btn-primary btn-sm" onClick={postComment} disabled={posting}>
                {posting ? "…" : "Post"}
              </button>
            </div>
          </div>
        )}
      </div>

      {showCreate && (
        <CreateIssueModal projectId={project.id} token={token} toast={toast}
          onClose={() => setShowCreate(false)}
          onCreated={() => { setShowCreate(false); loadIssues(); }} />
      )}

      {showEdit && selected && (
        <EditIssueModal issue={selected} token={token} toast={toast}
          onClose={() => setShowEdit(false)}
          onUpdated={(updated) => { setShowEdit(false); setSelected(updated); loadIssues(); }} />
      )}
    </div>
  );
}

// ─── CREATE ISSUE MODAL ───────────────────────────────────────────────────────
function CreateIssueModal({ projectId, token, toast, onClose, onCreated }) {
  const [form, setForm] = useState({ title: "", description: "", priority: "medium" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const f = k => e => setForm(p => ({ ...p, [k]: e.target.value }));

  const submit = async () => {
    if (!form.title.trim()) { setError("Title is required"); return; }
    setLoading(true); setError("");
    try {
      // POST /api/issues/project/{project_id}
      // IssueCreate: { title, description, priority }
      await api(`/issues/project/${projectId}`, "POST", {
        title: form.title,
        description: form.description,
        priority: form.priority,
      }, token);
      toast("Issue created!", "success");
      onCreated();
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  return (
    <Modal title="Create Issue" onClose={onClose}
      footer={<>
        <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
        <button className="btn btn-primary" onClick={submit} disabled={loading}>
          {loading ? <span className="spinner" /> : "Create Issue"}
        </button>
      </>}>
      {error && <div className="error-msg">{error}</div>}
      <div className="form-group">
        <label className="form-label">Title</label>
        <input className="form-input" placeholder="e.g. Login button not working"
          value={form.title} onChange={f("title")} />
      </div>
      <div className="form-group">
        <label className="form-label">Description</label>
        <textarea className="form-textarea" placeholder="Describe the issue in detail…"
          value={form.description} onChange={f("description")} />
      </div>
      <div className="form-group">
        <label className="form-label">Priority</label>
        <select className="form-select" value={form.priority} onChange={f("priority")}>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>
    </Modal>
  );
}

// ─── EDIT ISSUE MODAL ─────────────────────────────────────────────────────────
function EditIssueModal({ issue, token, toast, onClose, onUpdated }) {
  const [form, setForm] = useState({
    title: issue.title || "",
    description: issue.description || "",
    status: issue.status || "open",
    priority: issue.priority || "medium",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const f = k => e => setForm(p => ({ ...p, [k]: e.target.value }));

  const submit = async () => {
    setLoading(true); setError("");
    try {
      // PATCH /api/issues/{issue_id}
      // IssueUpdate: { title?, description?, status?, priority? }
      const updated = await api(`/issues/${issue.id}`, "PATCH", form, token);
      toast("Issue updated!", "success");
      onUpdated(updated);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  return (
    <Modal title="Edit Issue" onClose={onClose}
      footer={<>
        <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
        <button className="btn btn-primary" onClick={submit} disabled={loading}>
          {loading ? <span className="spinner" /> : "Save Changes"}
        </button>
      </>}>
      {error && <div className="error-msg">{error}</div>}
      <div className="form-group">
        <label className="form-label">Title</label>
        <input className="form-input" value={form.title} onChange={f("title")} />
      </div>
      <div className="form-group">
        <label className="form-label">Description</label>
        <textarea className="form-textarea" value={form.description} onChange={f("description")} />
      </div>
      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Status</label>
          <select className="form-select" value={form.status} onChange={f("status")}>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="closed">Closed</option>
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Priority</label>
          <select className="form-select" value={form.priority} onChange={f("priority")}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
      </div>
    </Modal>
  );
}

// ─── SIDEBAR ──────────────────────────────────────────────────────────────────
function Sidebar({ page, onNav, user, onLogout, projectName }) {
  return (
    <div className="sidebar">
      <div className="logo">
        <div className="logo-icon">IH</div>
        <div className="logo-text">IssueHub</div>
      </div>
      <div className="nav-section">
        <div className="nav-label">Main</div>
        <button className={`nav-item ${page === "projects" ? "active" : ""}`} onClick={() => onNav("projects")}>
          <span className="icon">📁</span> Projects
        </button>
      </div>
      {projectName && (
        <div className="nav-section" style={{ marginTop: 8 }}>
          <div className="nav-label">Current Project</div>
          <button className={`nav-item ${page === "issues" ? "active" : ""}`} onClick={() => onNav("issues")}>
            <span className="icon">🐞</span>
            <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{projectName}</span>
          </button>
        </div>
      )}
      <div className="sidebar-bottom">
        <div className="user-chip">
          <div className="avatar">{user?.charAt(0)?.toUpperCase() || "U"}</div>
          <div className="user-info">
            <div className="user-name">{user || "User"}</div>
            <div className="user-role">member</div>
          </div>
          <button className="logout-btn" onClick={onLogout} title="Sign out">↩</button>
        </div>
      </div>
    </div>
  );
}

// ─── APP ──────────────────────────────────────────────────────────────────────
export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("ih_token") || "");
  const [userEmail, setUserEmail] = useState(() => localStorage.getItem("ih_email") || "");
  const [page, setPage] = useState("projects");
  const [project, setProject] = useState(null);

  const handleAuth = (t, email) => {
    setToken(t); setUserEmail(email);
    localStorage.setItem("ih_token", t);
    localStorage.setItem("ih_email", email);
  };

  const handleLogout = () => {
    setToken(""); setUserEmail(""); setProject(null); setPage("projects");
    localStorage.removeItem("ih_token");
    localStorage.removeItem("ih_email");
  };

  const handleSelectProject = (p) => { setProject(p); setPage("issues"); };

  if (!token) {
    return (
      <ToastProvider>
        <style>{styles}</style>
        <AuthPage onAuth={handleAuth} />
      </ToastProvider>
    );
  }

  return (
    <AuthContext.Provider value={{ token, userEmail }}>
      <ToastProvider>
        <style>{styles}</style>
        <div className="app">
          <Sidebar
            page={page} onNav={setPage} user={userEmail}
            onLogout={handleLogout} projectName={project?.name}
          />
          <div className="main">
            {page === "projects" && <ProjectsPage onSelectProject={handleSelectProject} />}
            {page === "issues" && project && (
              <IssuesPage project={project} onBack={() => setPage("projects")} />
            )}
          </div>
        </div>
      </ToastProvider>
    </AuthContext.Provider>
  );
}