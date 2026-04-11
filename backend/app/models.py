from pydantic import BaseModel


class MedicineEntry(BaseModel):
    medicine_name: str
    strength: str | None = None
    dosage: str | None = None
    frequency: str | None = None
    duration: str | None = None
    instructions: str | None = None
    confidence: float = 0.0  # 0.0 to 1.0


class SafetyWarning(BaseModel):
    type: str  # "unclear_name", "unusual_dosage", "duplicate", "missing_info"
    message: str
    severity: str  # "low", "medium", "high"
    related_medicine: str | None = None


class PrescriptionResult(BaseModel):
    raw_text: str
    medicines: list[MedicineEntry]
    warnings: list[SafetyWarning]
    overall_confidence: float
    disclaimer: str = (
        "⚠️ This result may not be 100% accurate. "
        "Please confirm with a doctor or pharmacist before taking any medication."
    )
