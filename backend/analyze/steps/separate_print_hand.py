"""인쇄물 vs 손글씨 분리 단계 - 핵심 기술.

인쇄된 텍스트/도형과 손글씨/색연필을 분리하는 단계.
- 색상 분석 (인쇄물은 보통 검정/회색, 손글씨는 다양한 색)
- 질감 분석 (인쇄물은 균일, 손글씨는 불규칙)
- 두께 분석 (인쇄물은 일정, 손글씨는 변화)

이 단계가 전체 프로젝트의 기술적 난이도를 결정한다.
"""

from pathlib import Path
from analyze.base import PipelineStep
from analyze.models import PipelineContext


class SeparatePrintHandStep(PipelineStep):
    """인쇄물 vs 손글씨 분리 단계 - 핵심 기술."""

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        인쇄물과 손글씨를 분리합니다.

        현재는 더미 구현입니다.
        나중에 실제 CV 모델을 사용하여 색상, 질감, 두께를 분석합니다.

        Args:
            context: Pipeline 컨텍스트

        Returns:
            업데이트된 Pipeline 컨텍스트
        """
        # 전처리된 이미지 경로 가져오기
        preprocessed = context.preprocessed or {}
        processed_path = preprocessed.get("processed_path", str(context.file_path))

        # 더미 분리 결과
        # 실제 구현 시: 인쇄물 레이어와 손글씨 레이어를 분리하여 이미지로 저장
        context.separated_layers = {
            "print_layer_path": processed_path,  # 더미: 원본 그대로
            "hand_layer_path": processed_path,  # 더미: 원본 그대로
            "separation_method": "dummy",  # "color", "texture", "thickness", "ml_model"
            "confidence": 0.0,  # 더미 구현이므로 0
            "status": "completed",
        }

        return context

    def get_name(self) -> str:
        """단계 이름 반환."""
        return "separate_print_hand"

