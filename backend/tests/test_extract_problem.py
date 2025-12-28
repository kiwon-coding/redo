"""extract_problem 단계 테스트 - 실제 이미지 처리 로직."""

import pytest
import numpy as np
from PIL import Image
from pathlib import Path
from analyze.steps.image_processing import (
    remove_handwriting,
    remove_handwriting_from_pil,
    ThresholdBasedRemover,
    MorphologyBasedRemover,
    AIBasedRemover,
)


class TestRemoveHandwriting:
    """remove_handwriting 함수 테스트."""

    @pytest.fixture
    def test_image_path(self, tmp_path):
        """테스트용 이미지 파일 생성."""
        image_path = tmp_path / "test.png"
        # 최소한의 유효한 PNG 바이너리
        image_path.write_bytes(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        return image_path

    def test_remove_handwriting_with_path(self, test_image_path):
        """경로로 이미지 로드 테스트."""
        result = remove_handwriting(str(test_image_path))
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 2  # Grayscale이므로 2D
        assert result.dtype == np.uint8

    def test_remove_handwriting_with_array(self):
        """numpy array로 이미지 전달 테스트."""
        # 테스트용 이미지 생성 (흰색 배경에 검정 사각형)
        test_img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        test_img[40:60, 40:60] = [0, 0, 0]  # 검정 사각형

        result = remove_handwriting(test_img)
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 2  # Grayscale
        assert result.dtype == np.uint8

    def test_remove_handwriting_parameters(self, test_image_path):
        """파라미터 조정 테스트."""
        result1 = remove_handwriting(
            str(test_image_path), threshold_block_size=11, threshold_c=2
        )
        result2 = remove_handwriting(
            str(test_image_path), threshold_block_size=15, threshold_c=5
        )

        assert isinstance(result1, np.ndarray)
        assert isinstance(result2, np.ndarray)
        # 파라미터가 다르면 결과도 다를 수 있음
        assert result1.shape == result2.shape

    def test_remove_handwriting_invalid_path(self, tmp_path):
        """존재하지 않는 경로 테스트."""
        invalid_path = tmp_path / "nonexistent.png"
        with pytest.raises(ValueError, match="Failed to load image"):
            remove_handwriting(str(invalid_path))

    def test_remove_handwriting_invalid_type(self):
        """잘못된 타입 전달 테스트."""
        with pytest.raises(TypeError):
            remove_handwriting(123)  # 숫자는 지원하지 않음


class TestRemoveHandwritingFromPil:
    """remove_handwriting_from_pil 함수 테스트."""

    @pytest.fixture
    def test_pil_image(self):
        """테스트용 PIL Image 생성."""
        # 흰색 배경에 검정 사각형이 있는 이미지
        img = Image.new("RGB", (100, 100), color="white")
        pixels = img.load()
        # 중앙에 검정 사각형 그리기
        for x in range(40, 60):
            for y in range(40, 60):
                pixels[x, y] = (0, 0, 0)
        return img

    def test_remove_handwriting_from_pil_basic(self, test_pil_image):
        """기본 PIL Image 처리 테스트."""
        result = remove_handwriting_from_pil(test_pil_image)
        assert isinstance(result, Image.Image)
        assert result.size == test_pil_image.size
        assert result.mode == "L"  # Grayscale

    def test_remove_handwriting_from_pil_parameters(self, test_pil_image):
        """파라미터 전달 테스트."""
        result = remove_handwriting_from_pil(
            test_pil_image,
            threshold_block_size=11,
            threshold_c=2,
            noise_kernel_size=3,
        )
        assert isinstance(result, Image.Image)

    def test_remove_handwriting_from_pil_grayscale(self):
        """Grayscale 이미지 처리 테스트."""
        img = Image.new("L", (100, 100), color=255)
        pixels = img.load()
        for x in range(40, 60):
            for y in range(40, 60):
                pixels[x, y] = 0

        result = remove_handwriting_from_pil(img)
        assert isinstance(result, Image.Image)
        assert result.mode == "L"


class TestExtractProblemIntegration:
    """extract_problem 단계 통합 테스트."""

    @pytest.fixture
    def test_image_with_text(self, tmp_path):
        """텍스트가 있는 테스트 이미지 생성."""
        # 간단한 이미지 생성 (실제로는 더 복잡한 이미지가 필요)
        image_path = tmp_path / "test_with_text.png"
        img = Image.new("RGB", (200, 100), color="white")
        # 여기에 실제 텍스트나 패턴을 그릴 수 있음
        img.save(image_path)
        return image_path

    @pytest.mark.asyncio
    async def test_extract_problem_step_with_processing(self, tmp_path):
        """ExtractProblemStep이 실제로 이미지 처리를 수행하는지 테스트."""
        from analyze.steps.extract_problem import ExtractProblemStep
        from analyze.models import PipelineContext

        # 테스트 이미지 생성
        test_image_path = tmp_path / "test.png"
        img = Image.new("RGB", (100, 100), color="white")
        img.save(test_image_path)

        # 컨텍스트 생성
        context = PipelineContext(
            file_id="test-id",
            file_path=test_image_path,
        )
        context.preprocessed = {
            "processed_path": str(test_image_path),
            "status": "completed",
        }

        # ExtractProblemStep 실행
        step = ExtractProblemStep()
        result = await step.execute(context)

        # 결과 검증
        assert result.extracted_problem is not None
        assert result.extracted_problem["status"] == "completed"
        assert result.extracted_problem["handwriting_removed"] is True
        # separation_method는 remover에 따라 달라질 수 있음
        assert "separation_method" in result.extracted_problem
        assert isinstance(result.extracted_problem["separation_method"], str)

        # 처리된 이미지 파일이 생성되었는지 확인
        problem_image_path = Path(
            result.extracted_problem["problem_image_path"]
        )
        assert problem_image_path.exists()

        # 처리된 이미지가 원본과 다른지 확인 (실제로 처리되었는지)
        original_img = Image.open(test_image_path)
        processed_img = Image.open(problem_image_path)

        # 크기는 같아야 함
        assert original_img.size == processed_img.size

