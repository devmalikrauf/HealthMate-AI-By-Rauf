const ICONS = {
  high: "🔴",
  medium: "🟡",
  low: "🔵",
};

export default function WarningsList({ warnings }) {
  if (!warnings || warnings.length === 0) return null;

  return (
    <div className="warnings">
      <div className="warnings__title">⚠️ Safety Alerts</div>
      {warnings.map((w, i) => (
        <div key={i} className={`warning-item warning-item--${w.severity}`}>
          <span className="warning-item__icon">{ICONS[w.severity] || "⚠️"}</span>
          <span>{w.message}</span>
        </div>
      ))}
    </div>
  );
}
