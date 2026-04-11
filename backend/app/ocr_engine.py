"""OCR engine using Tesseract for text extraction from prescription images."""

import re
import pytesseract
from PIL import Image

from app.config import settings

pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

OCR_CONFIGS = [
    "--oem 3 --psm 6",   # Uniform block of text
    "--oem 3 --psm 4",   # Single column text
    "--oem 3 --psm 3",   # Fully automatic page segmentation
    "--oem 3 --psm 11",  # Sparse text (common in handwritten prescriptions)
    "--oem 3 --psm 12",  # Sparse text with OSD
]


def _extract_with_config(image: Image.Image, config: str) -> tuple[str, float]:
    """Extract text using one Tesseract configuration."""
    try:
        data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT,
            config=config,
        )
    except pytesseract.TesseractNotFoundError as exc:
        raise RuntimeError(
            "Tesseract OCR not found. Install Tesseract and set TESSERACT_CMD in backend/.env"
        ) from exc

    words = []
    confidences = []

    for i, text in enumerate(data["text"]):
        text = text.strip()
        try:
            conf = float(data["conf"][i])
        except (TypeError, ValueError):
            conf = -1.0

        if text and conf >= 0:
            words.append(text)
            if conf > 0:
                confidences.append(conf)

    raw_text = " ".join(words)
    avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
    return raw_text, avg_confidence


def extract_text(image: Image.Image) -> tuple[str, float]:
    """Extract text from a preprocessed image.

    Returns (extracted_text, average_confidence).
    """
    # Backward-compatible single-pass extraction using default config.
    return _extract_with_config(image, OCR_CONFIGS[0])


def extract_text_with_layout(image: Image.Image) -> str:
    """Extract text preserving line-by-line layout (useful for prescriptions)."""
    try:
        text = pytesseract.image_to_string(image, config=OCR_CONFIGS[0])
    except pytesseract.TesseractNotFoundError as exc:
        raise RuntimeError(
            "Tesseract OCR not found. Install Tesseract and set TESSERACT_CMD in backend/.env"
        ) from exc
    return text.strip()


def extract_best_text(images: list[Image.Image]) -> tuple[str, float]:
    """Run multi-pass OCR on image variants and return best text + confidence.
    
    Scores candidates by: OCR confidence, word count, and known medicine matches.
    """
    from app.nlp_extractor import COMMON_MEDICINE_PATTERNS, OCR_FUZZY_ALIASES

    candidates: list[tuple[str, float, float]] = []

    def _medicine_score(text: str) -> float:
        """Count how many known medicines appear in the text."""
        count = 0
        text_lower = text.lower()
        for med, pattern in COMMON_MEDICINE_PATTERNS:
            if pattern.search(text):
                count += 1
        for variant in OCR_FUZZY_ALIASES:
            if re.search(r"\b" + re.escape(variant) + r"\b", text_lower):
                count += 0.5
        return count

    for image in images:
        for config in OCR_CONFIGS:
            raw_text, conf = _extract_with_config(image, config)
            if raw_text.strip():
                word_score = min(len(raw_text.split()) / 25.0, 1.0)
                med_score = _medicine_score(raw_text)
                # Medicine matches are the most important factor
                score = (conf * 0.4) + (word_score * 0.2) + (med_score * 0.4)
                candidates.append((raw_text.strip(), conf, score))

            # Also test layout-preserving extraction
            try:
                layout_text = pytesseract.image_to_string(image, config=config).strip()
            except pytesseract.TesseractNotFoundError as exc:
                raise RuntimeError(
                    "Tesseract OCR not found. Install Tesseract and set TESSERACT_CMD in backend/.env"
                ) from exc
            if layout_text:
                word_score = min(len(layout_text.split()) / 25.0, 1.0)
                med_score = _medicine_score(layout_text)
                layout_conf = conf  # use same confidence
                score = (layout_conf * 0.4) + (word_score * 0.2) + (med_score * 0.4)
                candidates.append((layout_text, layout_conf, score))

    if not candidates:
        return "", 0.0

    # If multiple candidates have medicine matches, merge unique lines from top candidates
    candidates.sort(key=lambda x: x[2], reverse=True)
    best_text, best_conf, best_score = candidates[0]

    # Try merging top candidates to recover more medicine names
    if len(candidates) > 1:
        merged_lines = []
        seen_lower = set()
        for text, conf, score in candidates[:6]:  # Top 6 candidates
            for line in text.split("\n"):
                line_clean = line.strip()
                line_key = re.sub(r"\s+", " ", line_clean.lower())
                if line_clean and line_key not in seen_lower:
                    seen_lower.add(line_key)
                    merged_lines.append(line_clean)
        merged_text = "\n".join(merged_lines)
        merged_med_score = _medicine_score(merged_text)
        # Use merged text if it finds more medicines
        if merged_med_score > _medicine_score(best_text):
            best_text = merged_text

    return best_text, round(best_conf, 2)
