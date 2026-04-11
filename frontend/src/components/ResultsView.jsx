import { useState } from "react";
import MedicineCard from "./MedicineCard";
import WarningsList from "./WarningsList";
import FeedbackPanel from "./FeedbackPanel";

export default function ResultsView({ result }) {
  const [showRaw, setShowRaw] = useState(false);

  if (!result) return null;

  const confLevel =
    result.overall_confidence >= 0.7
      ? "high"
      : result.overall_confidence >= 0.5
      ? "medium"
      : "low";

  return (
    <div className="results">
      <div className="disclaimer">{result.disclaimer}</div>

      <div className="results__header">
        <div className="results__title">Extracted Medicines</div>
        <span className={`confidence-badge confidence-badge--${confLevel}`}>
          Overall: {Math.round(result.overall_confidence * 100)}%
        </span>
      </div>

      {result.medicines.length === 0 ? (
        <div className="error-box">
          No medicines could be identified. Try uploading a clearer image.
        </div>
      ) : (
        result.medicines.map((med, i) => <MedicineCard key={i} medicine={med} />)
      )}

      <WarningsList warnings={result.warnings} />

      <div className="raw-text">
        <button
          className="raw-text__toggle"
          onClick={() => setShowRaw(!showRaw)}
        >
          {showRaw ? "▾ Hide" : "▸ Show"} Raw OCR Text
        </button>
        {showRaw && (
          <div className="raw-text__content">
            {result.raw_text || "(empty)"}
          </div>
        )}
      </div>

      <FeedbackPanel result={result} />
    </div>
  );
}
