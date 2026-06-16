/* ─── icons ─── */
const IcoMission = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>;
const IcoBrain    = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.96-.44 2.5 2.5 0 010-3.12 3 3 0 010-4.88 2.5 2.5 0 010-3.12A2.5 2.5 0 019.5 2zM14.5 2A2.5 2.5 0 0012 4.5v15a2.5 2.5 0 004.96-.44 2.5 2.5 0 000-3.12 3 3 0 000-4.88 2.5 2.5 0 000-3.12A2.5 2.5 0 0014.5 2z"/></svg>;
const IcoShield   = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>;
const IcoTech     = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M3 12h3M18 12h3M12 3v3M12 18v3M5.6 5.6l2.2 2.2M16.2 16.2l2.2 2.2M5.6 18.2l2.2-2.2M16.2 7.8l2.2-2.2"/></svg>;

const IcoCamera   = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>;
const IcoPill     = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4.5 16.5c-1.5-1.5-2.5-3.5-2.5-6s1-4.5 2.5-6 3.5-2.5 6-2.5 4.5 1 6 2.5 2.5 3.5 2.5 6-1 4.5-2.5 6-3.5 2.5-6 2.5-4.5-1-6-2.5z"/><line x1="9" y1="9" x2="15" y2="15"/></svg>;
const IcoAlert    = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>;
const IcoHistory  = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 8v4l3 3"/><circle cx="12" cy="12" r="10"/><path d="M3.05 11a9 9 0 11.5 4m-.5 5v-5h5"/></svg>;
const IcoKey      = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 11-7.778 7.778 5.5 5.5 0 017.777-7.777zm0 0L15.5 7.5m0 0l3 3M15.5 7.5L14 6"/></svg>;
const IcoPhone    = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>;

export default function AboutSection() {
  return (
    <div className="section-wrap about-section">
      <div className="section-header center">
        <h2>About HealthMate AI</h2>
        <p>AI-powered prescription reading for safer medication management</p>
      </div>

      <div className="about-cards">
        <div className="about-item">
          <div className="about-icon"><IcoMission/></div>
          <h4>Our Mission</h4>
          <p>Help patients understand prescriptions using advanced OCR and NLP to extract medicine names, dosages, and frequencies.</p>
        </div>
        <div className="about-item">
          <div className="about-icon"><IcoBrain/></div>
          <h4>How It Works</h4>
          <p>Multi-pass OCR with intelligent preprocessing identifies 150+ medicines, detects dosages, and flags safety issues.</p>
        </div>
        <div className="about-item">
          <div className="about-icon"><IcoShield/></div>
          <h4>Safety First</h4>
          <p>Checks for unusual dosages, duplicate medications, similar-sounding drug names, and missing information.</p>
        </div>
        <div className="about-item">
          <div className="about-icon"><IcoTech/></div>
          <h4>Technology</h4>
          <p>FastAPI, Tesseract OCR, OpenCV for backend. React + Vite PWA for a fast, installable frontend.</p>
        </div>
      </div>

      <div className="features-block">
        <h3>Key Features</h3>
        <div className="features-grid">
          <div className="feat">
            <div className="feat-icon"><IcoCamera /></div>
            <div>
              <h5>Smart Image Processing</h5>
              <p>Auto-rotation, deskewing, noise removal, contrast enhancement</p>
            </div>
          </div>
          <div className="feat">
            <div className="feat-icon"><IcoPill /></div>
            <div>
              <h5>150+ Medicine Database</h5>
              <p>Comprehensive whitelist with brand-to-generic mapping for Pakistani medicines</p>
            </div>
          </div>
          <div className="feat">
            <div className="feat-icon"><IcoAlert /></div>
            <div>
              <h5>Safety Warnings</h5>
              <p>Dosage checks, duplicate detection, allergy alerts, side effects info</p>
            </div>
          </div>
          <div className="feat">
            <div className="feat-icon"><IcoHistory /></div>
            <div>
              <h5>Scan History</h5>
              <p>Track all your previous prescription scans with detailed results</p>
            </div>
          </div>
          <div className="feat">
            <div className="feat-icon"><IcoKey /></div>
            <div>
              <h5>Optional Sign In</h5>
              <p>Create an account to save history — or scan as guest</p>
            </div>
          </div>
          <div className="feat">
            <div className="feat-icon"><IcoPhone /></div>
            <div>
              <h5>PWA Support</h5>
              <p>Install as a mobile app for quick access anywhere</p>
            </div>
          </div>
        </div>
      </div>

      <div className="disclaimer">
        <div className="disclaimer-icon">
          <IcoAlert />
        </div>
        <div className="disclaimer-content">
          <h4>⚕️ Medical Disclaimer</h4>
          <p>
            HealthMate AI is <strong>not a substitute for professional medical advice</strong>.
            Always consult your doctor or pharmacist. AI extraction may contain errors — verify all results with your healthcare provider.
          </p>
        </div>
      </div>
    </div>
  );
}
