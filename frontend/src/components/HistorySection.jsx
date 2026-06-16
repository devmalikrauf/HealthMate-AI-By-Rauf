import { useState, useEffect } from "react";
import { scan as scanApi } from "../api";

/* ─── icons ─── */
const IcoClip    = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>;
const IcoChevron = () => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"/></svg>;
const IcoPill    = () => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4.5 16.5c-1.5-1.5-2.5-3.5-2.5-6s1-4.5 2.5-6 3.5-2.5 6-2.5 4.5 1 6 2.5 2.5 3.5 2.5 6-1 4.5-2.5 6-3.5 2.5-6 2.5-4.5-1-6-2.5z"/><line x1="9" y1="9" x2="15" y2="15"/></svg>;
const IcoAlert   = () => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>;

export default function HistorySection() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    scanApi.history()
      .then((r) => setScans(r.scans || []))
      .catch(() => { })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="section-wrap"><div className="loader" /></div>;

  return (
    <div className="section-wrap">
      <div className="section-header">
        <h2>Scan History</h2>
        <p>{scans.length} previous prescription scan{scans.length !== 1 ? "s" : ""}</p>
      </div>

      {scans.length === 0 ? (
        <div className="card empty">
          <div style={{ color: "var(--text-muted)", display: "flex", justifyContent: "center", marginBottom: "12px" }}>
            <IcoClip />
          </div>
          <h4>No scans yet</h4>
          <p>Your analysis results will appear here after you scan your first prescription.</p>
        </div>
      ) : (
        <div className="history-list">
          {scans.map((s) => (
            <div
              key={s.id}
              className={`hist-card ${expanded === s.id ? "open" : ""}`}
              onClick={() => setExpanded(expanded === s.id ? null : s.id)}
            >
              <div className="hist-row">
                <div>
                  <h4>{s.filename || "Prescription Scan"}</h4>
                  <span className="hist-date">
                    {new Date(s.created_at).toLocaleDateString("en-US", {
                      year: "numeric", month: "short", day: "numeric",
                      hour: "2-digit", minute: "2-digit",
                    })}
                  </span>
                </div>
                <div className="hist-meta">
                  <span className="badge">{s.medicines?.length || 0} medicines</span>
                  <span className={`pill ${s.overall_confidence >= 0.7 ? "high" : s.overall_confidence >= 0.4 ? "med" : "low"}`}>
                    {Math.round((s.overall_confidence || 0) * 100)}% Match
                  </span>
                  <span className="chevron"><IcoChevron /></span>
                </div>
              </div>

              {expanded === s.id && (
                <div className="hist-body" onClick={(e) => e.stopPropagation()}>
                  {s.warnings?.length > 0 && (
                    <div className="hist-block">
                      <h5><IcoAlert /> Warnings &amp; Guidance</h5>
                      {s.warnings.map((w, i) => (
                        <p key={i} className={`sev-${w.severity}`}>
                          <strong>{w.type?.replace(/_/g," ")}</strong> — {w.message}
                        </p>
                      ))}
                    </div>
                  )}
                  <div className="hist-block">
                    <h5><IcoPill /> Medicines Extracted</h5>
                    {s.medicines?.map((m, i) => (
                      <p key={i}>
                        <strong>{m.medicine_name}</strong>
                        {m.strength ? ` (${m.strength})` : ""}
                        {m.dosage ? ` · Dose: ${m.dosage}` : ""}
                        {m.frequency ? ` · Freq: ${m.frequency}` : ""}
                        {m.duration ? ` · Dur: ${m.duration}` : ""}
                      </p>
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
