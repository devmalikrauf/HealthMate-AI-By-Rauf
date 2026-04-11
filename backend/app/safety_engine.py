"""Safety engine: checks for potential issues in extracted prescription data."""

import re
from app.models import MedicineEntry, SafetyWarning

# Known dangerous dosage thresholds (simplified)
MAX_DOSAGE_WARNINGS = {
    "paracetamol": {"max_mg": 4000, "note": "Max 4g/day for adults"},
    "acetaminophen": {"max_mg": 4000, "note": "Max 4g/day for adults"},
    "ibuprofen": {"max_mg": 3200, "note": "Max 3.2g/day for adults"},
    "aspirin": {"max_mg": 4000, "note": "Max 4g/day for adults"},
    "metformin": {"max_mg": 2550, "note": "Max 2.55g/day for adults"},
    "amoxicillin": {"max_mg": 3000, "note": "Max 3g/day for adults"},
    "azithromycin": {"max_mg": 500, "note": "Typically 500mg/day"},
    "omeprazole": {"max_mg": 40, "note": "Typically max 40mg/day"},
    "cetirizine": {"max_mg": 10, "note": "Typically max 10mg/day"},
    "diclofenac": {"max_mg": 150, "note": "Max 150mg/day"},
    "gabapentin": {"max_mg": 3600, "note": "Max 3.6g/day"},
    # Additional thresholds from Pakistani medicine dataset
    "domperidone": {"max_mg": 30, "note": "Max 30mg/day for adults"},
    "furosemide": {"max_mg": 80, "note": "Max 80mg/day for adults"},
    "naproxen": {"max_mg": 1250, "note": "Max 1.25g/day for adults"},
    "enalapril": {"max_mg": 40, "note": "Max 40mg/day for adults"},
    "glimepiride": {"max_mg": 8, "note": "Max 8mg/day for adults"},
    "metronidazole": {"max_mg": 2000, "note": "Max 2g/day for adults"},
    "perindopril": {"max_mg": 16, "note": "Max 16mg/day for adults"},
    "amlodipine": {"max_mg": 10, "note": "Max 10mg/day for adults"},
    "pantoprazole": {"max_mg": 40, "note": "Typically max 40mg/day"},
    "telmisartan": {"max_mg": 80, "note": "Max 80mg/day for adults"},
    "sofosbuvir": {"max_mg": 400, "note": "Standard 400mg/day"},
    "entecavir": {"max_mg": 1, "note": "Max 1mg/day for adults"},
    "sitagliptin": {"max_mg": 100, "note": "Max 100mg/day for adults"},
}

# Medicines that sound similar (common confusion pairs)
SIMILAR_MEDICINES = [
    ("losartan", "lisinopril"),
    ("metformin", "metoprolol"),
    ("prednisolone", "prednisone"),
    ("omeprazole", "esomeprazole"),
    ("cetirizine", "sertraline"),
    ("hydroxyzine", "hydralazine"),
    ("clopidogrel", "carvedilol"),
    ("glimepiride", "glipizide"),
    ("clonidine", "clonazepam"),
    ("tramadol", "trazodone"),
]


def run_safety_checks(medicines: list[MedicineEntry]) -> list[SafetyWarning]:
    """Run all safety checks and return warnings."""
    warnings: list[SafetyWarning] = []

    for med in medicines:
        warnings.extend(_check_low_confidence(med))
        warnings.extend(_check_unclear_name(med))
        warnings.extend(_check_unusual_dosage(med))
        warnings.extend(_check_missing_info(med))

    warnings.extend(_check_duplicates(medicines))
    warnings.extend(_check_similar_names(medicines))

    return warnings


def _check_low_confidence(med: MedicineEntry) -> list[SafetyWarning]:
    """Flag medicines with low OCR confidence."""
    warnings = []
    if med.confidence < 0.5:
        warnings.append(SafetyWarning(
            type="low_confidence",
            message=f"Low confidence ({med.confidence:.0%}) in reading '{med.medicine_name}'. "
                    f"The text may have been misread.",
            severity="high",
            related_medicine=med.medicine_name,
        ))
    elif med.confidence < 0.7:
        warnings.append(SafetyWarning(
            type="low_confidence",
            message=f"Moderate confidence ({med.confidence:.0%}) in reading '{med.medicine_name}'. "
                    f"Please verify.",
            severity="medium",
            related_medicine=med.medicine_name,
        ))
    return warnings


def _check_unclear_name(med: MedicineEntry) -> list[SafetyWarning]:
    """Check if medicine name looks unclear or garbled."""
    warnings = []
    name = med.medicine_name

    # Check for too many consonants in a row (garbled OCR)
    if re.search(r"[bcdfghjklmnpqrstvwxyz]{5,}", name, re.IGNORECASE):
        warnings.append(SafetyWarning(
            type="unclear_name",
            message=f"Medicine name '{name}' may be incorrectly read. "
                    f"It contains unusual character patterns.",
            severity="high",
            related_medicine=name,
        ))

    # Check for numbers mixed into name
    if re.search(r"[a-zA-Z]\d[a-zA-Z]", name):
        warnings.append(SafetyWarning(
            type="unclear_name",
            message=f"Medicine name '{name}' contains unexpected numbers. "
                    f"It may have been misread.",
            severity="medium",
            related_medicine=name,
        ))

    # Very short name
    if len(name.strip()) < 3:
        warnings.append(SafetyWarning(
            type="unclear_name",
            message=f"Medicine name '{name}' is very short and may be incomplete.",
            severity="medium",
            related_medicine=name,
        ))

    return warnings


def _check_unusual_dosage(med: MedicineEntry) -> list[SafetyWarning]:
    """Check for unusually high dosages."""
    warnings = []
    if not med.strength:
        return warnings

    name_lower = med.medicine_name.lower()
    match = re.search(r"(\d+(?:\.\d+)?)", med.strength)
    if not match:
        return warnings

    dosage_value = float(match.group(1))

    for med_name, limits in MAX_DOSAGE_WARNINGS.items():
        if med_name in name_lower:
            if dosage_value > limits["max_mg"]:
                warnings.append(SafetyWarning(
                    type="unusual_dosage",
                    message=f"Dosage of {med.strength} for '{med.medicine_name}' seems unusually high. "
                            f"{limits['note']}.",
                    severity="high",
                    related_medicine=med.medicine_name,
                ))
            break

    return warnings


def _check_missing_info(med: MedicineEntry) -> list[SafetyWarning]:
    """Flag medicines with missing critical information."""
    warnings = []
    missing = []

    if not med.strength:
        missing.append("strength/dose")
    if not med.frequency:
        missing.append("frequency")
    if not med.dosage:
        missing.append("dosage form")

    if missing:
        warnings.append(SafetyWarning(
            type="missing_info",
            message=f"Missing information for '{med.medicine_name}': {', '.join(missing)}. "
                    f"Please check the original prescription.",
            severity="medium" if len(missing) <= 1 else "high",
            related_medicine=med.medicine_name,
        ))

    return warnings


def _check_duplicates(medicines: list[MedicineEntry]) -> list[SafetyWarning]:
    """Check for duplicate medicine entries."""
    warnings = []
    seen = {}

    for med in medicines:
        name_lower = med.medicine_name.lower().strip()
        if name_lower in seen:
            warnings.append(SafetyWarning(
                type="duplicate",
                message=f"'{med.medicine_name}' appears more than once in the prescription. "
                        f"This may be an error.",
                severity="high",
                related_medicine=med.medicine_name,
            ))
        else:
            seen[name_lower] = True

    return warnings


def _check_similar_names(medicines: list[MedicineEntry]) -> list[SafetyWarning]:
    """Warn if extracted names are suspiciously similar to known confusion pairs."""
    warnings = []
    names_lower = [m.medicine_name.lower() for m in medicines]

    for name in names_lower:
        for med_a, med_b in SIMILAR_MEDICINES:
            if med_a in name:
                warnings.append(SafetyWarning(
                    type="similar_name",
                    message=f"Note: '{med_a}' is sometimes confused with '{med_b}'. "
                            f"Please verify the correct medicine.",
                    severity="low",
                    related_medicine=med_a,
                ))
            elif med_b in name:
                warnings.append(SafetyWarning(
                    type="similar_name",
                    message=f"Note: '{med_b}' is sometimes confused with '{med_a}'. "
                            f"Please verify the correct medicine.",
                    severity="low",
                    related_medicine=med_b,
                ))

    return warnings
