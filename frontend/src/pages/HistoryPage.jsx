import { useState, useEffect } from "react";
import { scan as scanApi } from "../api";

export default function HistoryPage() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    scanApi.history()
      .then((res) => setScans(res.scans || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-loader"><div className="spinner" /></div>;

  return (
    <div className="history-page">
      <div className="page-header">
        <h1>📜 Scan History</h1>
        <p>Your previous prescription scans</p>
        <span className="badge">{scans.length} scans</span>
      </div>

      {scans.length === 0 ? (
        <div className="empty-state glass">
          <span className="empty-icon">📋</span>
          <h3>No scans yet</h3>
          <p>Your prescription scan results will appear here</p>
        </div>
      ) : (
        <div className="history-list">
          {scans.map((s) => (
            <div
              key={s.id}
              className={`history-card glass ${expanded === s.id ? "expanded" : ""}`}
              onClick={() => setExpanded(expanded === s.id ? null : s.id)}
            >
              <div className="history-card-header">
                <div className="history-info">
                  <h3>{s.filename || "Prescription"}</h3>
                  <span className="history-date">
                    {new Date(s.created_at).toLocaleDateString("en-US", {
                      year: "numeric", month: "short", day: "numeric",
                      hour: "2-digit", minute: "2-digit",
                    })}
                  </span>
                </div>
                <div className="history-meta">
                  <span className="badge">{s.medicines?.length || 0} medicines</span>
                  <span className={`conf-pill ${s.overall_confidence >= 0.7 ? "high" : s.overall_confidence >= 0.4 ? "med" : "low"}`}>
                    {Math.round((s.overall_confidence || 0) * 100)}%
                  </span>
                  <span className="expand-icon">{expanded === s.id ? "▲" : "▼"}</span>
                </div>
              </div>

              {expanded === s.id && (
                <div className="history-details" onClick={(e) => e.stopPropagation()}>
                  {s.warnings?.length > 0 && (
                    <div className="detail-section">
                      <h4>⚠️ Warnings</h4>
                      {s.warnings.map((w, i) => (
                        <div key={i} className={`warning-item severity-${w.severity}`}>
                          <strong>{w.type}</strong> — {w.message}
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="detail-section">
                    <h4>💊 Medicines</h4>
                    <div className="detail-medicines">
                      {s.medicines?.map((m, i) => (
                        <div key={i} className="detail-med">
                          <strong>{m.name}</strong>
                          {m.dosage && <span> • {m.dosage}</span>}
                          {m.frequency && <span> • {m.frequency}</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                  {s.raw_text && (
                    <details className="raw-text-section">
                      <summary>📄 Raw Text</summary>
                      <pre>{s.raw_text}</pre>
                    </details>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
