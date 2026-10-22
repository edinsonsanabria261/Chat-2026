:root {
  --red-1: #ff4d6d;
  --red-2: #8b5cf6;
  --red-3: #f43f5e;
  --ink: #07111f;
  --card: rgba(15, 23, 42, 0.72);
  --card-strong: rgba(15, 23, 42, 0.9);
  --text: #e2e8f0;
  --text-soft: #94a3b8;
  --line: rgba(148, 163, 184, 0.2);
  --line-light: rgba(148, 163, 184, 0.35);
  --sky: #38bdf8;
  --sky-strong: #22d3ee;
  --ok: #4ade80;
  --warn: #fbbf24;
  --bad: #f87171;
  --canvas: #020817;
  --canvas-2: #0f172a;
  --white: #ffffff;
  --radius: 18px;
  --shadow: 0 20px 50px rgba(11, 17, 31, 0.6);
  font-family: "Segoe UI", "Inter", "SF Pro Display", system-ui, sans-serif;
}

* { box-sizing: border-box; }

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(56, 189, 248, 0.16), transparent 25%),
    radial-gradient(circle at bottom right, rgba(139, 92, 246, 0.2), transparent 30%),
    linear-gradient(135deg, var(--canvas) 0%, #0b1120 45%, #111827 100%);
  color: var(--text);
}

h1, h2, h3, h4, p { margin: 0; }

button, input, select, textarea { font: inherit; }

button { cursor: pointer; }

input, select, textarea {
  width: 100%;
  margin-top: 0.4rem;
  padding: 0.8rem 0.95rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.75);
  color: var(--text);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
  transition: border-color 0.25s ease, box-shadow 0.25s ease, background 0.25s ease, transform 0.2s ease;
}

input::placeholder,
textarea::placeholder {
  color: rgba(148, 163, 184, 0.8);
}

textarea { resize: vertical; }

label {
  display: block;
  margin-top: 0.9rem;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: rgba(226, 232, 240, 0.85);
}

button:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible {
  outline: none;
}

.login-layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1.12fr;
  gap: 1.75rem;
  align-items: center;
  padding: clamp(1rem, 4vw, 3.5rem);
}

.hero {
  background: linear-gradient(135deg, rgba(255, 77, 109, 0.18), rgba(139, 92, 246, 0.18));
  border: 1px solid rgba(148, 163, 184, 0.18);
  backdrop-filter: blur(10px);
  color: white;
  border-radius: var(--radius);
  padding: 2.4rem;
  box-shadow: var(--shadow);
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, rgba(34, 211, 238, 0.12), transparent 40%, rgba(255, 77, 109, 0.12));
  pointer-events: none;
}

.eyebrow {
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.8);
  margin-bottom: 0.8rem;
}

.hero h1 {
  font-size: clamp(2rem, 3vw, 3rem);
  font-weight: 800;
  line-height: 1.1;
  margin: 0.5rem 0 1rem;
  letter-spacing: -0.04em;
}

.hero-copy {
  font-size: 0.98rem;
  line-height: 1.7;
  color: rgba(255,255,255,0.82);
}

.auth-card, .panel-block, .command {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 18px;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 14px 40px rgba(2, 6, 23, 0.5);
}

.auth-card {
  position: relative;
  overflow: hidden;
}

.auth-card::before,
.panel-block::before,
.command::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.04), rgba(139, 92, 246, 0.03), transparent 60%);
  pointer-events: none;
}

.auth-card > *, .panel-block > *, .command > * {
  position: relative;
  z-index: 1;
}

.auth-card h2 {
  font-size: clamp(1.5rem, 2vw, 1.8rem);
  font-weight: 700;
  letter-spacing: -0.04em;
}

.muted { color: var(--text-soft); margin-top: 0.35rem; font-size: 0.92rem; }

.tabs {
  display: flex;
  gap: 0.35rem;
  margin: 1.2rem 0 0.8rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
  padding-bottom: 0.25rem;
}

.tabs button {
  background: transparent;
  border: 0;
  border-bottom: 2px solid transparent;
  padding: 0.75rem 1rem;
  color: var(--text-soft);
  font-weight: 700;
  letter-spacing: 0.02em;
  transition: all 0.25s ease;
}

.tabs button[aria-selected="true"] {
  color: #f8fafc;
  border-bottom-color: rgba(56, 189, 248, 0.9);
  background: rgba(56, 189, 248, 0.06);
}

.btn-primary, .btn-danger, .btn-ghost, .open-link {
  border-radius: 12px;
  padding: 0.82rem 1rem;
  font-weight: 700;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.25s ease, box-shadow 0.25s ease, filter 0.25s ease, border-color 0.25s ease;
}

.btn-primary {
  width: 100%;
  margin-top: 1rem;
  background: linear-gradient(135deg, #ff4d6d 0%, #8b5cf6 35%, #22d3ee 100%);
  color: white;
  border: 0;
  box-shadow: 0 12px 24px rgba(139, 92, 246, 0.35);
}

.btn-primary:hover,
.btn-danger:hover,
.btn-ghost:hover,
.open-link:hover {
  transform: translateY(-1px) scale(1.01);
  filter: brightness(1.08);
}

.btn-primary:active,
.btn-danger:active,
.btn-ghost:active,
.open-link:active {
  transform: scale(0.99);
}

.btn-danger {
  background: rgba(239, 68, 68, 0.1);
  color: #fca5a5;
  border: 1px solid rgba(248, 113, 113, 0.35);
}

.btn-ghost {
  background: rgba(148, 163, 184, 0.08);
  color: var(--on-dark);
  border: 1px solid var(--line);
}

.form-error, .form-ok {
  min-height: 1.2rem;
  margin: 0.8rem 0 0;
  font-size: 0.9rem;
}

.form-error { color: #fca5a5; }
.form-ok { color: #86efac; }

.hint {
  margin-top: 0.35rem;
  font-size: 0.76rem;
  color: var(--text-soft);
  line-height: 1.5;
}

.fine-print {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.74rem;
  color: var(--text-soft);
}

.input-glow {
  border-color: rgba(34, 211, 238, 0.9) !important;
  box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.45), 0 0 18px rgba(34, 211, 238, 0.18) !important;
  background: rgba(15, 23, 42, 0.9) !important;
}

.app-shell {
  max-width: 1080px;
  margin: 0 auto;
  padding: 1.25rem;
}

.command {
  background: rgba(15, 23, 42, 0.82);
  border: 1px solid rgba(148, 163, 184, 0.18);
  color: var(--on-dark);
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  margin-bottom: 0.75rem;
}

.command p { color: var(--text-soft); margin-top: 0.3rem; font-size: 0.85rem; }

.panel-head, .form-row, .crud-actions {
  display: flex;
  gap: 0.8rem;
  align-items: end;
  justify-content: space-between;
}

.form-row label, .filter { flex: 1; }

.filter { font-size: 0.85rem; font-weight: 700; min-width: 180px; color: var(--text-soft); }

.hub-toolbar {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 0.8rem;
  margin: 1rem 0 0.8rem;
}

.filter-field {
  display: block;
  color: var(--text-soft);
  font-size: 0.78rem;
  font-weight: 700;
}

.app-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
  margin-top: 1rem;
}

.app-card {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 12px;
  padding: 15px;
  color: var(--white);
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  box-shadow: 0 12px 22px rgba(2, 6, 23, 0.28);
}

.app-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.app-card h4 { font-size: 1rem; }
.app-card .version { color: var(--sky); font-size: 0.75rem; font-weight: 700; }
.app-card p { color: rgba(226, 232, 240, 0.8); font-size: 0.85rem; }
.app-card .meta { font-size: 0.75rem; color: var(--ok); }
.app-card .meta.warn { color: var(--warn); }
.app-card .meta.bad { color: var(--bad); }
.app-extra {
  color: var(--text-soft) !important;
  font-size: 0.75rem !important;
}

.favorite {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.6rem;
  height: 1.6rem;
  border-radius: 999px;
  font-size: 0.9rem;
  background: rgba(148, 163, 184, 0.08);
  color: #fbbf24;
}

.favorite.active { background: rgba(251, 191, 36, 0.12); }

.priority-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  background: rgba(56, 189, 248, 0.08);
  color: var(--sky);
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.tag {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0.2rem 0.5rem;
  font-size: 0.68rem;
  background: rgba(139, 92, 246, 0.12);
  color: #d8b4fe;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.open-link {
  margin-top: 0.5rem;
  background: rgba(30, 41, 59, 0.9);
  color: white;
  border: 1px solid rgba(148, 163, 184, 0.18);
}

.metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.8rem;
  margin-top: 1rem;
}

.metric {
  background: rgba(15, 23, 42, 0.8);
  color: var(--white);
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  padding: 1rem;
}

.metric span { display: block; color: rgba(148, 163, 184, 0.9); font-size: 0.8rem; }
.metric strong { display: block; margin-top: 0.35rem; font-size: 1.4rem; }

.empty {
  grid-column: 1 / -1;
  color: var(--text-soft);
  padding: 1rem 0;
}

.checkbox-field {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.75rem;
  margin-top: 1rem;
}

.checkbox-field input {
  width: 1.1rem;
  height: 1.1rem;
  margin: 0;
}

@media (max-width: 800px) {
  .login-layout, .app-grid, .metrics, .form-row, .command, .panel-head {
    grid-template-columns: 1fr;
    display: grid;
  }

  .hub-toolbar {
    grid-template-columns: 1fr;
  }

  .command, .panel-head { align-items: stretch; }
  .btn-ghost, .crud-actions { width: 100%; }
  .crud-actions { display: grid; }
}

@media (max-width: 480px) {
  .app-shell {
    padding: 0.8rem;
  }

  .auth-card, .panel-block, .command {
    padding: 1rem;
  }
}

