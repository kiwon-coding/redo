"""문제 이미지 정리 단계 - 인쇄물만 복원.

손글씨/색연필을 제거하고 인쇄물만 남긴 깨끗한 문제 이미지를 생성합니다.
- separated_layers의 print_layer만 사용
- 손글씨 영역을 배경색으로 채우기
- 최종 이미지 저장 및 URL 생성
"""

from analyze.base import PipelineStep
from analyze.models import PipelineContext


class CleanProblemStep(PipelineStep):
    """문제 이미지 정리 단계 - 인쇄물만 복원."""

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        인쇄물만 남긴 깨끗한 문제 이미지를 생성합니다.

        현재는 더미 구현입니다.
        나중에 실제 이미지 처리 로직을 추가합니다.

        Args:
            context: Pipeline 컨텍스트

        Returns:
            업데이트된 Pipeline 컨텍스트
        """
        # 분리된 레이어 가져오기
        separated_layers = context.separated_layers or {}
        print_layer_path = separated_layers.get(
            "print_layer_path", str(context.file_path)
        )

        # 더미 정리 결과
        # 실제 구현 시: print_layer를 사용하여 손글씨 제거된 이미지 생성 및 저장
        context.cleaned_problem = {
            "clean_image_path": print_layer_path,  # 더미: 원본 그대로
            "clean_image_url": f"/uploads/{context.file_id}_clean.png",
            "handwriting_removed": True,  # 더미
            "status": "completed",
        }

        return context

    def get_name(self) -> str:
        """단계 이름 반환."""
        return "clean_problem"
