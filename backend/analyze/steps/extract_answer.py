"""답안 추출 단계 - 손글씨에서 정답만 텍스트로 추출.

손글씨 부분에서 정답만 추출하여 텍스트로 변환합니다.
- 손글씨 영역 감지
- 답 영역 감지 (문제 번호 옆)
- 숫자/식 OCR 수행
- 텍스트로 변환 및 신뢰도 계산

중요: 이미지로 저장하지 않고 텍스트 데이터로만 저장합니다.
"""

from typing import Tuple
import pytesseract
from PIL import Image
from analyze.base import PipelineStep
from analyze.models import PipelineContext
from analyze.steps.image_processing import preprocess_for_ocr


class ExtractAnswerStep(PipelineStep):
    """답안 추출 단계 - 손글씨에서 정답만 텍스트로 추출."""

    def __init__(
        self,
        min_confidence: float = 0.3,
        tesseract_config: str = (
            "--psm 6 -c tessedit_char_whitelist=0123456789+-×÷=()[]"
        ),
    ):
        """
        Args:
            min_confidence: 최소 신뢰도 (이보다 낮으면 빈 문자열 반환)
            tesseract_config: Tesseract OCR 설정
                - --psm 6: 단일 블록 텍스트
                - tessedit_char_whitelist: 숫자와 기본 수학 기호만
        """
        self.min_confidence = min_confidence
        self.tesseract_config = tesseract_config

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        손글씨 부분에서 정답만 추출하여 텍스트로 변환합니다.

        처리 과정:
        1. 전처리된 이미지 로드 (손글씨가 포함된 원본)
        2. OCR 전처리 (색상 반전, 대비 증가)
        3. pytesseract로 OCR 수행 (숫자/기호만)
        4. confidence 확인하고 낮으면 빈 문자열 반환

        Args:
            context: Pipeline 컨텍스트

        Returns:
            업데이트된 Pipeline 컨텍스트
        """
        # 전처리된 이미지 경로 가져오기 (손글씨가 포함된 원본)
        preprocessed = context.preprocessed or {}
        processed_path = preprocessed.get("processed_path", str(context.file_path))

        # 이미지 로드
        try:
            original_img = Image.open(processed_path)
        except Exception as e:
            # 이미지 로드 실패 시 빈 결과 반환
            context.extracted_answer = {
                "answer_text": "",
                "confidence": 0.0,
                "ocr_method": "tesseract",
                "status": "failed",
                "error": str(e),
            }
            return context

        # OCR 전처리 (색상 반전, 대비 증가)
        preprocessed_img = preprocess_for_ocr(original_img)

        # OCR 수행
        answer_text, confidence = self._extract_text_with_confidence(preprocessed_img)

        # confidence가 낮으면 빈 문자열 반환
        if confidence < self.min_confidence:
            answer_text = ""
            confidence = 0.2  # 프론트에서 "직접 입력하세요" 유도

        context.extracted_answer = {
            "answer_text": answer_text,
            "confidence": confidence,
            "ocr_method": "tesseract",
            "status": "completed",
        }

        return context

    def _extract_text_with_confidence(self, image: Image.Image) -> Tuple[str, float]:
        """
        pytesseract를 사용하여 텍스트와 confidence를 추출합니다.

        Args:
            image: OCR 전처리된 PIL Image

        Returns:
            (추출된 텍스트, 평균 confidence)
        """
        try:
            # pytesseract로 OCR 수행 (숫자/기호만)
            # image_to_data를 사용하여 confidence 정보도 함께 가져옴
            data = pytesseract.image_to_data(
                image,
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT,
            )

            # 텍스트 추출
            texts = []
            confidences = []

            for i, text in enumerate(data["text"]):
                if text.strip():  # 빈 문자열이 아닌 경우만
                    texts.append(text.strip())
                    conf = float(data["conf"][i])
                    if conf > 0:  # confidence가 0보다 큰 경우만
                        confidences.append(conf)

            # 전체 텍스트 합치기
            answer_text = " ".join(texts).strip()

            # 평균 confidence 계산
            if confidences:
                avg_confidence = sum(confidences) / len(confidences) / 100.0
            else:
                avg_confidence = 0.0

            # confidence가 없거나 너무 낮으면 image_to_string으로 재시도
            if not answer_text or avg_confidence < 0.1:
                answer_text = pytesseract.image_to_string(
                    image, config=self.tesseract_config
                ).strip()
                # image_to_string은 confidence를 반환하지 않으므로
                # 기본값 사용
                if answer_text:
                    avg_confidence = 0.5  # 기본 confidence
                else:
                    avg_confidence = 0.0

            return answer_text, avg_confidence

        except Exception:
            # OCR 실패 시 빈 결과 반환
            return "", 0.0

    def get_name(self) -> str:
        """단계 이름 반환."""
        return "extract_answer"
