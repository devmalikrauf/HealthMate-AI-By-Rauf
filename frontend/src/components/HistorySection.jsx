import { useState, useEffect } from "react";
import { scan as scanApi } from "../api";

export default function HistorySection() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    scanApi.history()
      .then((r) => setScans(r.scans || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="section-wrap"><div className="loader" /></div>;

  return (
    <div className="section-wrap">
      <div className="section-header">
        <h2>Scan History</h2>
        <p>{scans.length} previous scan{scans.length !== 1 ? "s" : ""}</p>
      </div>

      {scans.length === 0 ? (
        <div className="card empty">
          <span style={{ fontSize: "2rem" }}>📋</span>
          <h4>No scans yet</h4>
          <p>Your results will appear here after scanning</p>
        </div>
      ) : (
        <div className="history-list">
          {scans.map((s) => (
            <div
              key={s.id}
              className={`card hist-card ${expanded === s.id ? "open" : ""}`}
              onClick={() => setExpanded(expanded === s.id ? null : s.id)}
            >
              <div className="hist-row">
                <div>
                  <h4>{s.filename || "Prescription"}</h4>
                  <span className="hist-date">
                    {new Date(s.created_at).toLocaleDateString("en-US", {
                      year: "numeric", month: "short", day: "numeric",
                      hour: "2-digit", minute: "2-digit",
                    })}
                  </span>
                </div>
                <div className="hist-meta">
                  <span className="badge">{s.medicines?.length || 0} meds</span>
                  <span className={`pill ${s.overall_confidence >= 0.7 ? "high" : s.overall_confidence >= 0.4 ? "med" : "low"}`}>
                    {Math.round((s.overall_confidence || 0) * 100)}%
                  </span>
                  <span className="chevron">{expanded === s.id ? "▲" : "▼"}</span>
                </div>
              </div>

              {expanded === s.id && (
                <div className="hist-body" onClick={(e) => e.stopPropagation()}>
                  {s.warnings?.length > 0 && (
                    <div className="hist-block">
                      <h5>⚠️ Warnings</h5>
                      {s.warnings.map((w, i) => (
                        <p key={i} className={`sev-${w.severity}`}>
                          <strong>{w.type}</strong> — {w.message}
                        </p>
                      ))}
                    </div>
                  )}
                  <div className="hist-block">
                    <h5>💊 Medicines</h5>
                    {s.medicines?.map((m, i) => (
                      <p key={i}><strong>{m.medicine_name}</strong>{m.strength ? ` ${m.strength}` : ""}{m.dosage ? ` · ${m.dosage}` : ""}{m.frequency ? ` · ${m.frequency}` : ""}</p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
