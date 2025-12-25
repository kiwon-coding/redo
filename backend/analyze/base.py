"""Pipeline 기본 인터페이스 및 추상 클래스."""

from abc import ABC, abstractmethod
from analyze.models import PipelineContext


class PipelineStep(ABC):
    """Pipeline 단계 추상 클래스."""

    @abstractmethod
    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        단계 실행.

        Args:
            context: Pipeline 컨텍스트

        Returns:
            업데이트된 Pipeline 컨텍스트
        """
        ...

    @abstractmethod
    def get_name(self) -> str:
        """단계 이름 반환."""
        ...


class Pipeline(ABC):
    """Pipeline 추상 클래스."""

    def __init__(self, steps: list[PipelineStep]):
        """
        Pipeline 초기화.

        Args:
            steps: 실행할 단계 리스트
        """
        self.steps = steps

    async def run(self, context: PipelineContext) -> PipelineContext:
        """
        Pipeline 실행.

        Args:
            context: 초기 Pipeline 컨텍스트

        Returns:
            최종 Pipeline 컨텍스트
        """
        current_context = context
        for step in self.steps:
            current_context = await step.execute(current_context)
        return current_context
