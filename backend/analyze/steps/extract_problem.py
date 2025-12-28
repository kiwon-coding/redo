"""문제 추출 단계 - 손글씨 제거하고 문제만 남기기.

인쇄물과 손글씨를 분리한 후, 손글씨를 제거하고 인쇄물만 남긴 
깨끗한 문제 이미지를 생성합니다.

- 인쇄물 vs 손글씨 분리 (색상, 질감, 두께 분석)
- 손글씨 영역 제거
- 최종 문제 이미지 저장 및 URL 생성
"""

from analyze.base import PipelineStep
from analyze.models import PipelineContext


class ExtractProblemStep(PipelineStep):
    """문제 추출 단계 - 손글씨 제거하고 문제만 남기기."""

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        손글씨를 제거하고 인쇄물만 남긴 깨끗한 문제 이미지를 생성합니다.

        현재는 더미 구현입니다.
        나중에 실제 CV 모델을 사용하여:
        1. 인쇄물과 손글씨를 분리 (색상, 질감, 두께 분석)
        2. 손글씨 영역을 배경색으로 채우기
        3. 최종 이미지 저장

        Args:
            context: Pipeline 컨텍스트

        Returns:
            업데이트된 Pipeline 컨텍스트
        """
        # 전처리된 이미지 경로 가져오기
        preprocessed = context.preprocessed or {}
        processed_path = preprocessed.get("processed_path", str(context.file_path))

        # 더미 추출 결과
        # 실제 구현 시:
        # 1. 인쇄물과 손글씨를 분리하여 레이어 생성
        # 2. 손글씨 영역을 제거하고 인쇄물만 남김
        # 3. 깨끗한 문제 이미지로 저장
        context.extracted_problem = {
            "problem_image_path": processed_path,  # 더미: 원본 그대로
            "problem_image_url": f"/uploads/{context.file_id}_problem.png",
            "handwriting_removed": True,  # 더미
            "separation_method": "dummy",  # "color", "texture", "thickness", "ml_model"
            "confidence": 0.0,  # 더미 구현이므로 0
            "status": "completed",
        }

        return context

    def get_name(self) -> str:
        """단계 이름 반환."""
        return "extract_problem"

