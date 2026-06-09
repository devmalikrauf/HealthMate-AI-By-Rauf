import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    TESSERACT_CMD: str = os.getenv(
        "TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_ORIGINS: list[str] = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")
    FEEDBACK_DATASET_PATH: str = os.getenv(
        "FEEDBACK_DATASET_PATH", "./data/feedback.jsonl"
    )
    JWT_SECRET: str = os.getenv("JWT_SECRET", "healthmate-dev-secret-change-in-prod")
    JWT_EXPIRY_HOURS: int = int(os.getenv("JWT_EXPIRY_HOURS", "72"))
    DB_DIR: str = os.getenv("DB_DIR", "./data")
    DB_PATH: str = os.getenv("DB_PATH", str(Path(DB_DIR) / "healthmate.db"))
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY", None)

    def __init__(self):
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.FEEDBACK_DATASET_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(self.DB_DIR).mkdir(parents=True, exist_ok=True)


settings = Settings()
