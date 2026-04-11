"""HealthMate AI - Prescription Reader API."""

import io
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel

from app.auth import hash_password, verify_password, create_token, decode_token
from app.config import settings
from app.database import (
    find_user, create_user, get_user_scans, save_scan,
    count_users, count_scans, get_scan_stats, get_all_scans, get_all_users,
)
from app.image_processing import auto_rotate, deskew, preprocess_image
from app.models import PrescriptionResult
from app.nlp_extractor import extract_medicines, get_supported_medicines
from app.ocr_engine import extract_best_text
from app.safety_engine import run_safety_checks

logger = logging.getLogger("healthmate")

app = FastAPI(
    title="HealthMate AI",
    description="AI-powered prescription reader and medication safety checker",
    version="2.0.0",
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


# ── Auth helpers ───────────────────────────────────

def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


def get_optional_user(authorization: str | None = Header(default=None)) -> dict | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    return payload


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ── Request models ─────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


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


# ── Public endpoints ───────────────────────────────

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "HealthMate AI", "version": "2.0.0"}


@app.post("/api/auth/register")
async def register(req: RegisterRequest):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if find_user(req.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    user_id = uuid.uuid4().hex
    role = "admin" if count_users() == 0 else "user"

    create_user({
        "id": user_id,
        "name": req.name.strip(),
        "email": req.email.strip().lower(),
        "password": hash_password(req.password),
        "role": role,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    token = create_token(user_id, req.email, role)
    return {
        "token": token,
        "user": {"id": user_id, "name": req.name, "email": req.email, "role": role},
    }


@app.post("/api/auth/login")
async def login(req: LoginRequest):
    user = find_user(req.email)
    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user["id"], user["email"], user.get("role", "user"))
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "user"),
        },
    }


@app.get("/api/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    db_user = find_user(user["email"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": db_user["id"],
        "name": db_user["name"],
        "email": db_user["email"],
        "role": db_user.get("role", "user"),
        "created_at": db_user.get("created_at"),
    }


@app.get("/api/medicines")
async def supported_medicines():
    medicines = get_supported_medicines()
    return {
        "count": len(medicines),
        "medicines": medicines,
    }


# ── Authenticated endpoints ───────────────────────

@app.post("/api/analyze", response_model=PrescriptionResult)
async def analyze_prescription(
    file: UploadFile = File(...),
    user: dict | None = Depends(get_optional_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    contents = await file.read()
    if len(contents) > MAX_BYTES:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum {settings.MAX_FILE_SIZE_MB} MB.")
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    upload_path = Path(settings.UPLOAD_DIR) / f"{uuid.uuid4().hex}{ext}"
    upload_path.write_bytes(contents)

    try:
        original = Image.open(io.BytesIO(contents)).convert("RGB")
        processed = preprocess_image(contents)
        processed = deskew(auto_rotate(processed))
        original = deskew(auto_rotate(original))

        final_text, ocr_confidence = extract_best_text([processed, original])

        if not final_text.strip():
            result = PrescriptionResult(
                raw_text="",
                medicines=[],
                warnings=[],
                overall_confidence=0.0,
                disclaimer="No text could be extracted. Please try a clearer photo.",
            )
            if user:
                _save_scan_record(user, file.filename, result)
            return result

        medicines = extract_medicines(final_text)
        warnings = run_safety_checks(medicines)

        if medicines:
            med_conf = sum(m.confidence for m in medicines) / len(medicines)
            overall = (ocr_confidence + med_conf) / 2
        else:
            overall = ocr_confidence * 0.5

        result = PrescriptionResult(
            raw_text=final_text,
            medicines=medicines,
            warnings=warnings,
            overall_confidence=round(overall, 2),
        )

        if user:
            _save_scan_record(user, file.filename, result)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing: {str(e)}")
    finally:
        try:
            upload_path.unlink(missing_ok=True)
        except OSError:
            pass


def _save_scan_record(user: dict, filename: str, result: PrescriptionResult):
    save_scan({
        "id": uuid.uuid4().hex,
        "user_id": user["sub"],
        "filename": filename,
        "raw_text": result.raw_text,
        "medicines": [m.model_dump() for m in result.medicines],
        "warnings": [w.model_dump() for w in result.warnings],
        "overall_confidence": result.overall_confidence,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })


@app.get("/api/history")
async def scan_history(user: dict = Depends(get_current_user)):
    scans = get_user_scans(user["sub"])
    scans.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return {"count": len(scans), "scans": scans}


@app.post("/api/feedback")
async def submit_feedback(payload: FeedbackRequest, user: dict = Depends(get_current_user)):
    if not payload.raw_text.strip():
        raise HTTPException(status_code=400, detail="raw_text is required")

    sample = {
        "id": uuid.uuid4().hex,
        "user_id": user["sub"],
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


@app.post("/api/debug/parse-text")
async def debug_parse_text(payload: DebugParseRequest):
    medicines = extract_medicines(payload.raw_text)
    warnings = run_safety_checks(medicines)
    return {
        "medicines": [m.model_dump() for m in medicines],
        "warnings": [w.model_dump() for w in warnings],
        "count": len(medicines),
    }


# ── Admin endpoints ────────────────────────────────

@app.get("/api/admin/dashboard")
async def admin_dashboard(admin: dict = Depends(require_admin)):
    stats = get_scan_stats()
    feedback_path = Path(settings.FEEDBACK_DATASET_PATH)
    feedback_count = 0
    if feedback_path.exists():
        with feedback_path.open("r", encoding="utf-8") as f:
            feedback_count = sum(1 for line in f if line.strip())

    return {
        "users": count_users(),
        "scans": stats,
        "feedback_samples": feedback_count,
        "supported_medicines": len(get_supported_medicines()),
    }


@app.get("/api/admin/users")
async def admin_users(admin: dict = Depends(require_admin)):
    users = get_all_users()
    safe = [
        {
            "id": u["id"],
            "name": u["name"],
            "email": u["email"],
            "role": u.get("role", "user"),
            "created_at": u.get("created_at"),
        }
        for u in users
    ]
    return {"count": len(safe), "users": safe}


@app.get("/api/admin/scans")
async def admin_scans(admin: dict = Depends(require_admin)):
    scans = get_all_scans()
    scans.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return {"count": len(scans), "scans": scans[:100]}


@app.get("/api/feedback/stats")
async def feedback_stats(admin: dict = Depends(require_admin)):
    feedback_path = Path(settings.FEEDBACK_DATASET_PATH)
    if not feedback_path.exists():
        return {"samples": 0}

    total = corrected = confirmed = 0
    with feedback_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
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
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
