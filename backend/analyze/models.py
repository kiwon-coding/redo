"""Pipeline 데이터 모델 정의."""

from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class PipelineContext(BaseModel):
    """Pipeline 실행 컨텍스트 - 각 단계 간 데이터 전달용."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    file_id: str
    file_path: Path
    original_filename: Optional[str] = None

    # 각 단계의 결과를 저장
    preprocessed: Optional[Dict[str, Any]] = None
    separated_layers: Optional[Dict[str, Any]] = None  # separate_print_hand 결과
    cleaned_problem: Optional[Dict[str, Any]] = None  # clean_problem 결과
    extracted_answer: Optional[Dict[str, Any]] = None  # extract_answer 결과
    postprocessed: Optional[Dict[str, Any]] = None

    # 메타데이터
    metadata: Dict[str, Any] = {}


class AnswerResult(BaseModel):
    """답안 추출 결과."""

    text: str
    confidence: float


class AnalyzeResult(BaseModel):
    """Analyze Pipeline 최종 결과 스키마."""

    clean_problem_image_url: str
    answer: AnswerResult


class PipelineResult(BaseModel):
    """Pipeline 최종 결과."""

    file_id: str
    analysis: AnalyzeResult
    context: Optional[PipelineContext] = None
