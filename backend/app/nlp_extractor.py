"""NLP extraction of structured medicine details from OCR text."""

import re
from app.models import MedicineEntry

# Curated common medicines list for deterministic testing and extraction.
COMMON_MEDICINES = sorted(set([
    "acetaminophen", "aceclofenac", "acyclovir", "alprazolam", "amlodipine",
    "amitriptyline", "amoxicillin", "amoxiclav", "apixaban", "aspirin",
    "atenolol", "atorvastatin", "azithromycin", "bisoprolol", "budesonide",
    "calcium", "carvedilol", "cefixime", "cephalexin", "cefpodoxime",
    "ceftriaxone", "cefuroxime", "celecoxib", "cetirizine", "chlorthalidone",
    "ciprofloxacin", "clindamycin", "clonazepam", "clopidogrel", "dabigatran",
    "dapagliflozin", "deriphyllin", "diazepam", "dicyclomine", "diclofenac",
    "domperidone", "doxycycline", "duloxetine", "empagliflozin", "enalapril",
    "escitalopram", "esomeprazole", "etoricoxib", "famotidine", "fexofenadine",
    "fluconazole", "fluoxetine", "fluticasone", "folic acid", "formoterol",
    "furosemide", "gabapentin", "gliclazide", "glimepiride", "heparin",
    "hydrochlorothiazide", "ibuprofen", "insulin", "ipratropium", "iron",
    "itraconazole", "levocetirizine", "levofloxacin", "levothyroxine", "linezolid",
    "lisinopril", "loratadine", "lorazepam", "losartan", "mesalamine",
    "metformin", "metoprolol", "metronidazole", "montelukast", "moxifloxacin",
    "multivitamin", "naproxen", "nebivolol", "nortriptyline", "olanzapine",
    "olmesartan", "omeprazole", "ondansetron", "pantoprazole", "paracetamol",
    "pravastatin", "prednisolone", "prednisone", "pregabalin", "quetiapine",
    "rabeprazole", "ramipril", "risperidone", "rivaroxaban", "rosuvastatin",
    "salbutamol", "sertraline", "simvastatin", "sitagliptin", "spironolactone",
    "tapentadol", "telmisartan", "teneligliptin", "ticagrelor", "tiotropium",
    "torsemide", "tramadol", "valacyclovir", "valsartan", "vildagliptin",
    "vitamin b12", "vitamin d3", "warfarin", "zinc",
    # Common brand names used in South Asian prescriptions
    "augmentin", "azee", "combiflam", "crocin", "dolo", "ecosprin",
    "glycomet", "pan", "shelcal", "stamlo", "telma",
]))

# Brand-to-generic normalization helps keep output consistent.
MEDICINE_ALIASES = {
    "augmentin": "amoxiclav",
    "azee": "azithromycin",
    "combiflam": "ibuprofen",
    "crocin": "paracetamol",
    "dolo": "paracetamol",
    "ecosprin": "aspirin",
    "glycomet": "metformin",
    "pan": "pantoprazole",
    "shelcal": "calcium",
    "stamlo": "amlodipine",
    "telma": "telmisartan",
}

COMMON_MEDICINE_PATTERNS = [
    (med, re.compile(r"\\b" + re.escape(med) + r"\\b", re.IGNORECASE))
    for med in sorted(COMMON_MEDICINES, key=len, reverse=True)
]

# More complete strength patterns used in prescriptions
STRENGTH_PATTERN = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|iu|units?|%)\b", re.IGNORECASE
)

DOSAGE_PATTERNS = [
    re.compile(r"\b(\d+(?:/\d+)?)\s*(tab(?:let)?s?|cap(?:sule)?s?|pill|puffs?)\b", re.IGNORECASE),
    re.compile(r"\b(\d+(?:\.\d+)?)\s*(ml|drops?|spoon(?:ful)?s?)\b", re.IGNORECASE),
    re.compile(r"\b(half|one|two|three)\s*(tab(?:let)?s?|cap(?:sule)?s?|pill|spoon(?:ful)?s?)\b", re.IGNORECASE),
]

FREQUENCY_PATTERNS = [
    (re.compile(r"\b([0-3]-[0-3]-[0-3])\b"), None),
    (re.compile(r"\bOD\b", re.IGNORECASE), "once daily"),
    (re.compile(r"\bBD\b", re.IGNORECASE), "twice daily"),
    (re.compile(r"\bTDS\b", re.IGNORECASE), "thrice daily"),
    (re.compile(r"\bQID\b", re.IGNORECASE), "four times daily"),
    (re.compile(r"\bSOS\b", re.IGNORECASE), "as needed (SOS)"),
    (re.compile(r"\bPRN\b", re.IGNORECASE), "as needed (PRN)"),
    (re.compile(r"\bonce\s+(?:daily|a\s+day)\b", re.IGNORECASE), "once daily"),
    (re.compile(r"\btwice\s+(?:daily|a\s+day)\b", re.IGNORECASE), "twice daily"),
    (re.compile(r"\bthrice\s+(?:daily|a\s+day)\b", re.IGNORECASE), "thrice daily"),
    (re.compile(r"\b(\d+)\s*times\s*(?:a\s*)?day\b", re.IGNORECASE), None),
    (re.compile(r"\bevery\s*(\d+)\s*(?:hrs?|hours?)\b", re.IGNORECASE), None),
    (re.compile(r"\bq\s*(\d+)h\b", re.IGNORECASE), None),
    (re.compile(r"\bHS\b", re.IGNORECASE), "at bedtime"),
]

DURATION_PATTERNS = [
    re.compile(r"\bfor\s*(\d+)\s*(days?|weeks?|months?)\b", re.IGNORECASE),
    re.compile(r"\bx\s*(\d+)\s*(days?|weeks?|months?)\b", re.IGNORECASE),
    re.compile(r"\b(\d+)\s*(days?|weeks?|months?)\b", re.IGNORECASE),
]

INSTRUCTION_PATTERNS = [
    (re.compile(r"\bafter\s+food\b", re.IGNORECASE), "after food"),
    (re.compile(r"\bbefore\s+food\b", re.IGNORECASE), "before food"),
    (re.compile(r"\bempty\s+stomach\b", re.IGNORECASE), "on empty stomach"),
    (re.compile(r"\bat\s+bed(?:time)?\b", re.IGNORECASE), "at bedtime"),
    (re.compile(r"\bwith\s+water\b", re.IGNORECASE), "with water"),
    (re.compile(r"\bwith\s+milk\b", re.IGNORECASE), "with milk"),
    (re.compile(r"\bafter\s+lunch\b", re.IGNORECASE), "after lunch"),
    (re.compile(r"\bafter\s+dinner\b", re.IGNORECASE), "after dinner"),
]

MED_PREFIX_PATTERN = re.compile(
    r"^\s*(?:tab(?:let)?\.?|cap(?:sule)?\.?|syp\.?|syr(?:up)?\.?|inj(?:ection)?\.?|cream\.?|ointment\.?)\s+",
    re.IGNORECASE,
)

NOISE_LINE_PATTERN = re.compile(
    r"\b(patient|doctor|hospital|clinic|address|phone|date|age|gender|rx)\b",
    re.IGNORECASE,
)


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _split_candidate_lines(raw_text: str) -> list[str]:
    text = raw_text.replace("\r", "\n")
    lines = [line.strip(" -•\t") for line in text.split("\n") if line.strip()]

    # If OCR came as a single line, split on separators to recover likely rows
    if len(lines) <= 1:
        compact = _normalize_space(raw_text)
        lines = [x.strip() for x in re.split(r"\s{2,}|;|\|", compact) if x.strip()]

    return lines


def get_supported_medicines() -> list[str]:
    """Return deterministic supported medicine names for testing."""
    return sorted(COMMON_MEDICINES)


def _find_known_medicine_in_line(text: str) -> str | None:
    """Find known medicine name in a line and normalize aliases to generic names."""
    for med, pattern in COMMON_MEDICINE_PATTERNS:
        if pattern.search(text):
            return MEDICINE_ALIASES.get(med, med)
    return None


def _parse_strength(text: str) -> str | None:
    match = STRENGTH_PATTERN.search(text)
    if not match:
        return None
    return f"{match.group(1)} {match.group(2).lower()}"


def _parse_dosage(text: str) -> str | None:
    for pattern in DOSAGE_PATTERNS:
        match = pattern.search(text)
        if match:
            return _normalize_space(match.group(0))
    return None


def _parse_frequency(text: str) -> str | None:
    for pattern, replacement in FREQUENCY_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        if replacement is not None:
            return replacement

        token = match.group(0)
        if pattern.pattern.startswith("\\b(\\d+)\\s*times"):
            return f"{match.group(1)} times daily"
        if "every" in pattern.pattern:
            return f"every {match.group(1)} hours"
        if "q\\s*(\\d+)h" in pattern.pattern:
            return f"every {match.group(1)} hours"
        return token
    return None


def _parse_duration(text: str) -> str | None:
    for pattern in DURATION_PATTERNS:
        match = pattern.search(text)
        if match:
            number = match.group(1)
            unit = match.group(2).lower()
            if number != "1" and not unit.endswith("s"):
                unit += "s"
            return f"{number} {unit}"
    return None


def _parse_instructions(text: str) -> str | None:
    found = []
    for pattern, label in INSTRUCTION_PATTERNS:
        if pattern.search(text):
            found.append(label)
    if not found:
        return None
    return ", ".join(dict.fromkeys(found))


def _extract_name(line: str, strength: str | None) -> str | None:
    working = MED_PREFIX_PATTERN.sub("", line)

    known = _find_known_medicine_in_line(working)
    if known:
        return known

    cut_positions = []
    if strength:
        idx = re.search(re.escape(strength), working, re.IGNORECASE)
        if idx:
            cut_positions.append(idx.start())

    for pattern in DOSAGE_PATTERNS:
        match = pattern.search(working)
        if match:
            cut_positions.append(match.start())

    for pattern, _ in FREQUENCY_PATTERNS:
        match = pattern.search(working)
        if match:
            cut_positions.append(match.start())

    for pattern in DURATION_PATTERNS:
        match = pattern.search(working)
        if match:
            cut_positions.append(match.start())

    end = min(cut_positions) if cut_positions else len(working)
    candidate = _normalize_space(working[:end])

    candidate = re.sub(r"[^A-Za-z0-9+\-/\s]", "", candidate).strip()
    tokens = [t for t in candidate.split(" ") if t]

    if not tokens:
        return None

    # Remove pure numeric leading tokens
    while tokens and re.fullmatch(r"\d+[.)-]?", tokens[0]):
        tokens.pop(0)

    if not tokens:
        return None

    name = " ".join(tokens[:4]).strip()

    # Avoid header-like or clearly invalid names
    if len(name) < 2 or NOISE_LINE_PATTERN.search(name):
        return None

    if re.fullmatch(r"[\d\s./-]+", name):
        return None

    return name


def _line_to_medicine(line: str) -> MedicineEntry | None:
    if len(line) < 3:
        return None

    if NOISE_LINE_PATTERN.search(line) and not STRENGTH_PATTERN.search(line):
        return None

    strength = _parse_strength(line)
    dosage = _parse_dosage(line)
    frequency = _parse_frequency(line)
    duration = _parse_duration(line)
    instructions = _parse_instructions(line)
    known_name = _find_known_medicine_in_line(line)
    name = known_name or _extract_name(line, strength)

    # Require a likely medicine name and at least one extracted clinical field.
    has_any_field = any([strength, dosage, frequency, duration, instructions])
    if not name or not (has_any_field or known_name):
        return None

    extracted_fields = sum(1 for x in [strength, dosage, frequency, duration, instructions] if x)
    if known_name:
        confidence = min(0.95, 0.55 + (extracted_fields * 0.08))
    else:
        confidence = min(0.95, 0.45 + (extracted_fields * 0.1))

    return MedicineEntry(
        medicine_name=name,
        strength=strength,
        dosage=dosage,
        frequency=frequency,
        duration=duration,
        instructions=instructions,
        confidence=round(confidence, 2),
    )


def _dedupe_medicines(medicines: list[MedicineEntry]) -> list[MedicineEntry]:
    merged: dict[str, MedicineEntry] = {}

    for med in medicines:
        key = re.sub(r"\s+", " ", med.medicine_name.lower()).strip()
        if key not in merged:
            merged[key] = med
            continue

        existing = merged[key]
        # Keep the richer entry if duplicates occur.
        existing_fields = sum(
            1 for x in [existing.strength, existing.dosage, existing.frequency, existing.duration, existing.instructions] if x
        )
        new_fields = sum(1 for x in [med.strength, med.dosage, med.frequency, med.duration, med.instructions] if x)

        if new_fields > existing_fields or med.confidence > existing.confidence:
            merged[key] = med

    return list(merged.values())


def extract_medicines(raw_text: str) -> list[MedicineEntry]:
    """Extract structured medicine information from OCR text."""
    lines = _split_candidate_lines(raw_text)

    medicines: list[MedicineEntry] = []
    for line in lines:
        parsed = _line_to_medicine(line)
        if parsed:
            medicines.append(parsed)

    if medicines:
        return _dedupe_medicines(medicines)

    # Last-resort fallback: parse by chunks around strength patterns.
    fallback: list[MedicineEntry] = []
    for chunk in re.split(r"(?=\b\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|iu|units?|%)\b)", raw_text, flags=re.IGNORECASE):
        chunk = _normalize_space(chunk)
        if not chunk:
            continue
        parsed = _line_to_medicine(chunk)
        if parsed:
            fallback.append(parsed)

    return _dedupe_medicines(fallback)
