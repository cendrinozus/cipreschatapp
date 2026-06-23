import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";
import ReactMarkdown from "react-markdown";

export default function ChatPage() {
  const { user, logout }   = useAuth();
  const navigate           = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input,    setInput]    = useState("");
  const [loading,  setLoading]  = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => { fetchSessions(); }, []);
  useEffect(() => { if (activeId) fetchMessages(activeId); }, [activeId]);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const fetchSessions = async () => {
    const r = await api.get("/api/chat/sessions");
    setSessions(r.data);
  };

  const fetchMessages = async id => {
    const r = await api.get(`/api/chat/sessions/${id}/messages`);
    setMessages(r.data);
  };

  const newSession = async () => {
    const r = await api.post("/api/chat/sessions");
    setSessions(s => [r.data, ...s]);
    setActiveId(r.data.id);
    setMessages([]);
  };

  const deleteSession = async id => {
    await api.delete(`/api/chat/sessions/${id}`);
    setSessions(s => s.filter(x => x.id !== id));
    if (activeId === id) { setActiveId(null); setMessages([]); }
  };

  const send = async e => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    if (!activeId) { await newSession(); return; }

    const question = input.trim();
    setInput("");
    setMessages(m => [...m,
      { id: Date.now(), role: "user",      content: question, sources: [] },
      { id: Date.now()+1, role: "assistant", content: "…",   sources: [], loading: true },
    ]);
    setLoading(true);

    try {
      const r = await api.post(`/api/chat/sessions/${activeId}/ask`, { question });
      setMessages(m => {
        const copy = [...m];
        copy[copy.length - 1] = {
          id: r.data.message_id, role: "assistant",
          content: r.data.answer, sources: r.data.sources,
          api_calls: r.data.api_calls || [], loading: false,
        };
        return copy;
      });
      fetchSessions();
    } catch {
      setMessages(m => {
        const copy = [...m];
        copy[copy.length - 1] = {
          ...copy[copy.length - 1],
          content: "Erreur lors de la génération de la réponse.", loading: false,
        };
        return copy;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={S.app}>
      {/* Sidebar */}
      <aside style={S.sidebar}>
        <div style={S.sideTop}>
          <div style={S.brand}>🤖 <span>ChatEntreprise</span></div>
          <button onClick={newSession} style={S.newBtn}>+ Nouvelle conversation</button>
        </div>

        <div style={S.sessionList}>
          {sessions.map(s => (
            <div key={s.id}
              style={{ ...S.sessionItem, ...(activeId === s.id ? S.sessionActive : {}) }}
              onClick={() => setActiveId(s.id)}
            >
              <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis",
                whiteSpace: "nowrap", fontSize: ".875rem" }}>{s.title}</span>
              <button onClick={e => { e.stopPropagation(); deleteSession(s.id); }}
                style={S.delBtn}>✕</button>
            </div>
          ))}
          {sessions.length === 0 &&
            <p style={{ color: "var(--text2)", fontSize: ".8rem", padding: ".5rem 1rem" }}>
              Aucune conversation
            </p>}
        </div>

        <div style={S.sideBottom}>
          {user?.role === "admin" &&
            <button onClick={() => navigate("/admin")} style={S.adminBtn}>⚙ Administration</button>}
          <div style={S.userRow}>
            <span style={{ fontSize: ".85rem" }}>{user?.username}</span>
            <button onClick={logout} style={S.logoutBtn}>Déconnexion</button>
          </div>
        </div>
      </aside>

      {/* Main chat */}
      <main style={S.main}>
        {!activeId ? (
          <div style={S.empty}>
            <p style={{ fontSize: "3rem" }}>💬</p>
            <h2>Comment puis-je vous aider ?</h2>
            <p style={{ color: "var(--text2)", marginTop: ".5rem" }}>
              Cliquez sur <strong>+ Nouvelle conversation</strong> pour commencer.
            </p>
          </div>
        ) : (
          <>
            <div style={S.messages}>
              {messages.map(m => (
                <div key={m.id} style={{ ...S.msgRow, justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
                  <div style={{ ...S.bubble, ...(m.role === "user" ? S.bubbleUser : S.bubbleBot) }}>
                    {m.loading ? <span style={S.typing}>●●●</span>
                      : <ReactMarkdown>{m.content}</ReactMarkdown>}
                    {m.api_calls?.length > 0 && (
                      <div style={S.apiCallsBox}>
                        <span style={S.apiCallsLabel}>🔌 Données système consultées</span>
                        {m.api_calls.map((c, i) => (
                          <span key={i} style={S.apiCallTag}>
                            {c.classe}
                            {c.recherche && <em> « {c.recherche} »</em>}
                            {" "}— {c.nb_lignes} ligne{c.nb_lignes !== 1 ? "s" : ""}
                          </span>
                        ))}
                      </div>
                    )}
                    {m.sources?.length > 0 && (
                      <div style={S.sources}>
                        <strong>Sources :</strong>
                        {m.sources.map((src, i) => (
                          <span key={i} style={S.sourceTag}>
                            📄 {src.file} <em>({Math.round(src.score * 100)}%)</em>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div ref={bottomRef} />
            </div>

            <form onSubmit={send} style={S.inputRow}>
              <input
                value={input} onChange={e => setInput(e.target.value)}
                placeholder="Posez votre question…" style={S.textInput} disabled={loading}
              />
              <button type="submit" disabled={loading || !input.trim()} style={S.sendBtn}>
                {loading ? "…" : "Envoyer"}
              </button>
            </form>
          </>
        )}
      </main>
    </div>
  );
}

const S = {
  app:      { display: "flex", height: "100vh", overflow: "hidden" },
  sidebar:  { width: 260, background: "var(--bg2)", borderRight: "1px solid var(--border)",
              display: "flex", flexDirection: "column" },
  sideTop:  { padding: "1rem", borderBottom: "1px solid var(--border)" },
  brand:    { display: "flex", alignItems: "center", gap: ".5rem", fontWeight: 700,
              fontSize: "1.1rem", marginBottom: "1rem" },
  newBtn:   { width: "100%", background: "var(--accent)", color: "#fff",
              padding: ".55rem", fontWeight: 600, fontSize: ".875rem" },
  sessionList: { flex: 1, overflowY: "auto", padding: ".5rem 0" },
  sessionItem: { display: "flex", alignItems: "center", gap: ".5rem",
                 padding: ".5rem 1rem", cursor: "pointer", borderRadius: 6, margin: "0 .5rem",
                 transition: "background .15s" },
  sessionActive: { background: "var(--surface)" },
  delBtn:   { background: "transparent", color: "var(--text2)", padding: "0 .25rem",
              fontSize: ".75rem", borderRadius: 4 },
  sideBottom: { padding: "1rem", borderTop: "1px solid var(--border)" },
  adminBtn: { width: "100%", background: "var(--bg3)", color: "var(--text)",
              border: "1px solid var(--border)", padding: ".45rem", marginBottom: ".75rem",
              fontSize: ".8rem" },
  userRow:  { display: "flex", justifyContent: "space-between", alignItems: "center" },
  logoutBtn: { background: "transparent", color: "var(--text2)", fontSize: ".8rem",
               padding: ".25rem .5rem", border: "1px solid var(--border)", borderRadius: 6 },
  main:     { flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" },
  empty:    { flex: 1, display: "flex", flexDirection: "column", alignItems: "center",
              justifyContent: "center", textAlign: "center", gap: ".5rem" },
  messages: { flex: 1, overflowY: "auto", padding: "1.5rem", display: "flex",
              flexDirection: "column", gap: "1rem" },
  msgRow:   { display: "flex" },
  bubble:   { maxWidth: "72%", padding: ".75rem 1rem", borderRadius: 12,
              fontSize: ".925rem", lineHeight: 1.6 },
  bubbleUser: { background: "var(--accent2)", color: "#fff", borderBottomRightRadius: 4 },
  bubbleBot:  { background: "var(--bg2)", border: "1px solid var(--border)",
                borderBottomLeftRadius: 4 },
  typing:   { letterSpacing: 4, color: "var(--text2)" },
  apiCallsBox: { marginTop: ".5rem", paddingTop: ".5rem", borderTop: "1px solid var(--border)",
                 fontSize: ".78rem", display: "flex", flexWrap: "wrap",
                 gap: ".35rem", alignItems: "center" },
  apiCallsLabel: { color: "#4caf7d", fontWeight: 600, marginRight: ".25rem" },
  apiCallTag: { background: "#0d2b1a", border: "1px solid #2a6644",
                color: "#6fdd9e", borderRadius: 4, padding: ".1rem .45rem" },
  sources:  { marginTop: ".5rem", paddingTop: ".5rem", borderTop: "1px solid var(--border)",
              fontSize: ".78rem", color: "var(--text2)", display: "flex",
              flexWrap: "wrap", gap: ".35rem", alignItems: "center" },
  sourceTag: { background: "var(--bg3)", border: "1px solid var(--border)",
               borderRadius: 4, padding: ".1rem .4rem" },
  inputRow: { display: "flex", gap: ".75rem", padding: "1rem 1.5rem",
              borderTop: "1px solid var(--border)", background: "var(--bg2)" },
  textInput: { flex: 1, padding: ".65rem 1rem", fontSize: "1rem", borderRadius: 8 },
  sendBtn:  { background: "var(--accent)", color: "#fff", padding: ".65rem 1.25rem",
              fontWeight: 600, minWidth: 90 },
};
