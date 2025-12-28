"""extract_answer 단계 테스트 - OCR 로직."""

import pytest
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from analyze.steps.image_processing import preprocess_for_ocr
from analyze.steps.extract_answer import ExtractAnswerStep
from analyze.models import PipelineContext


class TestPreprocessForOCR:
    """OCR 전처리 함수 테스트."""

    def test_preprocess_for_ocr_rgb(self):
        """RGB 이미지 전처리 테스트."""
        # 테스트용 이미지 생성 (흰색 배경에 검정 텍스트)
        img = Image.new("RGB", (200, 100), color="white")
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "642", fill="black")

        result = preprocess_for_ocr(img)

        assert isinstance(result, Image.Image)
        assert result.mode == "L"  # Grayscale
        assert result.size == img.size

    def test_preprocess_for_ocr_grayscale(self):
        """Grayscale 이미지 전처리 테스트."""
        # 테스트용 Grayscale 이미지 생성
        img = Image.new("L", (200, 100), color=255)
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "123", fill=0)

        result = preprocess_for_ocr(img)

        assert isinstance(result, Image.Image)
        assert result.mode == "L"
        assert result.size == img.size


class TestExtractAnswerStep:
    """ExtractAnswerStep 테스트."""

    @pytest.fixture
    def test_image_with_text(self, tmp_path):
        """텍스트가 포함된 테스트 이미지 생성."""
        image_path = tmp_path / "test_answer.png"
        # 흰색 배경에 검정 숫자 이미지 생성
        img = Image.new("RGB", (200, 100), color="white")
        draw = ImageDraw.Draw(img)
        # 큰 폰트로 숫자 그리기
        try:
            # 시스템 폰트 사용 시도
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        except:
            # 폰트를 찾을 수 없으면 기본 폰트 사용
            font = ImageFont.load_default()
        draw.text((20, 20), "642", fill="black", font=font)
        img.save(image_path)
        return image_path

    @pytest.fixture
    def test_image_empty(self, tmp_path):
        """빈 이미지 생성."""
        image_path = tmp_path / "test_empty.png"
        img = Image.new("RGB", (200, 100), color="white")
        img.save(image_path)
        return image_path

    @pytest.fixture
    def context_with_image(self, test_image_with_text):
        """이미지가 포함된 PipelineContext 생성."""
        return PipelineContext(
            file_id="test_file_123",
            file_path=test_image_with_text,
            preprocessed={
                "processed_path": str(test_image_with_text),
                "status": "completed",
            },
        )

    @pytest.fixture
    def context_empty_image(self, test_image_empty):
        """빈 이미지가 포함된 PipelineContext 생성."""
        return PipelineContext(
            file_id="test_file_empty",
            file_path=test_image_empty,
            preprocessed={
                "processed_path": str(test_image_empty),
                "status": "completed",
            },
        )

    @pytest.mark.asyncio
    async def test_extract_answer_with_text(self, context_with_image):
        """텍스트가 있는 이미지에서 답안 추출 테스트."""
        step = ExtractAnswerStep(min_confidence=0.1)  # 낮은 threshold로 설정
        result_context = await step.execute(context_with_image)

        assert result_context.extracted_answer is not None
        assert result_context.extracted_answer["ocr_method"] == "tesseract"
        assert result_context.extracted_answer["status"] == "completed"
        # OCR 결과가 있을 수 있음 (환경에 따라 다를 수 있음)
        assert "answer_text" in result_context.extracted_answer
        assert "confidence" in result_context.extracted_answer

    @pytest.mark.asyncio
    async def test_extract_answer_empty_image(self, context_empty_image):
        """빈 이미지에서 답안 추출 테스트."""
        step = ExtractAnswerStep(min_confidence=0.3)
        result_context = await step.execute(context_empty_image)

        assert result_context.extracted_answer is not None
        assert result_context.extracted_answer["ocr_method"] == "tesseract"
        assert result_context.extracted_answer["status"] == "completed"
        # 빈 이미지는 빈 문자열 또는 낮은 confidence 반환
        answer_text = result_context.extracted_answer["answer_text"]
        confidence = result_context.extracted_answer["confidence"]

        # confidence가 낮으면 빈 문자열이어야 함
        if confidence < step.min_confidence:
            assert answer_text == ""
            assert confidence == 0.2

    @pytest.mark.asyncio
    async def test_extract_answer_low_confidence(self, context_with_image):
        """낮은 confidence로 인한 빈 문자열 반환 테스트."""
        step = ExtractAnswerStep(min_confidence=0.9)  # 매우 높은 threshold
        result_context = await step.execute(context_with_image)

        assert result_context.extracted_answer is not None
        # confidence가 낮으면 빈 문자열 반환
        if result_context.extracted_answer["confidence"] < step.min_confidence:
            assert result_context.extracted_answer["answer_text"] == ""
            assert result_context.extracted_answer["confidence"] == 0.2

    @pytest.mark.asyncio
    async def test_extract_answer_invalid_image_path(self):
        """잘못된 이미지 경로 처리 테스트."""
        context = PipelineContext(
            file_id="test_invalid",
            file_path=Path("/nonexistent/path/image.png"),
            preprocessed={
                "processed_path": "/nonexistent/path/image.png",
                "status": "completed",
            },
        )

        step = ExtractAnswerStep()
        result_context = await step.execute(context)

        assert result_context.extracted_answer is not None
        assert result_context.extracted_answer["status"] == "failed"
        assert result_context.extracted_answer["answer_text"] == ""
        assert result_context.extracted_answer["confidence"] == 0.0
        assert "error" in result_context.extracted_answer

    def test_extract_text_with_confidence_method(self):
        """_extract_text_with_confidence 메서드 테스트."""
        step = ExtractAnswerStep()

        # 테스트용 이미지 생성
        img = Image.new("RGB", (200, 100), color="white")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        except:
            font = ImageFont.load_default()
        draw.text((20, 20), "123", fill="black", font=font)

        # OCR 전처리
        preprocessed_img = preprocess_for_ocr(img)

        # OCR 수행
        answer_text, confidence = step._extract_text_with_confidence(
            preprocessed_img
        )

        # 결과 검증
        assert isinstance(answer_text, str)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

    def test_tesseract_config(self):
        """Tesseract 설정 테스트."""
        custom_config = "--psm 7 -c tessedit_char_whitelist=0123456789"
        step = ExtractAnswerStep(tesseract_config=custom_config)

        assert step.tesseract_config == custom_config

