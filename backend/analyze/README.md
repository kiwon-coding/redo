# 이미지 분석 Pipeline 구조

이 디렉토리는 이미지 분석을 위한 Pipeline 구조를 구현합니다.

## 폴더 구조

```
analyze/
├── __init__.py              # 모듈 초기화
├── models.py                # 데이터 모델 (PipelineContext, PipelineResult, AnalyzeResult)
├── base.py                  # 추상 클래스 (PipelineStep, Pipeline)
├── pipeline.py              # 메인 Pipeline 구현
└── steps/                   # 각 단계별 구현
    ├── __init__.py
    ├── preprocess.py        # 전처리 단계
    ├── separate_print_hand.py  # 인쇄물 vs 손글씨 분리 (핵심)
    ├── clean_problem.py     # 인쇄물만 복원
    ├── extract_answer.py    # 필기 중 '답'만 OCR
    └── postprocess.py       # 후처리 단계
```

## 각 단계의 역할

### 1. Preprocess (전처리)
**목적**: 사진을 분석 가능한 상태로 만든다

카메라로 찍은 사진을 '스캔본'처럼 만드는 단계

**하는 일**:
- 회전 보정
- 밝기 / 대비 보정
- 여백 제거
- 해상도 정규화

**현재 상태**: 더미 구현 (원본 경로 그대로 넘김)

### 2. SeparatePrintHand (인쇄물 vs 손글씨 분리) ⭐ 핵심
**목적**: 인쇄된 텍스트/도형과 손글씨/색연필을 분리한다

이 단계가 전체 프로젝트의 기술적 난이도를 결정한다.

**하는 일**:
- 색상 분석 (인쇄물은 보통 검정/회색, 손글씨는 다양한 색)
- 질감 분석 (인쇄물은 균일, 손글씨는 불규칙)
- 두께 분석 (인쇄물은 일정, 손글씨는 변화)

**출력**:
- `print_layer`: 인쇄물 레이어
- `hand_layer`: 손글씨 레이어

**현재 상태**: 더미 구현

### 3. CleanProblem (문제 이미지 정리)
**목적**: 인쇄물만 남긴 깨끗한 문제 이미지를 생성한다

**하는 일**:
- separated_layers의 print_layer만 사용
- 손글씨 영역을 배경색으로 채우기
- 최종 이미지 저장 및 URL 생성

**출력**:
- `clean_problem_image_url`: 정리된 문제 이미지 URL

**현재 상태**: 더미 구현

### 4. ExtractAnswer (답안 추출)
**목적**: 손글씨 레이어에서 정답만 추출한다

**하는 일**:
- 숫자/식 인식
- 답 영역 감지 (문제 번호 옆)
- OCR 수행하여 텍스트로 변환
- 신뢰도 계산

**중요**: 이미지로 저장하지 않고 텍스트 데이터로 저장합니다.

**출력**:
- `answer_text`: 추출된 답안 텍스트
- `confidence`: 신뢰도

**현재 상태**: 더미 구현

### 5. Postprocess (후처리)
**목적**: frontend가 쓰기 좋은 JSON으로 정리

**하는 일**:
- clean_problem_image_url 생성
- answer.text, answer.confidence 정리
- 최종 AnalyzeResult 형식으로 변환

**출력**: AnalyzeResult
```python
{
    "clean_problem_image_url": "...",
    "answer": {
        "text": "642",
        "confidence": 0.92
    }
}
```

**현재 상태**: 더미 구현

## 데이터 흐름

```
PipelineContext
├── file_id, file_path (입력)
├── preprocessed (전처리 결과)
├── separated_layers (인쇄물/손글씨 분리 결과)
├── cleaned_problem (문제 이미지 정리 결과)
├── extracted_answer (답안 추출 결과)
└── postprocessed (최종 결과)
    └── result: AnalyzeResult
        ├── clean_problem_image_url
        └── answer: AnswerResult
            ├── text
            └── confidence
```

## 사용 방법

### 기본 사용

```python
from analyze import AnalyzePipeline

pipeline = AnalyzePipeline()
result = await pipeline.analyze(file_id="...", file_path=Path("..."))

# 결과 접근
print(result.analysis.clean_problem_image_url)
print(result.analysis.answer.text)
print(result.analysis.answer.confidence)
```

### 단계 교체

```python
from analyze.base import Pipeline
from analyze.steps import (
    PreprocessStep,
    SeparatePrintHandStep,
    CleanProblemStep,
    ExtractAnswerStep,
    PostprocessStep,
)
from my_custom_steps import CustomSeparatePrintHandStep

# 커스텀 단계로 교체
custom_pipeline = Pipeline([
    PreprocessStep(),
    CustomSeparatePrintHandStep(),  # 커스텀 분리 로직
    CleanProblemStep(),
    ExtractAnswerStep(),
    PostprocessStep(),
])
```

### 새로운 단계 추가

```python
from analyze.base import PipelineStep
from analyze.models import PipelineContext

class MyCustomStep(PipelineStep):
    async def execute(self, context: PipelineContext) -> PipelineContext:
        # 단계 로직 구현
        context.metadata["custom_result"] = "my result"
        return context
    
    def get_name(self) -> str:
        return "my_custom_step"
```

## 비동기/병렬 처리 고려사항

현재 구조는 async/await를 지원하므로, 나중에 병렬 처리가 필요한 경우:

1. **독립적인 단계 병렬 실행**:
   ```python
   import asyncio
   
   # CleanProblem과 ExtractAnswer를 병렬로 실행 가능
   clean_task = clean_problem_step.execute(context)
   extract_task = extract_answer_step.execute(context)
   clean_context, extract_context = await asyncio.gather(clean_task, extract_task)
   ```

2. **Pipeline 수정**: `base.py`의 `run()` 메서드를 수정하여 병렬 실행 지원

3. **단계 내부 병렬 처리**: 각 step의 `execute()` 메서드 내에서 `asyncio.gather()` 사용

## 확장성

- 각 단계는 독립적으로 테스트 가능
- 단계 교체가 쉬움 (의존성 최소화)
- 새로운 단계 추가가 용이
- 비동기/병렬 처리 지원 가능
- 프로덕션 환경에서 모니터링/로깅 추가 용이

## 다음 단계

각 단계에 실제 AI 모델을 연결:
- **preprocess.py**: OpenCV, PIL 등을 사용한 이미지 전처리
- **separate_print_hand.py**: ⭐ 핵심 - 색상/질감/두께 분석, ML 모델 (YOLO, Segmentation 등)
- **clean_problem.py**: 이미지 합성, 손글씨 영역 제거
- **extract_answer.py**: Tesseract OCR, EasyOCR, 숫자 인식 모델
- **postprocess.py**: 데이터 포맷팅, 검증
