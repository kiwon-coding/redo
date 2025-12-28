"""문제 추출 단계 - 손글씨 제거하고 문제만 남기기.

인쇄물과 손글씨를 분리한 후, 손글씨를 제거하고 인쇄물만 남긴
깨끗한 문제 이미지를 생성합니다.

- 인쇄물 vs 손글씨 분리 (색상, 질감, 두께 분석)
- 손글씨 영역 제거
- 최종 문제 이미지 저장 및 URL 생성
"""

import uuid
from pathlib import Path
from datetime import datetime
from PIL import Image
from analyze.base import PipelineStep
from analyze.models import PipelineContext
from services.file_storage import UPLOAD_ROOT


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
        processed_path = Path(
            preprocessed.get("processed_path", str(context.file_path))
        )

        # 더미 구현: 원본 이미지를 복사하여 문제 이미지로 저장
        # 실제 구현 시:
        # 1. 인쇄물과 손글씨를 분리하여 레이어 생성
        # 2. 손글씨 영역을 제거하고 인쇄물만 남김
        # 3. 깨끗한 문제 이미지로 저장

        # 문제 이미지 저장을 위한 새 file_id 생성
        problem_file_id = str(uuid.uuid4())

        # 저장 경로 생성
        date_dir = datetime.now().strftime("%Y-%m-%d")
        upload_dir = UPLOAD_ROOT / date_dir
        upload_dir.mkdir(parents=True, exist_ok=True)

        ext = processed_path.suffix or ".png"
        stored_name = f"{problem_file_id}{ext}"
        problem_image_path = upload_dir / stored_name

        # 더미: 원본 이미지를 복사 (실제로는 손글씨 제거 처리)
        img = Image.open(processed_path)
        img.save(problem_image_path)

        # 문제 이미지 URL 생성 (frontend에서 사용할 수 있도록)
        problem_image_url = f"/files/{problem_file_id}"  # noqa: E501

        context.extracted_problem = {
            "problem_file_id": problem_file_id,
            "problem_image_path": str(problem_image_path),
            "problem_image_url": problem_image_url,
            "handwriting_removed": True,  # 더미
            "separation_method": "dummy",  # noqa: E501
            "confidence": 0.0,  # 더미 구현이므로 0
            "status": "completed",
        }

        return context

    def get_name(self) -> str:
        """단계 이름 반환."""
        return "extract_problem"
