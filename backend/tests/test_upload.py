from fastapi.testclient import TestClient
from pathlib import Path
from backend.main import app

client = TestClient(app)


def test_upload_image_success(tmp_path, monkeypatch):
    # uploads 경로를 임시 디렉토리로 대체
    # 문자열 기반 monkeypatch로 모듈 경로 지정
    monkeypatch.setattr(
        "services.file_storage.UPLOAD_ROOT",
        tmp_path,
    )

    # 테스트 이미지 파일 경로 (backend 디렉토리의 test.png 사용)
    image_path = Path(__file__).parent.parent / "test.png"

    # test.png가 없으면 간단한 PNG 바이너리 생성
    if not image_path.exists():
        # 최소한의 유효한 PNG 헤더
        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
    else:
        png_bytes = image_path.read_bytes()

    response = client.post(
        "/upload",
        files={"file": ("test.png", png_bytes, "image/png")},
    )

    assert response.status_code == 200

    data = response.json()
    assert "file_id" in data
    assert "stored_path" in data
    assert "original_filename" in data

    # 실제 파일이 저장되었는지 확인
    saved_path = Path(data["stored_path"])
    assert saved_path.exists()
