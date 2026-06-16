import { useState, useEffect } from "react";
import { admin as adminApi } from "../api";

/* ─── icons ─── */
const IcoShield = () => <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{verticalAlign:"middle",marginRight:"8px",color:"var(--primary)"}}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>;

export default function AdminPanel({ onClose }) {
  const [data, setData] = useState(null);
  const [users, setUsers] = useState([]);
  const [scans, setScans] = useState([]);
  const [tab, setTab] = useState("overview");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([adminApi.dashboard(), adminApi.users(), adminApi.scans()])
      .then(([d, u, s]) => { setData(d); setUsers(u.users || []); setScans(s.scans || []); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="admin-panel" onClick={(e) => e.stopPropagation()}>
        <div className="admin-head">
          <h2><IcoShield/>Admin Panel</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        {loading ? <div className="loader" /> : (
          <>
            <div className="stat-row">
              <div className="stat"><h3>{data?.users || 0}</h3><p>Users</p></div>
              <div className="stat"><h3>{data?.scans?.total_scans || 0}</h3><p>Scans</p></div>
              <div className="stat"><h3>{data?.feedback_samples || 0}</h3><p>Feedback</p></div>
              <div className="stat"><h3>{data?.supported_medicines || 0}</h3><p>Medicines</p></div>
            </div>

            {data?.scans && (
              <div className="perf-row">
                <div><strong>{Math.round((data.scans.avg_confidence || 0) * 100)}%</strong><span>Avg Confidence</span></div>
                <div><strong>{(data.scans.avg_medicines_per_scan || 0).toFixed(1)}</strong><span>Avg Meds/Scan</span></div>
                <div><strong>{data.scans.total_warnings || 0}</strong><span>Total Warnings</span></div>
              </div>
            )}

            <div className="tab-bar">
              <button className={tab === "overview" ? "active" : ""} onClick={() => setTab("overview")}>Recent Scans</button>
              <button className={tab === "users" ? "active" : ""} onClick={() => setTab("users")}>Users</button>
            </div>

            <div className="admin-table-wrap">
              {tab === "users" ? (
                <table>
                  <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Joined</th></tr></thead>
                  <tbody>
                    {users.map((u) => (
                      <tr key={u.id}>
                        <td>{u.name}</td>
                        <td>{u.email}</td>
                        <td><span className={`role ${u.role}`}>{u.role}</span></td>
                        <td>{new Date(u.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <table>
                  <thead><tr><th>File</th><th>Medicines</th><th>Confidence</th><th>Date</th></tr></thead>
                  <tbody>
                    {scans.map((s) => (
                      <tr key={s.id}>
                        <td>{s.filename || "—"}</td>
                        <td>{s.medicines?.length || 0}</td>
                        <td><span className={`pill ${s.overall_confidence >= 0.7 ? "high" : "low"}`}>{Math.round((s.overall_confidence || 0) * 100)}%</span></td>
                        <td>{new Date(s.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
