import { useState, useRef, useCallback } from "react";
import { scan as scanApi } from "../api";

export default function ScanPage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef();

  const handleFile = useCallback((f) => {
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError("");
  }, []);

  const onDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]);
  };

  const analyze = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const res = await scanApi.analyze(file);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError("");
  };

  return (
    <div className="scan-page">
      <div className="page-header">
        <h1>📋 Scan Prescription</h1>
        <p>Upload a prescription image to extract medicine details and safety warnings</p>
      </div>

      {!result ? (
        <div className="scan-upload-section">
          <div
            className={`drop-zone glass ${dragActive ? "drag-active" : ""} ${preview ? "has-preview" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={() => setDragActive(false)}
            onDrop={onDrop}
            onClick={() => !preview && inputRef.current?.click()}
          >
            {preview ? (
              <div className="preview-container">
                <img src={preview} alt="Preview" className="preview-image" />
                <div className="preview-overlay">
                  <button className="btn btn-ghost" onClick={(e) => { e.stopPropagation(); reset(); }}>
                    ✕ Remove
                  </button>
                </div>
              </div>
            ) : (
              <div className="drop-content">
                <span className="drop-icon">📷</span>
                <h3>Drop prescription image here</h3>
                <p>or click to browse files</p>
                <p className="drop-hint">Supports JPG, PNG, BMP, TIFF, WebP</p>
              </div>
            )}
            <input
              ref={inputRef}
              type="file"
              accept="image/*"
              hidden
              onChange={(e) => handleFile(e.target.files?.[0])}
            />
          </div>

          {file && (
            <button
              className="btn btn-primary btn-lg analyze-btn"
              onClick={analyze}
              disabled={loading}
            >
              {loading ? (
                <><span className="spinner-sm" /> Analyzing...</>
              ) : (
                "🔍 Analyze Prescription"
              )}
            </button>
          )}

          {error && <div className="alert alert-error">{error}</div>}
        </div>
      ) : (
        <div className="scan-results">
          <div className="results-header">
            <div className="confidence-badge">
              <span className="confidence-label">Confidence</span>
              <span className={`confidence-value ${result.overall_confidence >= 0.7 ? "high" : result.overall_confidence >= 0.4 ? "med" : "low"}`}>
                {Math.round(result.overall_confidence * 100)}%
              </span>
            </div>
            <button className="btn btn-primary" onClick={reset}>New Scan</button>
          </div>

          {result.warnings?.length > 0 && (
            <div className="warnings-section glass">
              <h2>⚠️ Safety Warnings</h2>
              <div className="warnings-list">
                {result.warnings.map((w, i) => (
                  <div key={i} className={`warning-item severity-${w.severity}`}>
                    <span className="warning-icon">
                      {w.severity === "high" ? "🔴" : w.severity === "medium" ? "🟡" : "🔵"}
                    </span>
                    <div>
                      <strong>{w.type}</strong>
                      <p>{w.message}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="medicines-section">
            <h2>💊 Detected Medicines ({result.medicines?.length || 0})</h2>
            {result.medicines?.length > 0 ? (
              <div className="medicines-grid">
                {result.medicines.map((m, i) => (
                  <div key={i} className="medicine-card glass">
                    <div className="med-header">
                      <h3>{m.name}</h3>
                      <span className={`conf-pill ${m.confidence >= 0.8 ? "high" : m.confidence >= 0.5 ? "med" : "low"}`}>
                        {Math.round(m.confidence * 100)}%
                      </span>
                    </div>
                    <div className="med-details">
                      {m.dosage && <div className="med-tag"><span>💉</span> {m.dosage}</div>}
                      {m.frequency && <div className="med-tag"><span>🕐</span> {m.frequency}</div>}
                      {m.duration && <div className="med-tag"><span>📅</span> {m.duration}</div>}
                      {m.instructions && <div className="med-tag"><span>📝</span> {m.instructions}</div>}
                      {m.generic_name && m.generic_name !== m.name && (
                        <div className="med-tag generic"><span>🧬</span> {m.generic_name}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state glass">
                <p>No medicines detected. Try a clearer image.</p>
              </div>
            )}
          </div>

          {result.raw_text && (
            <details className="raw-text-section glass">
              <summary>📄 Raw OCR Text</summary>
              <pre>{result.raw_text}</pre>
            </details>
          )}
        </div>
      )}
    </div>
  );
}
