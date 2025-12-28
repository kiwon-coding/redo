"""Pipeline 통합 테스트 - 실제 API 엔드포인트와 함께."""

import pytest
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


class TestPipelineIntegration:
    """Pipeline과 API 엔드포인트 통합 테스트."""

    def test_full_workflow(self, tmp_path, monkeypatch):
        """전체 워크플로우 테스트: 업로드 -> 분석."""
        # uploads 경로를 임시 디렉토리로 대체
        monkeypatch.setattr(
            "services.file_storage.UPLOAD_ROOT",
            tmp_path,
        )

        png_bytes = _get_test_image_bytes()

        # 1. 파일 업로드
        upload_response = client.post(
            "/upload",
            files={"file": ("test.png", png_bytes, "image/png")},
        )
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        file_id = upload_data["file_id"]
        assert "stored_path" in upload_data
        assert "original_filename" in upload_data

        # 2. 분석 요청
        analyze_response = client.post(
            "/analyze",
            json={"file_id": file_id},
        )
        assert analyze_response.status_code == 200
        analyze_data = analyze_response.json()

        # 3. 응답 구조 검증
        assert "message" in analyze_data
        assert analyze_data["message"] == "분석 완료"
        assert "file_id" in analyze_data
        assert analyze_data["file_id"] == file_id
        # 실제 API 응답 구조에 맞게 수정
        assert "problem_image_file_id" in analyze_data
        assert "problem_image_url" in analyze_data
        assert "answer" in analyze_data
        assert "text" in analyze_data["answer"]
        assert "confidence" in analyze_data["answer"]
        assert isinstance(analyze_data["answer"]["confidence"], (int, float))

    def test_analyze_response_structure(self, tmp_path, monkeypatch):
        """분석 응답의 구조가 올바른지 테스트."""
        monkeypatch.setattr(
            "services.file_storage.UPLOAD_ROOT",
            tmp_path,
        )

        png_bytes = _get_test_image_bytes()

        # 파일 업로드
        upload_response = client.post(
            "/upload",
            files={"file": ("test.png", png_bytes, "image/png")},
        )
        file_id = upload_response.json()["file_id"]

        # 분석 요청
        response = client.post(
            "/analyze",
            json={"file_id": file_id},
        )

        assert response.status_code == 200
        data = response.json()

        # 필수 필드 확인 (실제 API 응답 구조에 맞게 수정)
        required_fields = ["message", "file_id", "problem_image_file_id", "problem_image_url", "answer"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # answer 필드 구조 확인
        assert isinstance(data["answer"], dict)
        assert "text" in data["answer"]
        assert "confidence" in data["answer"]

    def test_multiple_analyses_same_file(self, tmp_path, monkeypatch):
        """같은 파일에 대해 여러 번 분석 요청 테스트."""
        monkeypatch.setattr(
            "services.file_storage.UPLOAD_ROOT",
            tmp_path,
        )

        png_bytes = _get_test_image_bytes()

        # 파일 업로드
        upload_response = client.post(
            "/upload",
            files={"file": ("test.png", png_bytes, "image/png")},
        )
        file_id = upload_response.json()["file_id"]

        # 여러 번 분석 요청
        for i in range(3):
            response = client.post(
                "/analyze",
                json={"file_id": file_id},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["file_id"] == file_id
            # 실제 API 응답 구조에 맞게 수정
            assert "problem_image_file_id" in data
            assert "answer" in data

    def test_analyze_with_different_file_ids(self, tmp_path, monkeypatch):
        """다른 파일 ID로 분석 요청 테스트."""
        monkeypatch.setattr(
            "services.file_storage.UPLOAD_ROOT",
            tmp_path,
        )

        png_bytes = _get_test_image_bytes()

        # 여러 파일 업로드
        file_ids = []
        for i in range(3):
            upload_response = client.post(
                "/upload",
                files={"file": (f"test_{i}.png", png_bytes, "image/png")},
            )
            file_ids.append(upload_response.json()["file_id"])

        # 각 파일에 대해 분석
        for file_id in file_ids:
            response = client.post(
                "/analyze",
                json={"file_id": file_id},
            )
            assert response.status_code == 200
            assert response.json()["file_id"] == file_id
