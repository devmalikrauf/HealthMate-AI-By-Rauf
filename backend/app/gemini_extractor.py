"""Gemini-based AI parser for prescription OCR text."""

import json
import logging
import urllib.request
import urllib.error
from app.config import settings
from app.models import MedicineEntry

logger = logging.getLogger("healthmate")


def extract_medicines_with_gemini(raw_text: str) -> list[MedicineEntry]:
    """Use Gemini 2.5 Flash API to parse raw OCR text into structured medicines.

    Uses standard library urllib to avoid adding external packages.
    """
    if not settings.GEMINI_API_KEY:
        logger.warning("Gemini API key is not configured. Skipping Gemini parser.")
        return []

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    
    prompt = (
        "You are an expert clinical pharmacist. Analyze the following raw OCR text extracted from a medical prescription. "
        "Extract all medicines listed and structure their details accurately.\n\n"
        f"Raw OCR Text:\n{raw_text}\n\n"
        "Rules:\n"
        "1. Extract the name of the medicine exactly as shown or normalize it to a clean brand/generic name.\n"
        "2. Parse the strength (e.g. '500 mg', '40 mg', '10 ml').\n"
        "3. Parse the dosage form (e.g. '1 tablet', '2 capsules', '1 syp').\n"
        "4. Parse frequency (e.g. 'twice daily', 'every 8 hours', '1-0-1', 'OD', 'BD').\n"
        "5. Parse duration (e.g. '5 days', 'ongoing').\n"
        "6. Parse instructions (e.g. 'after food', 'before food').\n"
        "7. Ensure fields are null if not present in the text.\n"
    )

    schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "medicine_name": {"type": "STRING"},
                "strength": {"type": "STRING"},
                "dosage": {"type": "STRING"},
                "frequency": {"type": "STRING"},
                "duration": {"type": "STRING"},
                "instructions": {"type": "STRING"}
            },
            "required": ["medicine_name"]
        }
    }

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema,
            "temperature": 0.1
        }
    }

    headers = {"Content-Type": "application/json"}
    req_data = json.dumps(body).encode("utf-8")
    
    try:
        logger.info("Sending request to Gemini API...")
        req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15.0) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            
            candidates = res_body.get("candidates", [])
            if not candidates:
                logger.error("Gemini API returned no candidates.")
                return []
                
            text_response = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if not text_response:
                logger.error("Gemini API response did not contain text content.")
                return []
                
            parsed_json = json.loads(text_response.strip())
            
            medicines = []
            for item in parsed_json:
                name = item.get("medicine_name")
                if not name or not isinstance(name, str) or len(name.strip()) < 2:
                    continue
                
                medicines.append(MedicineEntry(
                    medicine_name=name.strip(),
                    strength=item.get("strength"),
                    dosage=item.get("dosage"),
                    frequency=item.get("frequency"),
                    duration=item.get("duration"),
                    instructions=item.get("instructions"),
                    confidence=0.95
                ))
            
            logger.info(f"Gemini API extracted {len(medicines)} medicines.")
            return medicines
            
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        logger.error(f"Gemini API HTTP Error ({e.code}): {error_msg}")
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}")
        
    return []
