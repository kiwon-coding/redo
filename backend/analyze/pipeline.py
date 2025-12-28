"""이미지 분석 Pipeline 구현."""

from pathlib import Path
from analyze.base import Pipeline
from analyze.models import (
    PipelineContext,
    PipelineResult,
    AnalyzeResult,
    AnswerResult,
)
from analyze.steps import (
    PreprocessStep,
    ExtractProblemStep,
    ExtractAnswerStep,
    PostprocessStep,
)


class AnalyzePipeline(Pipeline):
    """이미지 분석 Pipeline.

    실행 순서:
    1. Preprocess: 사진을 분석 가능한 상태로 변환 (대비, 노이즈 정리)
    2. ExtractProblem: 손글씨 제거하고 문제만 남기기 (인쇄물만 추출)
    3. ExtractAnswer: 손글씨에서 정답만 텍스트로 추출 (OCR)
    4. Postprocess: frontend가 쓰기 좋은 JSON으로 정리
    """

    def __init__(self):
        """Pipeline 초기화 - 단계들을 순서대로 설정."""
        steps = [
            PreprocessStep(),
            ExtractProblemStep(),
            ExtractAnswerStep(),
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
        # postprocess 단계에서 생성한 AnalyzeResult 사용
        analysis_data = (
            final_context.postprocessed.get("result")
            if final_context.postprocessed
            else None
        )

        if analysis_data is None:
            # 더미 데이터로 fallback
            analysis_data = AnalyzeResult(
                clean_problem_image_url="",
                answer=AnswerResult(text="", confidence=0.0),
            )

        result = PipelineResult(
            file_id=file_id,
            analysis=analysis_data,
            context=final_context,
        )

        return result
