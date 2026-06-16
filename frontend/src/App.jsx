import { useState } from "react";
import AuthModal    from "./components/AuthModal";
import ScanSection  from "./components/ScanSection";
import HistorySection from "./components/HistorySection";
import AboutSection from "./components/AboutSection";
import AdminPanel   from "./components/AdminPanel";

export default function App() {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("hm_user")); } catch { return null; }
  });
  const [showAuth,  setShowAuth]  = useState(false);
  const [showAdmin, setShowAdmin] = useState(false);

  const loginUser = (u, tok) => {
    localStorage.setItem("hm_token", tok);
    localStorage.setItem("hm_user", JSON.stringify(u));
    setUser(u); setShowAuth(false);
  };
  const logout = () => {
    localStorage.removeItem("hm_token");
    localStorage.removeItem("hm_user");
    setUser(null); setShowAdmin(false);
  };

  return (
    <>
      {/* ── NAVBAR ── */}
      <nav className="navbar">
        <div className="nav-inner">
          <span className="nav-brand">healthmate</span>

          <div className="nav-center">
            <a href="#scan">Scan</a>
            {user && <a href="#history">History</a>}
            <a href="#about">How it works</a>
            <a href="#about">FAQ</a>
            {user?.role === "admin" && (
              <button className="nav-link-btn" onClick={() => setShowAdmin(v => !v)}>Admin</button>
            )}
          </div>

          <div className="nav-right">
            {user ? (
              <>
                <span className="user-chip">
                  <span className="user-av">{user.name?.[0]?.toUpperCase()}</span>
                  <span>{user.name}</span>
                </span>
                <button className="btn-auth" onClick={logout}>Sign out</button>
              </>
            ) : (
              <button className="btn-auth" onClick={() => setShowAuth(true)}>Sign up / Log in</button>
            )}
          </div>
        </div>
      </nav>

      {/* ── MODALS ── */}
      {showAuth  && <AuthModal onClose={() => setShowAuth(false)} onLogin={loginUser} />}
      {showAdmin && user?.role === "admin" && (
        <div className="overlay" onClick={() => setShowAdmin(false)}>
          <div onClick={e => e.stopPropagation()}>
            <AdminPanel onClose={() => setShowAdmin(false)} />
          </div>
        </div>
      )}

      {/* ── PAGE TITLE ── */}
      <div className="page-title" id="top">
        <h1>Doctor Prescription Reader</h1>
        <p>Upload a prescription image — instantly extract medicines, dosages &amp; safety warnings.</p>
      </div>

      {/* ── SCAN ── */}
      <div id="scan">
        <ScanSection user={user} onNeedAuth={() => setShowAuth(true)} />
      </div>

      {/* ── HISTORY ── */}
      {user && <div id="history"><HistorySection /></div>}

      {/* ── ABOUT ── */}
      <div id="about"><AboutSection /></div>

      {/* ── FOOTER ── */}
      <footer className="footer">
        <div className="footer-in">
          <span className="footer-brand">healthmate</span>
          <div className="footer-chips">
            {["FastAPI","Tesseract OCR","OpenCV","React","Vite"].map(t => <span key={t}>{t}</span>)}
          </div>
          <p className="footer-copy">Built by <strong>Rauf</strong> · {new Date().getFullYear()}</p>
        </div>
      </footer>
    </>
  );
}
