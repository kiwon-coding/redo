from fastapi.testclient import TestClient
from pathlib import Path
from io import BytesIO
from PIL import Image
from backend.main import app

client = TestClient(app)


def _get_test_image_bytes():
    """테스트용 이미지 바이너리를 반환합니다."""
    image_path = Path(__file__).parent.parent / "test.png"

    if not image_path.exists():
        # PIL Image를 사용해서 실제 이미지 생성
        img = Image.new("RGB", (100, 100), color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    else:
        return image_path.read_bytes()


def test_analyze_with_file_id(tmp_path, monkeypatch):
    # uploads 경로를 임시 디렉토리로 대체
    monkeypatch.setattr(
        "services.file_storage.UPLOAD_ROOT",
        tmp_path,
    )

    # 먼저 파일을 업로드해서 file_id를 얻음
    png_bytes = _get_test_image_bytes()

    # 파일 업로드
    upload_response = client.post(
        "/upload",
        files={"file": ("test.png", png_bytes, "image/png")},
    )
    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]

    # file_id로 분석 요청
    response = client.post(
        "/analyze",
        json={"file_id": file_id},
    )

    assert response.status_code == 200
    data = response.json()
    # 실제 API 응답 구조에 맞게 수정
    assert "file_id" in data
    assert data["file_id"] == file_id
    assert "problem_image_file_id" in data
    assert "problem_image_url" in data
    assert "answer" in data
    assert "text" in data["answer"]
    assert "confidence" in data["answer"]


def test_analyze_with_invalid_file_id(tmp_path, monkeypatch):
    # uploads 경로를 임시 디렉토리로 대체
    monkeypatch.setattr(
        "services.file_storage.UPLOAD_ROOT",
        tmp_path,
    )

    # 존재하지 않는 file_id로 분석 요청
    response = client.post(
        "/analyze",
        json={"file_id": "non-existent-id"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
