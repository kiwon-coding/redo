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
    detected_answers: Optional[Dict[str, Any]] = None
    detected_work: Optional[Dict[str, Any]] = None
    postprocessed: Optional[Dict[str, Any]] = None

    # 메타데이터
    metadata: Dict[str, Any] = {}


class PipelineResult(BaseModel):
    """Pipeline 최종 결과."""

    file_id: str
    analysis: Dict[str, Any]
    context: Optional[PipelineContext] = None
