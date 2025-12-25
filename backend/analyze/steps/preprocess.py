"""전처리 단계 - 사진을 분석 가능한 상태로 만든다.

카메라로 찍은 사진을 '스캔본'처럼 만드는 단계.
- 회전 보정
- 밝기 / 대비 보정
- 여백 제거
- 해상도 정규화
"""

from analyze.base import PipelineStep
from analyze.models import PipelineContext


class PreprocessStep(PipelineStep):
    """이미지 전처리 단계 - 사진을 분석 가능한 상태로 변환."""

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        이미지 파일 검증 및 전처리.

        현재는 더미 구현으로 원본 경로를 그대로 넘깁니다.
        나중에 실제 이미지 처리 로직을 추가합니다.

        Args:
            context: Pipeline 컨텍스트

        Returns:
            업데이트된 Pipeline 컨텍스트
        """
        file_path = context.file_path

        # 파일 존재 확인
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # 파일 크기 확인
        file_size = file_path.stat().st_size
        if file_size == 0:
            raise ValueError(f"File is empty: {file_path}")

        # 이미지 형식 검증
        allowed_extensions = {".png", ".jpg", ".jpeg"}
        if file_path.suffix.lower() not in allowed_extensions:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        # 더미 전처리 결과
        # 실제 구현 시: 회전 보정, 밝기/대비 보정, 여백 제거, 해상도 정규화 수행
        context.preprocessed = {
            "original_path": str(file_path),
            "processed_path": str(file_path),  # 현재는 원본 그대로
            "file_size": file_size,
            "file_format": file_path.suffix.lower(),
            "width": None,  # 실제 구현 시 이미지 로드하여 설정
            "height": None,  # 실제 구현 시 이미지 로드하여 설정
            "rotation_corrected": False,  # 회전 보정 여부
            "brightness_adjusted": False,  # 밝기 보정 여부
            "contrast_adjusted": False,  # 대비 보정 여부
            "margins_removed": False,  # 여백 제거 여부
            "resolution_normalized": False,  # 해상도 정규화 여부
            "status": "completed",
        }

        return context

    def get_name(self) -> str:
        """단계 이름 반환."""
        return "preprocess"
