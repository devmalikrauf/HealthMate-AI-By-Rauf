# HealthMate AI

AI-powered prescription reader and medication safety checker. Upload a prescription image and get structured medicine information with safety alerts.

## Architecture

```
HealthMate AI/
├── backend/              # Python FastAPI server
│   ├── app/
│   │   ├── main.py             # API endpoints
│   │   ├── config.py           # Settings
│   │   ├── models.py           # Pydantic models
│   │   ├── image_processing.py # Image preprocessing (OpenCV/Pillow)
│   │   ├── ocr_engine.py       # Tesseract OCR integration
│   │   ├── nlp_extractor.py    # Medicine info extraction (NLP/Regex)
│   │   └── safety_engine.py    # Dosage/duplicate/safety checks
│   └── requirements.txt
├── frontend/             # React PWA (Vite)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── components/
│   │       ├── UploadZone.jsx
│   │       ├── MedicineCard.jsx
│   │       ├── WarningsList.jsx
│   │       └── ResultsView.jsx
│   └── package.json
└── README.md
```

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Tesseract OCR** installed on your system
  - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
  - macOS: `brew install tesseract`
  - Linux: `sudo apt install tesseract-ocr`

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

# Copy and edit environment config
cp .env.example .env
# Edit .env with your Tesseract path if needed

# Run the server
python -m app.main
# → API running at http://localhost:8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# → App running at http://localhost:5173
```

Open http://localhost:5173 in your browser. The Vite dev server proxies `/api` requests to the backend.

## How It Works

1. **Upload** — User uploads or photographs a prescription image
2. **Preprocess** — Image is denoised, binarized, deskewed, and enhanced
3. **OCR** — Tesseract extracts text with confidence scores
4. **NLP Extraction** — Regex/NLP engine identifies:
   - Medicine names (from a known database + capitalized word heuristics)
   - Strength (e.g., 500 mg)
   - Dosage (e.g., 1 tablet)
   - Frequency (e.g., 1-0-1, twice daily, BD)
   - Duration (e.g., 5 days)
   - Instructions (e.g., after food)
5. **Safety Checks** — The engine flags:
   - Low-confidence OCR reads
   - Unclear/garbled medicine names
   - Unusually high dosages
   - Duplicate medicines
   - Missing critical information
   - Commonly confused medicine pairs

## API Endpoints

| Method | Endpoint       | Description                          |
|--------|---------------|--------------------------------------|
| GET    | `/api/health`  | Health check                         |
| POST   | `/api/analyze` | Upload image, get structured results |

## Disclaimer

> This tool is for **informational purposes only**. It does NOT replace professional medical advice. Always confirm extracted information with a doctor or pharmacist.
