import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import UploadFile

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_ROOT = BASE_DIR / "uploads"

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg"}


async def save_upload_file(
    file: UploadFile,
    upload_root: Optional[Path] = None,
    file_id: Optional[str] = None,
) -> dict:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Unsupported file type")

    if upload_root is None:
        upload_root = UPLOAD_ROOT

    date_dir = datetime.now().strftime("%Y-%m-%d")
    upload_dir = upload_root / date_dir
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix or ".jpg"
    if file_id is None:
        file_id = str(uuid.uuid4())
    stored_name = f"{file_id}{ext}"
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
        "file_id": file_id,
    }


def get_file_path_by_id(
    file_id: str, upload_root: Optional[Path] = None
) -> Optional[Path]:
    """file_id로 저장된 파일 경로를 찾습니다."""
    if upload_root is None:
        upload_root = UPLOAD_ROOT

    # uploads 디렉토리 하위의 모든 날짜 디렉토리를 검색
    if not upload_root.exists():
        return None

    # 날짜 디렉토리들을 검색 (최신 것부터)
    date_dirs = sorted([d for d in upload_root.iterdir() if d.is_dir()], reverse=True)

    for date_dir in date_dirs:
        # 해당 날짜 디렉토리에서 file_id로 시작하는 파일 찾기
        for file_path in date_dir.glob(f"{file_id}.*"):
            if file_path.is_file():
                return file_path

    return None
