"""HealthMate AI - Prescription Reader API."""

import io
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel

from app.config import settings
from app.image_processing import auto_rotate, deskew, preprocess_image
from app.models import PrescriptionResult
from app.nlp_extractor import extract_medicines, get_supported_medicines
from app.ocr_engine import extract_best_text
from app.safety_engine import run_safety_checks

logger = logging.getLogger("healthmate")


class DebugParseRequest(BaseModel):
    raw_text: str


class FeedbackRequest(BaseModel):
    raw_text: str
    extracted_medicines: list[dict]
    extracted_warnings: list[dict] | None = None
    corrected_text: str | None = None
    corrected_medicines: list[dict] | None = None
    notes: str | None = None
    user_confirmed_correct: bool = False

app = FastAPI(
    title="HealthMate AI",
    description="AI-powered prescription reader and medication safety checker",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
MAX_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "HealthMate AI"}


@app.get("/api/medicines")
async def supported_medicines():
    """Return supported/common medicine list for controlled testing."""
    medicines = get_supported_medicines()
    return {
        "count": len(medicines),
        "medicines": medicines,
        "note": "Use these names in prescriptions for deterministic tests.",
    }


@app.post("/api/debug/parse-text")
async def debug_parse_text(payload: DebugParseRequest):
    """Debug helper: parse OCR text directly without image upload."""
    medicines = extract_medicines(payload.raw_text)
    warnings = run_safety_checks(medicines)
    return {
        "medicines": [m.model_dump() for m in medicines],
        "warnings": [w.model_dump() for w in warnings],
        "count": len(medicines),
    }


@app.post("/api/feedback")
async def submit_feedback(payload: FeedbackRequest):
    """Store feedback samples for future model training and rule tuning."""
    if not payload.raw_text.strip():
        raise HTTPException(status_code=400, detail="raw_text is required")

    sample = {
        "id": uuid.uuid4().hex,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "raw_text": payload.raw_text.strip(),
        "extracted_medicines": payload.extracted_medicines,
        "extracted_warnings": payload.extracted_warnings or [],
        "corrected_text": payload.corrected_text,
        "corrected_medicines": payload.corrected_medicines or [],
        "notes": payload.notes,
        "user_confirmed_correct": payload.user_confirmed_correct,
    }

    feedback_path = Path(settings.FEEDBACK_DATASET_PATH)
    with feedback_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    return {"status": "saved", "sample_id": sample["id"]}


@app.get("/api/feedback/stats")
async def feedback_stats():
    """Get quick dataset stats for collected feedback."""
    feedback_path = Path(settings.FEEDBACK_DATASET_PATH)
    if not feedback_path.exists():
        return {"samples": 0, "path": str(feedback_path)}

    total = 0
    corrected = 0
    confirmed = 0

    with feedback_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("corrected_text") or item.get("corrected_medicines"):
                corrected += 1
            if item.get("user_confirmed_correct"):
                confirmed += 1

    return {
        "samples": total,
        "corrected_samples": corrected,
        "confirmed_correct_samples": confirmed,
        "path": str(feedback_path),
    }


@app.post("/api/analyze", response_model=PrescriptionResult)
async def analyze_prescription(file: UploadFile = File(...)):
    """Upload a prescription image and get structured analysis."""

    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB} MB.",
        )

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Save upload (for debugging/audit)
    upload_path = Path(settings.UPLOAD_DIR) / f"{uuid.uuid4().hex}{ext}"
    upload_path.write_bytes(contents)

    try:
        # 1. Build image variants for OCR
        original = Image.open(io.BytesIO(contents)).convert("RGB")
        processed = preprocess_image(contents)
        processed = deskew(auto_rotate(processed))
        original = deskew(auto_rotate(original))

        # 2. Multi-pass OCR extraction
        final_text, ocr_confidence = extract_best_text([processed, original])
        logger.info("OCR confidence: %.2f", ocr_confidence)

        if not final_text.strip():
            return PrescriptionResult(
                raw_text="",
                medicines=[],
                warnings=[],
                overall_confidence=0.0,
                disclaimer=(
                    "⚠️ No text could be extracted from this image. "
                    "Please try a clearer photo with good lighting."
                ),
            )

        # 3. NLP extraction
        medicines = extract_medicines(final_text)
        logger.info("Extracted medicines count: %d", len(medicines))
        if medicines:
            preview = [
                {
                    "name": m.medicine_name,
                    "strength": m.strength,
                    "dosage": m.dosage,
                    "frequency": m.frequency,
                    "duration": m.duration,
                }
                for m in medicines[:5]
            ]
            logger.info("Extracted medicines preview: %s", preview)

        # 4. Safety checks
        warnings = run_safety_checks(medicines)
        logger.info("Safety warnings count: %d", len(warnings))

        # Overall confidence
        if medicines:
            med_confidence = sum(m.confidence for m in medicines) / len(medicines)
            overall = (ocr_confidence + med_confidence) / 2
        else:
            overall = ocr_confidence * 0.5

        return PrescriptionResult(
            raw_text=final_text,
            medicines=medicines,
            warnings=warnings,
            overall_confidence=round(overall, 2),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing prescription: {str(e)}",
        )
    finally:
        # Clean up uploaded file
        try:
            upload_path.unlink(missing_ok=True)
        except OSError:
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
