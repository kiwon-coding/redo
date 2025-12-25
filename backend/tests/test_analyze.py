from fastapi.testclient import TestClient
from pathlib import Path
from backend.main import app

client = TestClient(app)


def _get_test_image_bytes():
    """테스트용 이미지 바이너리를 반환합니다."""
    image_path = Path(__file__).parent.parent / "test.png"

    if not image_path.exists():
        # 최소한의 유효한 PNG 헤더
        return (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
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
    assert "analysis" in data
    assert "file_id" in data
    assert data["file_id"] == file_id
    assert "problems_detected" in data["analysis"]
    assert "note" in data["analysis"]


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
