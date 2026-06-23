import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

export default function AdminPage() {
  const navigate = useNavigate();
  const [tab,   setTab]   = useState("docs");
  const [docs,  setDocs]  = useState([]);
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [msg, setMsg] = useState({ text: "", type: "" });
  const fileRef = useRef();

  useEffect(() => {
    fetchDocs(); fetchUsers(); fetchStats();
  }, []);

  const fetchDocs  = () => api.get("/api/documents/").then(r => setDocs(r.data));
  const fetchUsers = () => api.get("/api/admin/users").then(r => setUsers(r.data));
  const fetchStats = () => api.get("/api/admin/stats").then(r => setStats(r.data));

  const notify = (text, type = "success") => {
    setMsg({ text, type });
    setTimeout(() => setMsg({ text: "", type: "" }), 3500);
  };

  const handleUpload = async e => {
    const files = Array.from(e.target.files);
    if (!files.length) return;
    setUploading(true);
    let ok = 0, fail = 0;
    for (const file of files) {
      const fd = new FormData();
      fd.append("file", file);
      try {
        await api.post("/api/documents/upload", fd);
        ok++;
      } catch { fail++; }
    }
    setUploading(false);
    fetchDocs();
    notify(`${ok} document(s) indexé(s)${fail ? `, ${fail} échec(s)` : ""}.`);
    fileRef.current.value = "";
  };

  const deleteDoc = async filename => {
    if (!confirm(`Supprimer "${filename}" ?`)) return;
    await api.delete(`/api/documents/${filename}`);
    fetchDocs();
    notify(`${filename} supprimé.`);
  };

  const toggleUser = async (uid, active) => {
    await api.patch(`/api/admin/users/${uid}`, { is_active: active });
    fetchUsers();
  };

  const changeRole = async (uid, role) => {
    await api.patch(`/api/admin/users/${uid}`, { role });
    fetchUsers();
  };

  return (
    <div style={S.page}>
      <header style={S.header}>
        <button onClick={() => navigate("/")} style={S.back}>← Retour au chat</button>
        <h1 style={{ fontSize: "1.2rem", fontWeight: 700 }}>Administration</h1>
        {stats && (
          <div style={S.statRow}>
            <Stat label="Utilisateurs" value={stats.users} />
            <Stat label="Sessions"     value={stats.sessions} />
            <Stat label="Messages"     value={stats.messages} />
          </div>
        )}
      </header>

      {msg.text && (
        <div style={{ ...S.toast, background: msg.type === "success" ? "#4caf7d22" : "#e05c5c22",
          color: msg.type === "success" ? "var(--success)" : "var(--danger)",
          border: `1px solid ${msg.type === "success" ? "var(--success)" : "var(--danger)"}` }}>
          {msg.text}
        </div>
      )}

      <div style={S.tabs}>
        <Tab label="📄 Documents" active={tab === "docs"}   onClick={() => setTab("docs")} />
        <Tab label="👥 Utilisateurs" active={tab === "users"} onClick={() => setTab("users")} />
      </div>

      {tab === "docs" && (
        <div style={S.section}>
          <div style={S.uploadZone}>
            <p style={{ color: "var(--text2)", marginBottom: ".75rem" }}>
              Formats acceptés : PDF, DOCX, XLSX, TXT, MD
            </p>
            <input ref={fileRef} type="file" multiple accept=".pdf,.docx,.xlsx,.txt,.md"
              onChange={handleUpload} style={{ display: "none" }} id="file-input" />
            <label htmlFor="file-input" style={S.uploadBtn}>
              {uploading ? "Indexation en cours…" : "📤 Choisir des fichiers"}
            </label>
          </div>

          <table style={S.table}>
            <thead>
              <tr>{["Fichier", "Taille", "Actions"].map(h =>
                <th key={h} style={S.th}>{h}</th>)}</tr>
            </thead>
            <tbody>
              {docs.map(d => (
                <tr key={d.filename} style={S.tr}>
                  <td style={S.td}>📄 {d.filename}</td>
                  <td style={S.td}>{d.size_kb} Ko</td>
                  <td style={S.td}>
                    <button onClick={() => deleteDoc(d.filename)} style={S.dangerBtn}>
                      Supprimer
                    </button>
                  </td>
                </tr>
              ))}
              {docs.length === 0 && (
                <tr><td colSpan={3} style={{ ...S.td, color: "var(--text2)", textAlign: "center" }}>
                  Aucun document indexé
                </td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {tab === "users" && (
        <div style={S.section}>
          <table style={S.table}>
            <thead>
              <tr>{["Utilisateur", "Email", "Rôle", "Statut", "Actions"].map(h =>
                <th key={h} style={S.th}>{h}</th>)}</tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} style={S.tr}>
                  <td style={S.td}>{u.username}</td>
                  <td style={S.td}>{u.email}</td>
                  <td style={S.td}>
                    <select value={u.role} onChange={e => changeRole(u.id, e.target.value)}
                      style={{ ...S.sel, background: u.role === "admin" ? "#6c8ef522" : "var(--bg3)" }}>
                      <option value="user">user</option>
                      <option value="admin">admin</option>
                    </select>
                  </td>
                  <td style={S.td}>
                    <span style={{ ...S.badge,
                      background: u.is_active ? "#4caf7d22" : "#e05c5c22",
                      color: u.is_active ? "var(--success)" : "var(--danger)" }}>
                      {u.is_active ? "Actif" : "Inactif"}
                    </span>
                  </td>
                  <td style={S.td}>
                    <button onClick={() => toggleUser(u.id, !u.is_active)}
                      style={u.is_active ? S.dangerBtn : S.successBtn}>
                      {u.is_active ? "Désactiver" : "Activer"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const Stat = ({ label, value }) => (
  <div style={{ textAlign: "center" }}>
    <div style={{ fontWeight: 700, fontSize: "1.25rem" }}>{value}</div>
    <div style={{ color: "var(--text2)", fontSize: ".75rem" }}>{label}</div>
  </div>
);

const Tab = ({ label, active, onClick }) => (
  <button onClick={onClick} style={{
    ...S.tabBtn, ...(active ? S.tabActive : {})
  }}>{label}</button>
);

const S = {
  page:    { minHeight: "100vh", background: "var(--bg)", padding: "0 0 3rem" },
  header:  { background: "var(--bg2)", borderBottom: "1px solid var(--border)",
             padding: "1rem 2rem", display: "flex", alignItems: "center", gap: "2rem" },
  back:    { background: "var(--bg3)", color: "var(--text)", border: "1px solid var(--border)",
             padding: ".4rem .85rem", fontSize: ".85rem" },
  statRow: { display: "flex", gap: "1.5rem", marginLeft: "auto" },
  toast:   { margin: "1rem 2rem", padding: ".6rem 1rem", borderRadius: 8, fontSize: ".875rem" },
  tabs:    { display: "flex", gap: ".5rem", padding: "1.25rem 2rem .5rem" },
  tabBtn:  { background: "transparent", color: "var(--text2)", border: "1px solid var(--border)",
             padding: ".45rem 1rem", fontSize: ".875rem" },
  tabActive: { background: "var(--accent)", color: "#fff", border: "1px solid var(--accent)" },
  section: { padding: "1rem 2rem" },
  uploadZone: { background: "var(--bg2)", border: "2px dashed var(--border)",
                borderRadius: 12, padding: "2rem", textAlign: "center", marginBottom: "1.5rem" },
  uploadBtn: { background: "var(--accent)", color: "#fff", padding: ".6rem 1.25rem",
               borderRadius: 8, cursor: "pointer", fontWeight: 600, display: "inline-block" },
  table:   { width: "100%", borderCollapse: "collapse", background: "var(--bg2)",
             borderRadius: 10, overflow: "hidden", border: "1px solid var(--border)" },
  th:      { textAlign: "left", padding: ".65rem 1rem", background: "var(--bg3)",
             color: "var(--text2)", fontSize: ".8rem", fontWeight: 600,
             borderBottom: "1px solid var(--border)" },
  td:      { padding: ".65rem 1rem", borderBottom: "1px solid var(--border)", fontSize: ".875rem" },
  tr:      { transition: "background .1s" },
  dangerBtn:  { background: "#e05c5c22", color: "var(--danger)", border: "1px solid var(--danger)",
                padding: ".3rem .7rem", fontSize: ".8rem", borderRadius: 6 },
  successBtn: { background: "#4caf7d22", color: "var(--success)", border: "1px solid var(--success)",
                padding: ".3rem .7rem", fontSize: ".8rem", borderRadius: 6 },
  sel:     { border: "1px solid var(--border)", padding: ".25rem .5rem",
             borderRadius: 6, fontSize: ".8rem", color: "var(--text)" },
  badge:   { padding: ".2rem .5rem", borderRadius: 4, fontSize: ".78rem", fontWeight: 600 },
};
