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
  const [activeTab, setActiveTab] = useState("scan");

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
            <div className="brand-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2L12 22M2 12L22 12" />
                <rect x="6" y="6" width="12" height="12" rx="2" />
              </svg>
            </div>
            HealthMate <span className="ai">AI</span>
          </a>

          <div className="nav-links">
            <a href="#top" className={activeTab === "home" ? "active" : ""} onClick={() => setActiveTab("home")}>Home</a>
            <a href="#scan" className={activeTab === "scan" ? "active" : ""} onClick={() => setActiveTab("scan")}>Scan</a>
            {user && <a href="#history" className={activeTab === "history" ? "active" : ""} onClick={() => setActiveTab("history")}>History</a>}
            <a href="#about" className={activeTab === "about" ? "active" : ""} onClick={() => setActiveTab("about")}>About</a>
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
                  <span className="user-name">{user.name}</span>
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

      {/* ── Auth Modal ─────────────────── */}
      {showAuth && <AuthModal onClose={() => setShowAuth(false)} onLogin={loginUser} />}

      {/* ── Admin Overlay ─────────────── */}
      {showAdmin && user?.role === "admin" && (
        <AdminPanel onClose={() => setShowAdmin(false)} />
      )}

      {/* ── Hero Section (Split Layout) ── */}
      <header id="top" className="hero">
        <div className="hero-inner">
          <div className="hero-left">
            <div className="hero-badge fade-in-up">
              <span className="pulse-dot"></span>
              AI-Powered Prescription Reader
            </div>
            <h1 className="fade-in-up delay-1">
              Read Any Prescription
              <br />
              <span className="hero-gradient">With AI Precision</span>
            </h1>
            <p className="hero-sub fade-in-up delay-2">
              Upload a prescription image — we extract medicines, dosages, and safety warnings instantly using advanced OCR and NLP.
              {!user && " Sign in to save your scan history."}
            </p>
            <div className="hero-actions fade-in-up delay-3">
              <a href="#scan" className="btn-accent btn-lg">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>
                Start Scanning
              </a>
              <a href="#about" className="btn-outline btn-lg">Learn More</a>
            </div>
            <div className="hero-stats fade-in-up delay-4">
              <div className="hero-stat">
                <strong>151+</strong>
                <span>Medicines</span>
              </div>
              <div className="hero-stat-divider"></div>
              <div className="hero-stat">
                <strong>6</strong>
                <span>Safety Checks</span>
              </div>
              <div className="hero-stat-divider"></div>
              <div className="hero-stat">
                <strong>31+</strong>
                <span>Pakistani Brands</span>
              </div>
            </div>
          </div>
          <div className="hero-right fade-in-up delay-2">
            <div className="hero-visual">
              {/* Animated pill cards */}
              <div className="floating-card fc-1">
                <span className="fc-icon">💊</span>
                <div>
                  <strong>Paracetamol</strong>
                  <small>500 mg · Twice daily</small>
                </div>
              </div>
              <div className="floating-card fc-2">
                <span className="fc-icon">🛡️</span>
                <div>
                  <strong>Safety Check</strong>
                  <small>Dosage verified ✓</small>
                </div>
              </div>
              <div className="floating-card fc-3">
                <span className="fc-icon">🔬</span>
                <div>
                  <strong>OCR Confidence</strong>
                  <small>95% accuracy</small>
                </div>
              </div>
              {/* Center glow orb */}
              <div className="hero-orb"></div>
              <div className="hero-orb hero-orb-2"></div>
              {/* Prescription outline */}
              <div className="rx-outline">
                <div className="rx-line"></div>
                <div className="rx-line short"></div>
                <div className="rx-line"></div>
                <div className="rx-line med"></div>
                <div className="rx-line short"></div>
              </div>
            </div>
          </div>
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
        <div className="footer-inner">
          <div className="footer-brand">
            <strong>HealthMate AI</strong>
            <p>AI-powered prescription reader for safer medication.</p>
          </div>
          <div className="footer-tech">
            <span>FastAPI</span>
            <span>Tesseract OCR</span>
            <span>OpenCV</span>
            <span>React</span>
            <span>Vite</span>
          </div>
          <p className="footer-copy">Built by <strong>Rauf</strong> · {new Date().getFullYear()}</p>
        </div>
      </footer>
    </div>
  );
}
