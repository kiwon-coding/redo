"""답안 추출 단계 - 필기 중 '답'만 OCR.

손글씨 레이어에서 정답만 추출합니다.
- 숫자/식 인식
- 답 영역 감지 (문제 번호 옆)
- OCR 수행하여 텍스트로 변환
- 신뢰도 계산

중요: 이미지로 저장하지 않고 텍스트 데이터로 저장합니다.
"""

from analyze.base import PipelineStep
from analyze.models import PipelineContext


class ExtractAnswerStep(PipelineStep):
    """답안 추출 단계 - 필기 중 '답'만 OCR."""

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        손글씨 레이어에서 정답만 추출합니다.

        현재는 더미 구현입니다.
        나중에 실제 OCR 모델을 사용하여 숫자/식을 인식합니다.

        Args:
            context: Pipeline 컨텍스트

        Returns:
            업데이트된 Pipeline 컨텍스트
        """
        # 분리된 레이어 가져오기
        separated_layers = context.separated_layers or {}
        # hand_layer_path는 나중에 OCR 수행 시 사용
        # separated_layers.get("hand_layer_path", str(context.file_path))

        # 더미 답안 추출 결과
        # 실제 구현 시: hand_layer에서 답 영역을 찾고 OCR 수행
        context.extracted_answer = {
            "answer_text": "642",  # 더미 답안
            "confidence": 0.92,  # 더미 신뢰도
            "answer_region": None,  # 더미: bbox 정보
            "ocr_method": "dummy",  # "tesseract", "paddleocr", "ml_model"
            "status": "completed",
        }

        return context

    def get_name(self) -> str:
        """단계 이름 반환."""
        return "extract_answer"
