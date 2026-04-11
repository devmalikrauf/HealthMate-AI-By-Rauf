import { useState } from "react";
import { submitExtractionFeedback } from "../api";

export default function FeedbackPanel({ result }) {
  const [open, setOpen] = useState(false);
  const [notes, setNotes] = useState("");
  const [correctedText, setCorrectedText] = useState("");
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState("");

  if (!result) return null;

  const sendFeedback = async (confirmedCorrect) => {
    setStatus("loading");
    setMessage("");
    try {
      await submitExtractionFeedback({
        raw_text: result.raw_text || "",
        extracted_medicines: result.medicines || [],
        extracted_warnings: result.warnings || [],
        corrected_text: correctedText || null,
        corrected_medicines: [],
        notes: notes || null,
        user_confirmed_correct: confirmedCorrect,
      });
      setStatus("success");
      setMessage("Feedback saved. This will help improve extraction accuracy.");
      if (confirmedCorrect) {
        setOpen(false);
      }
    } catch (err) {
      setStatus("error");
      setMessage(err.message || "Could not submit feedback.");
    }
  };

  return (
    <div className="feedback-panel">
      <div className="feedback-panel__title">Model Feedback</div>
      <div className="feedback-panel__desc">
        Is extraction accurate? Share correction to improve future results.
      </div>
      <div className="feedback-panel__actions">
        <button className="btn btn--secondary" onClick={() => sendFeedback(true)}>
          Looks Correct
        </button>
        <button className="btn btn--primary" onClick={() => setOpen(!open)}>
          {open ? "Hide Correction" : "Report Issue"}
        </button>
      </div>

      {open && (
        <div className="feedback-panel__form">
          <label className="feedback-panel__label">Corrected Prescription Text (optional)</label>
          <textarea
            className="feedback-panel__textarea"
            value={correctedText}
            onChange={(e) => setCorrectedText(e.target.value)}
            placeholder="Write corrected line(s), e.g. Tab Dolo 650 mg 1 tablet BD for 5 days"
          />

          <label className="feedback-panel__label">Notes (optional)</label>
          <textarea
            className="feedback-panel__textarea"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Example: medicine name was misread, frequency should be OD"
          />

          <button
            className="btn btn--primary"
            onClick={() => sendFeedback(false)}
            disabled={status === "loading"}
          >
            {status === "loading" ? "Submitting..." : "Submit Feedback"}
          </button>
        </div>
      )}

      {message && (
        <div
          className={`feedback-panel__status feedback-panel__status--${
            status === "error" ? "error" : "success"
          }`}
        >
          {message}
        </div>
      )}
    </div>
  );
}
