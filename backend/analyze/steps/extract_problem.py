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
from typing import Optional
from analyze.base import PipelineStep
from analyze.models import PipelineContext
from services.file_storage import UPLOAD_ROOT
from analyze.steps.image_processing import (
    remove_handwriting_from_pil,
    HandwritingRemover,
    ThresholdBasedRemover,
    MorphologyBasedRemover,
    AIBasedRemover,
)


class ExtractProblemStep(PipelineStep):
    """문제 추출 단계 - 손글씨 제거하고 문제만 남기기."""

    def __init__(
        self,
        remover: Optional[HandwritingRemover] = None,
        remover_level: int = 1,
    ):
        """
        ExtractProblemStep 초기화.

        Args:
            remover: 사용할 HandwritingRemover 인스턴스
            remover_level: 사용할 레벨 (1: Threshold, 2: Morphology, 3: AI)
                          remover가 None일 때만 사용됨
        """
        if remover is None:
            if remover_level == 1:
                self.remover = ThresholdBasedRemover()
            elif remover_level == 2:
                self.remover = MorphologyBasedRemover()
            elif remover_level == 3:
                self.remover = AIBasedRemover()
            else:
                raise ValueError(
                    f"Invalid remover_level: {remover_level}. " "Must be 1, 2, or 3"
                )
        else:
            self.remover = remover

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        손글씨를 제거하고 인쇄물만 남긴 깨끗한 문제 이미지를 생성합니다.

        처리 방법:
        1. Grayscale 변환 (연필은 흐려지고 인쇄 텍스트는 선명해짐)
        2. Adaptive Threshold (인쇄 텍스트 → 검정, 연필 → 흰색으로 제거)
        3. Noise Removal (작은 노이즈 제거)
        4. 최종 이미지 저장

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

        # 문제 이미지 저장을 위한 새 file_id 생성
        problem_file_id = str(uuid.uuid4())

        # 저장 경로 생성
        date_dir = datetime.now().strftime("%Y-%m-%d")
        upload_dir = UPLOAD_ROOT / date_dir
        upload_dir.mkdir(parents=True, exist_ok=True)

        ext = processed_path.suffix or ".png"
        stored_name = f"{problem_file_id}{ext}"
        problem_image_path = upload_dir / stored_name

        # 이미지 로드 및 필기 제거 처리
        original_img = Image.open(processed_path)

        # 필기 제거 처리 (전략 패턴 사용)
        cleaned_img = remove_handwriting_from_pil(original_img, self.remover)

        # 처리된 이미지 저장
        cleaned_img.save(problem_image_path)

        # 문제 이미지 URL 생성 (frontend에서 사용할 수 있도록)
        problem_image_url = f"/files/{problem_file_id}"  # noqa: E501

        context.extracted_problem = {
            "problem_file_id": problem_file_id,
            "problem_image_path": str(problem_image_path),
            "problem_image_url": problem_image_url,
            "handwriting_removed": True,
            "separation_method": self.remover.get_method_name(),
            "confidence": self.remover.get_confidence(),
            "status": "completed",
        }

        return context

    def get_name(self) -> str:
        """단계 이름 반환."""
        return "extract_problem"
