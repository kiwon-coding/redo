# 이미지 분석 Pipeline 구조

이 디렉토리는 이미지 분석을 위한 Pipeline 구조를 구현합니다.

## 폴더 구조

```
analyze/
├── __init__.py              # 모듈 초기화
├── models.py                # 데이터 모델 (PipelineContext, PipelineResult)
├── base.py                  # 추상 클래스 (PipelineStep, Pipeline)
├── pipeline.py              # 메인 Pipeline 구현
└── steps/                   # 각 단계별 구현
    ├── __init__.py
    ├── preprocess.py        # 전처리 단계
    ├── detect_answer.py     # 답안 감지 단계
    ├── detect_work.py       # 작업 영역 감지 단계
    └── postprocess.py      # 후처리 단계
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

### 2. DetectAnswer (답안 감지)
**목적**: 정답이 써 있는 위치를 찾는다

아이의 '최종 답'이 어디에 쓰였는지 찾는 단계

**하는 일**:
- 숫자/기호가 모여 있는 영역 탐지
- 문제 번호 옆의 답 영역 찾기
- 체크 표시(○, ✕) 위치 파악

**나중에 추가할 것**:
- OCR
- 숫자 인식
- 체크 마크 분류

**현재 상태**: 더미 구현

### 3. DetectWork (작업 영역 감지)
**목적**: 풀이 과정이 있는 영역을 찾는다

지워야 할 '풀이 흔적'을 찾는 단계

**하는 일**:
- 연필 필기 영역 감지
- 계산식 / 낙서 구분
- 답이 아닌 필기 영역 분리

**핵심 포인트**: 이게 있어야 "문제만 남기기" 가능

**현재 상태**: 더미 구현

### 4. Postprocess (후처리)
**목적**: 사람과 시스템이 쓰기 좋은 결과로 정리

AI 결과를 '서비스 데이터'로 바꾸는 단계

**하는 일**:
- 문제 단위로 묶기
- 오답 여부 정리
- 프린트용 / 해답지용 데이터 생성

**현재 상태**: 더미 구현

## 데이터 흐름

```
PipelineContext
├── file_id, file_path (입력)
├── preprocessed (전처리 결과)
├── detected_answers (답안 감지 결과)
├── detected_work (작업 영역 감지 결과)
└── postprocessed (최종 결과)
    ├── problems (문제 단위 데이터)
    ├── summary (요약 정보)
    ├── for_print (프린트용 데이터)
    └── for_answer_sheet (해답지용 데이터)
```

## 사용 방법

### 기본 사용

```python
from analyze import AnalyzePipeline

pipeline = AnalyzePipeline()
result = await pipeline.analyze(file_id="...", file_path=Path("..."))
```

### 단계 교체

```python
from analyze.base import Pipeline
from analyze.steps import PreprocessStep, DetectAnswerStep
from my_custom_steps import CustomDetectWorkStep, PostprocessStep

# 커스텀 단계로 교체
custom_pipeline = Pipeline([
    PreprocessStep(),
    DetectAnswerStep(),
    CustomDetectWorkStep(),  # 커스텀 작업 영역 감지
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
   
   # DetectAnswer와 DetectWork를 병렬로 실행
   answer_task = detect_answer_step.execute(context)
   work_task = detect_work_step.execute(context)
   answer_context, work_context = await asyncio.gather(answer_task, work_task)
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
- **detect_answer.py**: Tesseract OCR, EasyOCR, 숫자 인식 모델
- **detect_work.py**: YOLO, Segmentation 모델 등
- **postprocess.py**: 정답 비교 로직, 데이터 포맷팅

