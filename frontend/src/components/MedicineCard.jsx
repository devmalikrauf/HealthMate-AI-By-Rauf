export default function MedicineCard({ medicine }) {
  const isLowConf = medicine.confidence < 0.5;

  const details = [
    { label: "Strength", value: medicine.strength },
    { label: "Dosage", value: medicine.dosage },
    { label: "Frequency", value: medicine.frequency },
    { label: "Duration", value: medicine.duration },
    { label: "Instructions", value: medicine.instructions },
  ];

  return (
    <div className={`medicine-card ${isLowConf ? "medicine-card--low-conf" : ""}`}>
      <div className="medicine-card__name">
        💊 {medicine.medicine_name}
        <span
          className={`confidence-badge confidence-badge--${
            medicine.confidence >= 0.7 ? "high" : medicine.confidence >= 0.5 ? "medium" : "low"
          }`}
        >
          {Math.round(medicine.confidence * 100)}%
        </span>
      </div>
      <div className="medicine-card__details">
        {details.map((d) => (
          <div key={d.label} className="medicine-card__detail">
            <div className="medicine-card__label">{d.label}</div>
            <div
              className={`medicine-card__value ${
                !d.value ? "medicine-card__value--missing" : ""
              }`}
            >
              {d.value || "Not detected"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
