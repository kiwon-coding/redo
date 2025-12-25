import uuid
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_ROOT = BASE_DIR / "uploads"

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg"}


async def save_upload_file(file: UploadFile) -> dict:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Unsupported file type")

    date_dir = datetime.now().strftime("%Y-%m-%d")
    upload_dir = UPLOAD_ROOT / date_dir
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix or ".jpg"
    stored_name = f"{uuid.uuid4()}{ext}"
    file_path = upload_dir / stored_name

    size = 0
    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)
            size += len(chunk)

    return {
        "original_filename": file.filename,
        "stored_path": str(file_path),
        "stored_name": stored_name,
        "content_type": file.content_type,
        "size": size,
    }
