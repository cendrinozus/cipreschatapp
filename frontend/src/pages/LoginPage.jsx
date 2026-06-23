import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const BROWN      = "#2a0e04";
const TERRACOTTA = "#c0622a";

function CipresLogo() {
  return (
    <svg width="76" height="76" viewBox="0 0 76 76" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="38" cy="38" r="36" stroke="white" strokeWidth="2.5" fill="rgba(255,255,255,0.07)" />
      {/* trunk */}
      <rect x="35.5" y="46" width="5" height="11" fill="white" rx="1.5" />
      {/* tree layers bottom → top */}
      <polygon points="38,42 25,54 51,54" fill="white" />
      <polygon points="38,33 26,47 50,47" fill="white" />
      <polygon points="38,24 28,40 48,40" fill="white" />
      {/* CIPRES arc text replaced by simple baseline text */}
      <text x="38" y="68" textAnchor="middle" fill="white"
            fontSize="7" fontFamily="Georgia, serif" letterSpacing="3" fontWeight="bold">
        CIPRES
      </text>
    </svg>
  );
}

export default function LoginPage() {
  const { login }   = useAuth();
  const navigate    = useNavigate();
  const [form,  setForm]  = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [busy,  setBusy]  = useState(false);

  const handle = async e => {
    e.preventDefault();
    setBusy(true); setError("");
    try {
      await login(form.email, form.password);
      navigate("/");
    } catch {
      setError("Email ou mot de passe incorrect.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={S.page}>
      {/* Logo + titre au-dessus de la carte */}
      <div style={S.hero}>
        <CipresLogo />
        <h1 style={S.appName}>CIPRESChat</h1>
        <p style={S.appSub}>ASSISTANT CONVERSATIONNEL — CIPRES</p>
      </div>

      {/* Carte de connexion */}
      <div style={S.card}>
        <div style={S.cardHeader}>CONNEXION</div>

        <div style={S.cardBody}>
          {error && <div style={S.errorBox}>{error}</div>}

          <form onSubmit={handle} style={S.form}>
            <div style={S.field}>
              <label style={S.label}>Adresse email</label>
              <input
                className="login-input"
                type="email"
                placeholder="admin@lacipres.org"
                required
                value={form.email}
                onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
              />
            </div>

            <div style={S.field}>
              <label style={S.label}>Mot de passe</label>
              <input
                className="login-input"
                type="password"
                placeholder="••••••••"
                required
                value={form.password}
                onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
              />
            </div>

            <button type="submit" disabled={busy} style={S.btn}>
              {busy ? "Connexion…" : "Se connecter"}
            </button>
          </form>

          <div style={S.demoBox}>
            <p style={S.demoTitle}>COMPTE DÉMO</p>
            <p style={S.demoCreds}>admin@lacipres.org &nbsp;/&nbsp; 1234</p>
          </div>
        </div>
      </div>
    </div>
  );
}

const S = {
  page: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    background: BROWN,
    padding: "2rem 1rem",
    fontFamily: "'Inter', system-ui, sans-serif",
  },
  hero: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "0.5rem",
    marginBottom: "1.75rem",
  },
  appName: {
    color: "#ffffff",
    fontSize: "2.4rem",
    fontWeight: 700,
    fontFamily: "Georgia, 'Times New Roman', serif",
    marginTop: "0.5rem",
    letterSpacing: "-0.01em",
  },
  appSub: {
    color: TERRACOTTA,
    fontSize: "0.72rem",
    fontWeight: 600,
    letterSpacing: "0.18em",
    textTransform: "uppercase",
  },
  card: {
    width: "100%",
    maxWidth: 460,
    borderRadius: 16,
    overflow: "hidden",
    boxShadow: "0 12px 40px rgba(0,0,0,0.55)",
    background: "#ffffff",
  },
  cardHeader: {
    background: TERRACOTTA,
    color: "#ffffff",
    fontWeight: 700,
    fontSize: "0.82rem",
    letterSpacing: "0.12em",
    padding: "0.95rem 1.5rem",
  },
  cardBody: {
    padding: "1.75rem 2rem 2.25rem",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "1.25rem",
  },
  field: {
    display: "flex",
    flexDirection: "column",
    gap: "0.45rem",
  },
  label: {
    color: "#374151",
    fontSize: "0.88rem",
    fontWeight: 500,
    fontFamily: "inherit",
  },
  btn: {
    width: "100%",
    padding: "0.85rem",
    background: TERRACOTTA,
    color: "#ffffff",
    fontWeight: 700,
    fontSize: "1rem",
    border: "none",
    borderRadius: 10,
    cursor: "pointer",
    marginTop: "0.35rem",
    letterSpacing: "0.02em",
    fontFamily: "inherit",
    transition: "background 0.15s",
  },
  demoBox: {
    marginTop: "1.5rem",
    background: "#fdf0e8",
    border: "1px solid #e8c9b0",
    borderRadius: 10,
    padding: "0.8rem 1.1rem",
  },
  demoTitle: {
    color: TERRACOTTA,
    fontWeight: 700,
    fontSize: "0.78rem",
    letterSpacing: "0.1em",
    textTransform: "uppercase",
    marginBottom: "0.3rem",
  },
  demoCreds: {
    color: "#6b3a1f",
    fontSize: "0.88rem",
  },
  errorBox: {
    background: "#fef2f2",
    color: "#b91c1c",
    border: "1px solid #fca5a5",
    borderRadius: 8,
    padding: "0.6rem 0.9rem",
    fontSize: "0.875rem",
    marginBottom: "0.5rem",
  },
};
