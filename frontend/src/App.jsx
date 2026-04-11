import { useState, useEffect } from "react";
import AuthModal from "./components/AuthModal";
import ScanSection from "./components/ScanSection";
import HistorySection from "./components/HistorySection";
import AboutSection from "./components/AboutSection";
import AdminPanel from "./components/AdminPanel";

export default function App() {
  const [user, setUser] = useState(() => {
    const s = localStorage.getItem("hm_user");
    return s ? JSON.parse(s) : null;
  });
  const [showAuth, setShowAuth] = useState(false);
  const [showAdmin, setShowAdmin] = useState(false);

  const loginUser = (u, token) => {
    localStorage.setItem("hm_token", token);
    localStorage.setItem("hm_user", JSON.stringify(u));
    setUser(u);
    setShowAuth(false);
  };

  const logout = () => {
    localStorage.removeItem("hm_token");
    localStorage.removeItem("hm_user");
    setUser(null);
    setShowAdmin(false);
  };

  return (
    <div className="app">
      {/* ── Navbar ─────────────────────── */}
      <nav className="navbar">
        <div className="nav-inner">
          <a href="#top" className="nav-brand">
            <span className="brand-pill">💊</span>
            HealthMate <span className="ai">AI</span>
          </a>

          <div className="nav-links">
            <a href="#scan">Scan</a>
            {user && <a href="#history">History</a>}
            <a href="#about">About</a>
            {user?.role === "admin" && (
              <button className="nav-link-btn" onClick={() => setShowAdmin(!showAdmin)}>
                Admin
              </button>
            )}
          </div>

          <div className="nav-right">
            {user ? (
              <>
                <span className="user-chip">
                  <span className="user-avatar">{user.name?.[0]?.toUpperCase()}</span>
                  {user.name}
                </span>
                <button className="btn-outline btn-sm" onClick={logout}>Logout</button>
              </>
            ) : (
              <button className="btn-accent btn-sm" onClick={() => setShowAuth(true)}>
                Sign In
              </button>
            )}
          </div>
        </div>
      </nav>

      {/* ── Auth Modal (optional) ─────── */}
      {showAuth && <AuthModal onClose={() => setShowAuth(false)} onLogin={loginUser} />}

      {/* ── Admin Overlay ─────────────── */}
      {showAdmin && user?.role === "admin" && (
        <AdminPanel onClose={() => setShowAdmin(false)} />
      )}

      {/* ── Hero ──────────────────────── */}
      <header id="top" className="hero">
        <div className="hero-inner">
          <h1>Read Any Prescription<br /><span className="hero-gradient">With AI Precision</span></h1>
          <p className="hero-sub">
            Upload a prescription image — we extract medicines, dosages, and safety warnings instantly.
            {!user && " Sign in to save your scan history."}
          </p>
          <a href="#scan" className="btn-accent btn-lg">Start Scanning ↓</a>
        </div>
      </header>

      {/* ── Sections ──────────────────── */}
      <section id="scan">
        <ScanSection user={user} onNeedAuth={() => setShowAuth(true)} />
      </section>

      {user && (
        <section id="history">
          <HistorySection />
        </section>
      )}

      <section id="about">
        <AboutSection />
      </section>

      {/* ── Footer ────────────────────── */}
      <footer className="footer">
        <p>Built by <strong>Rauf</strong> &nbsp;·&nbsp; FastAPI · Tesseract OCR · OpenCV · React · Vite</p>
      </footer>
    </div>
  );
}
