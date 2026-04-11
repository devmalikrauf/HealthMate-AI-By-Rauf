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

    def __init__(self):
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.FEEDBACK_DATASET_PATH).parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
