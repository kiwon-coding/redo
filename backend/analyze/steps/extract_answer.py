"""답안 추출 단계 - 손글씨에서 정답만 텍스트로 추출.

손글씨 부분에서 정답만 추출하여 텍스트로 변환합니다.
- 손글씨 영역 감지
- 답 영역 감지 (문제 번호 옆)
- 숫자/식 OCR 수행
- 텍스트로 변환 및 신뢰도 계산

중요: 이미지로 저장하지 않고 텍스트 데이터로만 저장합니다.
"""

from analyze.base import PipelineStep
from analyze.models import PipelineContext


class ExtractAnswerStep(PipelineStep):
    """답안 추출 단계 - 손글씨에서 정답만 텍스트로 추출."""

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        손글씨 부분에서 정답만 추출하여 텍스트로 변환합니다.

        현재는 더미 구현입니다.
        나중에 실제 OCR 모델을 사용하여:
        1. 손글씨 영역 감지
        2. 답 영역 감지 (문제 번호 옆)
        3. 숫자/식 OCR 수행
        4. 텍스트로 변환

        Args:
            context: Pipeline 컨텍스트

        Returns:
            업데이트된 Pipeline 컨텍스트
        """
        # 전처리된 이미지 경로 가져오기 (손글씨가 포함된 원본)
        # 나중에 실제 구현 시: 손글씨 영역만 추출하여 OCR 수행
        # preprocessed = context.preprocessed or {}
        # processed_path = preprocessed.get(
        #     "processed_path", str(context.file_path)
        # )

        # 더미 답안 추출 결과
        # 실제 구현 시: 손글씨 영역에서 답 영역을 찾고 OCR 수행
        context.extracted_answer = {
            "answer_text": "642",  # 더미 답안
            "confidence": 0.92,  # 더미 신뢰도
            "answer_region": None,  # 더미: bbox 정보 (답 영역 좌표)
            "ocr_method": "dummy",  # "tesseract", "paddleocr", "ml_model"
            "status": "completed",
        }

        return context

    def get_name(self) -> str:
        """단계 이름 반환."""
        return "extract_answer"
