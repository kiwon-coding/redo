"""후처리 단계 - 사람과 시스템이 쓰기 좋은 결과로 정리.

AI 결과를 '서비스 데이터'로 바꾸는 단계.
- 문제 단위로 묶기
- 오답 여부 정리
- 프린트용 / 해답지용 데이터 생성
"""

from analyze.base import PipelineStep
from analyze.models import PipelineContext


class PostprocessStep(PipelineStep):
    """후처리 단계 - 최종 결과 정리 및 포맷팅."""

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        모든 단계의 결과를 종합하여 최종 결과 생성.

        문제 단위로 묶고, 오답 여부를 정리하며,
        프린트용/해답지용 데이터를 생성합니다.

        Args:
            context: Pipeline 컨텍스트

        Returns:
            업데이트된 Pipeline 컨텍스트
        """
        # 답안 감지 결과 가져오기
        detected_answers = context.detected_answers or {}
        answer_regions = detected_answers.get("answer_regions", [])

        # 작업 영역 감지 결과 가져오기
        detected_work = context.detected_work or {}
        work_regions = detected_work.get("work_regions", [])

        # 문제 단위로 묶기
        problems = []
        for answer_region in answer_regions:
            problem_number = answer_region.get("problem_number")
            answer_value = answer_region.get("detected_value")
            answer_bbox = answer_region.get("bbox")

            # 해당 문제의 작업 영역 찾기
            related_work = [
                w
                for w in work_regions
                if w.get("problem_number") == problem_number
            ]

            problem_data = {
                "problem_number": problem_number,
                "answer": {
                    "value": answer_value,
                    "bbox": answer_bbox,
                    "type": answer_region.get("answer_type"),
                    "confidence": answer_region.get("confidence"),
                },
                "work_regions": [
                    {
                        "region_id": w.get("region_id"),
                        "bbox": w.get("bbox"),
                        "work_type": w.get("work_type"),
                    }
                    for w in related_work
                ],
                "is_correct": None,  # 나중에 정답과 비교하여 설정
            }
            problems.append(problem_data)

        # 오답 여부 정리 (더미 - 나중에 정답과 비교)
        total_problems = len(problems)
        correct_count = 0  # 더미
        incorrect_count = 0  # 더미

        # 최종 결과 생성
        context.postprocessed = {
            "problems": problems,
            "summary": {
                "total_problems": total_problems,
                "correct_count": correct_count,
                "incorrect_count": incorrect_count,
                "total_work_regions": detected_work.get("total_work_regions", 0),
            },
            "for_print": {
                "problems_detected": total_problems,
                "note": "더미 데이터",
            },
            "for_answer_sheet": {
                "answers": [
                    {
                        "problem_number": p["problem_number"],
                        "answer": p["answer"]["value"],
                    }
                    for p in problems
                ],
            },
            "status": "completed",
        }

        return context

    def get_name(self) -> str:
        """단계 이름 반환."""
        return "postprocess"

