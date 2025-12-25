"""답안 감지 단계 - 정답이 써 있는 위치를 찾는다.

아이의 '최종 답'이 어디에 쓰였는지 찾는 단계.
- 숫자/기호가 모여 있는 영역 탐지
- 문제 번호 옆의 답 영역 찾기
- 체크 표시(○, ✕) 위치 파악

나중에:
- OCR
- 숫자 인식
- 체크 마크 분류
"""

from analyze.base import PipelineStep
from analyze.models import PipelineContext


class DetectAnswerStep(PipelineStep):
    """답안 감지 단계 - 정답이 써 있는 위치를 찾기."""

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        정답이 써 있는 위치를 찾습니다.

        현재는 더미 구현입니다.
        나중에 OCR, 숫자 인식, 체크 마크 분류를 추가합니다.

        Args:
            context: Pipeline 컨텍스트

        Returns:
            업데이트된 Pipeline 컨텍스트
        """
        # 더미 답안 감지 결과
        context.detected_answers = {
            "answer_regions": [
                {
                    "problem_number": 1,
                    "bbox": [100, 200, 150, 250],  # [x1, y1, x2, y2]
                    "answer_type": "number",  # "number", "checkmark", "symbol"
                    "detected_value": "5",
                    "confidence": 0.92,
                },
                {
                    "problem_number": 2,
                    "bbox": [100, 300, 150, 350],
                    "answer_type": "checkmark",
                    "detected_value": "○",
                    "confidence": 0.88,
                },
                {
                    "problem_number": 3,
                    "bbox": [100, 400, 150, 450],
                    "answer_type": "number",
                    "detected_value": "3",
                    "confidence": 0.95,
                },
            ],
            "checkmarks": [
                {
                    "problem_number": 2,
                    "bbox": [100, 300, 150, 350],
                    "mark_type": "circle",  # "circle", "cross", "check"
                    "confidence": 0.88,
                },
            ],
            "total_problems_detected": 3,
            "status": "completed",
        }

        return context

    def get_name(self) -> str:
        """단계 이름 반환."""
        return "detect_answer"

