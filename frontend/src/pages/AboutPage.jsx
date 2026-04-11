export default function AboutPage() {
  return (
    <div className="about-page">
      <div className="about-hero">
        <h1>About <span className="brand-ai">HealthMate AI</span></h1>
        <p className="about-subtitle">AI-powered prescription reading for safer medication management</p>
      </div>

      <div className="about-grid">
        <div className="about-card glass">
          <span className="about-icon">🎯</span>
          <h3>Our Mission</h3>
          <p>
            HealthMate AI helps patients understand their prescriptions by using advanced
            OCR and NLP technology to extract medicine names, dosages, and frequencies
            from doctor-written prescriptions.
          </p>
        </div>

        <div className="about-card glass">
          <span className="about-icon">🧠</span>
          <h3>How It Works</h3>
          <p>
            Upload a prescription image and our AI engine performs multi-pass OCR with
            intelligent text extraction. It identifies 125+ common medicines, detects
            dosages, checks for safety warnings, and flags potential issues.
          </p>
        </div>

        <div className="about-card glass">
          <span className="about-icon">🛡️</span>
          <h3>Safety First</h3>
          <p>
            Our safety engine checks for unusual dosages, duplicate medications,
            similar-sounding drug names, and missing prescription information to help
            you stay safe.
          </p>
        </div>

        <div className="about-card glass">
          <span className="about-icon">🔬</span>
          <h3>Technology</h3>
          <p>
            Built with FastAPI, Tesseract OCR, OpenCV, and React. Uses advanced image
            preprocessing including auto-rotation, deskewing, and adaptive thresholding
            for optimal text extraction.
          </p>
        </div>
      </div>

      <div className="about-features glass">
        <h2>Key Features</h2>
        <div className="features-list">
          <div className="feature-item">
            <span>📷</span>
            <div>
              <h4>Smart Image Processing</h4>
              <p>Auto-rotation, deskewing, noise removal, and contrast enhancement</p>
            </div>
          </div>
          <div className="feature-item">
            <span>💊</span>
            <div>
              <h4>125+ Medicine Database</h4>
              <p>Comprehensive whitelist with brand-to-generic name mapping</p>
            </div>
          </div>
          <div className="feature-item">
            <span>⚠️</span>
            <div>
              <h4>Safety Warnings</h4>
              <p>Dosage checks, duplicate detection, and confusion-prone name alerts</p>
            </div>
          </div>
          <div className="feature-item">
            <span>📜</span>
            <div>
              <h4>Scan History</h4>
              <p>Keep track of all your previous prescription scans</p>
            </div>
          </div>
          <div className="feature-item">
            <span>🔐</span>
            <div>
              <h4>Secure Authentication</h4>
              <p>JWT-based auth with password hashing to protect your data</p>
            </div>
          </div>
          <div className="feature-item">
            <span>📱</span>
            <div>
              <h4>PWA Support</h4>
              <p>Install as a mobile app for quick access on any device</p>
            </div>
          </div>
        </div>
      </div>

      <div className="about-disclaimer glass">
        <h3>⚕️ Disclaimer</h3>
        <p>
          HealthMate AI is a tool to assist in reading prescriptions. It is <strong>not a substitute
          for professional medical advice</strong>. Always consult your doctor or pharmacist for
          medication-related decisions. AI extraction may contain errors — verify all results
          with your healthcare provider.
        </p>
      </div>

      <div className="about-footer">
        <p>Built with ❤️ by <strong>Rauf</strong></p>
        <p className="tech-stack">FastAPI • Tesseract OCR • OpenCV • React • Vite</p>
      </div>
    </div>
  );
}
