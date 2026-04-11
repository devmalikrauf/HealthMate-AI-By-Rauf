"""OCR engine using Tesseract for text extraction from prescription images."""

import pytesseract
from PIL import Image

from app.config import settings

pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

OCR_CONFIGS = [
    "--oem 3 --psm 6",   # Uniform block of text
    "--oem 3 --psm 11",  # Sparse text (common in handwritten prescriptions)
    "--oem 3 --psm 4",   # Single column text
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
    """Run multi-pass OCR on image variants and return best text + confidence."""
    candidates: list[tuple[str, float, float]] = []

    for image in images:
        for config in OCR_CONFIGS:
            raw_text, conf = _extract_with_config(image, config)
            line_score = min(len(raw_text.split()) / 25.0, 1.0)
            score = (conf * 0.7) + (line_score * 0.3)
            if raw_text.strip():
                candidates.append((raw_text.strip(), conf, score))

            # Also test layout-preserving extraction for same config
            try:
                layout_text = pytesseract.image_to_string(image, config=config).strip()
            except pytesseract.TesseractNotFoundError as exc:
                raise RuntimeError(
                    "Tesseract OCR not found. Install Tesseract and set TESSERACT_CMD in backend/.env"
                ) from exc
            if layout_text:
                layout_score = (conf * 0.6) + (min(len(layout_text.split()) / 25.0, 1.0) * 0.4)
                candidates.append((layout_text, conf, layout_score))

    if not candidates:
        return "", 0.0

    best_text, best_conf, _ = max(candidates, key=lambda item: item[2])
    return best_text, round(best_conf, 2)
