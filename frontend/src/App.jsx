import { useState, useCallback } from "react";
import UploadZone from "./components/UploadZone";
import ResultsView from "./components/ResultsView";
import { analyzePrescription } from "./api";

export default function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = useCallback((selectedFile) => {
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setResult(null);
    setError(null);
  }, []);

  const handleRemove = useCallback(() => {
    if (preview) URL.revokeObjectURL(preview);
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
  }, [preview]);

  const handleAnalyze = useCallback(async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzePrescription(file);
      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to analyze prescription. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [file]);

  return (
    <div className="app">
      <header className="header">
        <div className="header__logo">🏥</div>
        <h1 className="header__title">HealthMate AI</h1>
        <p className="header__subtitle">
          AI-Powered Prescription Reader &amp; Safety Checker
        </p>
      </header>

      {!preview && <UploadZone onFileSelect={handleFileSelect} disabled={loading} />}

      {preview && (
        <div className="preview">
          <img src={preview} alt="Prescription preview" className="preview__img" />
          <button className="preview__remove" onClick={handleRemove} title="Remove image">
            ✕
          </button>
        </div>
      )}

      {preview && !loading && !result && (
        <div style={{ textAlign: "center", marginTop: 16 }}>
          <button className="btn btn--primary" onClick={handleAnalyze}>
            🔍 Analyze Prescription
          </button>
        </div>
      )}

      {loading && (
        <div className="loading">
          <div className="loading__spinner" />
          <div className="loading__text">
            Analyzing your prescription...
            <br />
            <small>Preprocessing image → Running OCR → Extracting medicines</small>
          </div>
        </div>
      )}

      {error && (
        <div className="error-box">
          <strong>Error:</strong> {error}
          <br />
          <button
            className="btn btn--secondary"
            style={{ marginTop: 12 }}
            onClick={handleRemove}
          >
            Try Again
          </button>
        </div>
      )}

      <ResultsView result={result} />

      {result && (
        <div style={{ textAlign: "center", marginTop: 16 }}>
          <button className="btn btn--secondary" onClick={handleRemove}>
            📋 Analyze Another Prescription
          </button>
        </div>
      )}

      <footer className="footer">
        HealthMate AI &copy; {new Date().getFullYear()} &middot; This tool is for
        informational purposes only. Always consult a healthcare professional.
      </footer>
    </div>
  );
}
