import { useState, useRef, useCallback } from "react";
import { scan as scanApi } from "../api";

export default function ScanSection({ user, onNeedAuth }) {
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
    <div className="section-wrap">
      <div className="section-header">
        <h2>Upload Prescription</h2>
        <p>Drop or select a prescription image to analyze</p>
      </div>

      {!result ? (
        <div className="scan-area">
          <div
            className={`dropzone ${dragActive ? "active" : ""} ${preview ? "has-preview" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={() => setDragActive(false)}
            onDrop={onDrop}
            onClick={() => !preview && inputRef.current?.click()}
          >
            {preview ? (
              <div className="preview-wrap">
                <img src={preview} alt="Preview" />
                <button className="preview-remove" onClick={(e) => { e.stopPropagation(); reset(); }}>✕ Remove</button>
              </div>
            ) : (
              <div className="drop-placeholder">
                <span className="drop-icon">📷</span>
                <h3>Drop prescription image here</h3>
                <p>or click to browse · JPG, PNG, BMP, TIFF, WebP</p>
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
            <button className="btn-accent btn-lg" onClick={analyze} disabled={loading}>
              {loading ? "Analyzing…" : "🔍  Analyze Prescription"}
            </button>
          )}
          {error && <div className="alert-error">{error}</div>}

          {!user && (
            <p className="login-hint">
              <button onClick={onNeedAuth}>Sign in</button> to save scans to your history
            </p>
          )}
        </div>
      ) : (
        <div className="results">
          <div className="results-top">
            <div className="conf-display">
              <span className="conf-label">Confidence</span>
              <span className={`conf-big ${result.overall_confidence >= 0.7 ? "high" : result.overall_confidence >= 0.4 ? "med" : "low"}`}>
                {Math.round(result.overall_confidence * 100)}%
              </span>
            </div>
            <button className="btn-outline" onClick={reset}>← New Scan</button>
          </div>

          {result.warnings?.length > 0 && (
            <div className="card warnings-card">
              <h3>⚠️  Safety Warnings</h3>
              {result.warnings.map((w, i) => (
                <div key={i} className={`warning-row sev-${w.severity}`}>
                  <span>{w.severity === "high" ? "🔴" : w.severity === "medium" ? "🟡" : "🔵"}</span>
                  <div>
                    <strong>{w.type}</strong>
                    <p>{w.message}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          <h3 className="med-heading">💊 Detected Medicines ({result.medicines?.length || 0})</h3>
          {result.medicines?.length > 0 ? (
            <div className="med-grid">
              {result.medicines.map((m, i) => (
                <div key={i} className="card med-card">
                  <div className="med-top">
                    <h4>{m.name}</h4>
                    <span className={`pill ${m.confidence >= 0.8 ? "high" : m.confidence >= 0.5 ? "med" : "low"}`}>
                      {Math.round(m.confidence * 100)}%
                    </span>
                  </div>
                  <div className="med-tags">
                    {m.dosage && <span className="tag">💉 {m.dosage}</span>}
                    {m.frequency && <span className="tag">🕐 {m.frequency}</span>}
                    {m.duration && <span className="tag">📅 {m.duration}</span>}
                    {m.instructions && <span className="tag">📝 {m.instructions}</span>}
                    {m.generic_name && m.generic_name !== m.name && (
                      <span className="tag tag-gen">🧬 {m.generic_name}</span>
                    )}
                    {m.common_use && <span className="tag tag-use">🩺 {m.common_use}</span>}
                  </div>
                  {(m.allergy_warning || m.side_effects) && (
                    <div className="med-extra">
                      {m.allergy_warning && (
                        <p className="med-allergy">⚠️ <strong>Allergy:</strong> {m.allergy_warning}</p>
                      )}
                      {m.side_effects && (
                        <p className="med-sides">💊 <strong>Side Effects:</strong> {m.side_effects}</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="card empty">No medicines detected — try a clearer image.</div>
          )}

          {result.raw_text && (
            <details className="card raw-card">
              <summary>📄 Raw OCR Text</summary>
              <pre>{result.raw_text}</pre>
            </details>
          )}
        </div>
      )}
    </div>
  );
}
