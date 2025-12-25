"""이미지 분석 Pipeline 구현."""

from pathlib import Path
from analyze.base import Pipeline
from analyze.models import PipelineContext, PipelineResult
from analyze.steps import (
    PreprocessStep,
    DetectAnswerStep,
    DetectWorkStep,
    PostprocessStep,
)


class AnalyzePipeline(Pipeline):
    """이미지 분석 Pipeline.

    실행 순서:
    1. Preprocess: 사진을 분석 가능한 상태로 변환
    2. DetectAnswer: 정답이 써 있는 위치 찾기
    3. DetectWork: 풀이 과정이 있는 영역 찾기
    4. Postprocess: 최종 결과 정리
    """

    def __init__(self):
        """Pipeline 초기화 - 단계들을 순서대로 설정."""
        steps = [
            PreprocessStep(),
            DetectAnswerStep(),
            DetectWorkStep(),
            PostprocessStep(),
        ]
        super().__init__(steps)

    async def analyze(self, file_id: str, file_path: Path) -> PipelineResult:
        """
        이미지 분석 실행.

        Args:
            file_id: 파일 ID
            file_path: 파일 경로

        Returns:
            Pipeline 결과
        """
        # 초기 컨텍스트 생성
        context = PipelineContext(
            file_id=file_id,
            file_path=file_path,
        )

        # Pipeline 실행
        final_context = await self.run(context)

        # 최종 결과 생성 (API 응답 형식에 맞춤)
        # postprocess 단계에서 생성한 for_print 데이터 사용
        analysis_data = final_context.postprocessed.get("for_print", {}) if final_context.postprocessed else {}

        result = PipelineResult(
            file_id=file_id,
            analysis=analysis_data,
            context=final_context,
        )

        return result

