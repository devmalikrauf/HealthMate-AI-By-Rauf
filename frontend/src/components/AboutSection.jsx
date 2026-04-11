export default function AboutSection() {
  return (
    <div className="section-wrap about-section">
      <div className="section-header center">
        <h2>About HealthMate AI</h2>
        <p>AI-powered prescription reading for safer medication management</p>
      </div>

      <div className="about-cards">
        <div className="card about-item">
          <div className="about-icon mission">🎯</div>
          <h4>Our Mission</h4>
          <p>Help patients understand prescriptions using advanced OCR and NLP to extract medicine names, dosages, and frequencies.</p>
        </div>
        <div className="card about-item">
          <div className="about-icon brain">🧠</div>
          <h4>How It Works</h4>
          <p>Multi-pass OCR with intelligent preprocessing identifies 150+ medicines, detects dosages, and flags safety issues.</p>
        </div>
        <div className="card about-item">
          <div className="about-icon shield">🛡️</div>
          <h4>Safety First</h4>
          <p>Checks for unusual dosages, duplicate medications, similar-sounding drug names, and missing information.</p>
        </div>
        <div className="card about-item">
          <div className="about-icon tech">🔬</div>
          <h4>Technology</h4>
          <p>FastAPI, Tesseract OCR, OpenCV for backend. React + Vite PWA for a fast, installable frontend.</p>
        </div>
      </div>

      <div className="card features-block">
        <h3>Key Features</h3>
        <div className="features-grid">
          <div className="feat"><span>📷</span><div><h5>Smart Image Processing</h5><p>Auto-rotation, deskewing, noise removal, contrast enhancement</p></div></div>
          <div className="feat"><span>💊</span><div><h5>150+ Medicine Database</h5><p>Comprehensive whitelist with brand-to-generic mapping for Pakistani medicines</p></div></div>
          <div className="feat"><span>⚠️</span><div><h5>Safety Warnings</h5><p>Dosage checks, duplicate detection, allergy alerts, side effects info</p></div></div>
          <div className="feat"><span>📜</span><div><h5>Scan History</h5><p>Track all your previous prescription scans with detailed results</p></div></div>
          <div className="feat"><span>🔐</span><div><h5>Optional Sign In</h5><p>Create an account to save history — or scan as guest</p></div></div>
          <div className="feat"><span>📱</span><div><h5>PWA Support</h5><p>Install as a mobile app for quick access anywhere</p></div></div>
        </div>
      </div>

      <div className="card disclaimer">
        <h4>⚕️ Disclaimer</h4>
        <p>
          HealthMate AI is <strong>not a substitute for professional medical advice</strong>.
          Always consult your doctor or pharmacist. AI extraction may contain errors — verify all results with your healthcare provider.
        </p>
      </div>
    </div>
  );
}
