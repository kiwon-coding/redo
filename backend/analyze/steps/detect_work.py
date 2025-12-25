"""작업 영역 감지 단계 - 풀이 과정이 있는 영역을 찾는다.

지워야 할 '풀이 흔적'을 찾는 단계.
- 연필 필기 영역 감지
- 계산식 / 낙서 구분
- 답이 아닌 필기 영역 분리

핵심 포인트: 이게 있어야 "문제만 남기기" 가능
"""

from analyze.base import PipelineStep
from analyze.models import PipelineContext


class DetectWorkStep(PipelineStep):
    """작업 영역 감지 단계 - 풀이 과정이 있는 영역을 찾기."""

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        풀이 과정이 있는 영역을 찾습니다.

        현재는 더미 구현입니다.
        나중에 실제 CV 모델을 사용하여 연필 필기 영역을 감지합니다.

        Args:
            context: Pipeline 컨텍스트

        Returns:
            업데이트된 Pipeline 컨텍스트
        """
        # 더미 작업 영역 감지 결과
        context.detected_work = {
            "work_regions": [
                {
                    "region_id": "work_1",
                    "bbox": [400, 200, 800, 600],  # [x1, y1, x2, y2]
                    "work_type": "calculation",  # "calculation", "doodle", "erased"
                    "confidence": 0.85,
                    "problem_number": 1,  # 관련된 문제 번호
                },
                {
                    "region_id": "work_2",
                    "bbox": [400, 700, 800, 1100],
                    "work_type": "calculation",
                    "confidence": 0.82,
                    "problem_number": 2,
                },
                {
                    "region_id": "work_3",
                    "bbox": [200, 500, 350, 700],
                    "work_type": "doodle",
                    "confidence": 0.75,
                    "problem_number": None,  # 낙서는 문제와 무관
                },
            ],
            "calculation_regions": [
                {
                    "region_id": "work_1",
                    "bbox": [400, 200, 800, 600],
                    "problem_number": 1,
                },
                {
                    "region_id": "work_2",
                    "bbox": [400, 700, 800, 1100],
                    "problem_number": 2,
                },
            ],
            "doodle_regions": [
                {
                    "region_id": "work_3",
                    "bbox": [200, 500, 350, 700],
                },
            ],
            "total_work_regions": 3,
            "status": "completed",
        }

        return context

    def get_name(self) -> str:
        """단계 이름 반환."""
        return "detect_work"

