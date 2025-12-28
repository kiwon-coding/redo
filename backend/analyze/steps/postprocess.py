"""후처리 단계 - frontend가 쓰기 좋은 JSON으로 정리.

AI 결과를 '서비스 데이터'로 바꾸는 단계.
- clean_problem_image_url 생성
- answer.text, answer.confidence 정리
- 최종 AnalyzeResult 형식으로 변환
"""

from analyze.base import PipelineStep
from analyze.models import PipelineContext, AnalyzeResult, AnswerResult


class PostprocessStep(PipelineStep):
    """후처리 단계 - 최종 결과 정리 및 포맷팅."""

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        모든 단계의 결과를 종합하여 최종 결과 생성.

        frontend가 사용하기 좋은 형식으로 정리합니다.

        Args:
            context: Pipeline 컨텍스트

        Returns:
            업데이트된 Pipeline 컨텍스트
        """
        # 추출된 문제 이미지 정보 가져오기
        extracted_problem = context.extracted_problem or {}
        problem_image_url = extracted_problem.get("problem_image_url", "")

        # 추출된 답안 정보 가져오기
        extracted_answer = context.extracted_answer or {}
        answer_text = extracted_answer.get("answer_text", "")
        answer_confidence = extracted_answer.get("confidence", 0.0)

        # 최종 결과 생성 (AnalyzeResult 형식)
        result = AnalyzeResult(
            clean_problem_image_url=problem_image_url,
            answer=AnswerResult(
                text=answer_text,
                confidence=answer_confidence,
            ),
        )

        context.postprocessed = {
            "result": result,
            "status": "completed",
        }

        return context

    def get_name(self) -> str:
        """단계 이름 반환."""
        return "postprocess"
