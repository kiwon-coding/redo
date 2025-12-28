# Extract Problem - 필기 제거 전략

## 개요

`extract_problem` 단계는 연필/색연필로 쓴 필기를 제거하고 인쇄된 문제만 남기는 단계입니다.

## 구조

Strategy 패턴을 사용하여 확장 가능한 구조로 설계되었습니다.

```
image_processing.py
├── HandwritingRemover (추상 클래스)
│   ├── remove(image) -> image
│   ├── get_method_name() -> str
│   └── get_confidence() -> float
│
├── ThresholdBasedRemover (Level 1) ✅ 구현됨
│   └── Grayscale + Adaptive Threshold
│
├── MorphologyBasedRemover (Level 2) 🔜 미래 구현
│   └── 형태 기반 분리 (선 두께, 기울기, 곡률)
│
└── AIBasedRemover (Level 3) 🔜 미래 구현
    └── Diffusion inpainting / Vision-language 모델
```

## 사용 방법

### 기본 사용 (Level 1)

```python
from analyze.steps.extract_problem import ExtractProblemStep

# 기본값으로 Level 1 사용
step = ExtractProblemStep()
```

### 레벨 선택

```python
# Level 1 (Threshold 기반)
step = ExtractProblemStep(remover_level=1)

# Level 2 (형태 기반) - 미래 구현
step = ExtractProblemStep(remover_level=2)

# Level 3 (AI 기반) - 미래 구현
step = ExtractProblemStep(remover_level=3)
```

### 커스텀 Remover 사용

```python
from analyze.steps.image_processing import ThresholdBasedRemover

# 커스텀 파라미터로 Remover 생성
custom_remover = ThresholdBasedRemover(
    threshold_block_size=15,
    threshold_c=5,
    noise_kernel_size=5,
)

step = ExtractProblemStep(remover=custom_remover)
```

## Level별 상세

### Level 1: ThresholdBasedRemover ✅

**방법**: Grayscale + Adaptive Threshold

**아이디어**:
- 인쇄 텍스트: 검정색, 진하고 굵음
- 연필: 회색/연한 색, 밝고 얇음
- 색연필: 색 있음

**처리 흐름**:
1. Grayscale 변환 (연필은 흐려지고 인쇄 텍스트는 선명해짐)
2. Adaptive Threshold (인쇄 텍스트 → 검정, 연필 → 흰색으로 제거)
3. Noise Removal (작은 노이즈 제거)

**신뢰도**: 0.7 (MVP 수준)

### Level 2: MorphologyBasedRemover 🔜

**방법**: 형태 기반 분리

**아이디어**:
- 인쇄 텍스트: 일정한 두께, 일정한 폰트, 수평 정렬
- 필기: 선 두께 불균일, 기울어짐, 곡선 많음
→ 형태적 특징으로 필기 제거

**구현 예정**:
- 선 두께 분석
- 기울기 분석
- 곡률 분석
- 인쇄 텍스트 특징 추출

**현재 상태**: Level 1로 fallback

### Level 3: AIBasedRemover 🔜

**방법**: AI 기반 inpainting

**아이디어**:
- Diffusion 기반 inpainting
- Vision-language 모델로 "문제 복원"

**구현 예정**:
- Diffusion 모델 통합
- Vision-language 모델 사용

**현재 상태**: Level 1로 fallback

## 확장 방법

새로운 레벨을 추가하려면:

1. `HandwritingRemover`를 상속받는 클래스 생성
2. `remove()`, `get_method_name()`, `get_confidence()` 구현
3. `ExtractProblemStep.__init__()`에 레벨 추가 (선택사항)

예시:

```python
class CustomRemover(HandwritingRemover):
    def remove(self, image: np.ndarray) -> np.ndarray:
        # 커스텀 로직 구현
        pass
    
    def get_method_name(self) -> str:
        return "custom_method"
    
    def get_confidence(self) -> float:
        return 0.8

# 사용
step = ExtractProblemStep(remover=CustomRemover())
```

## 테스트

```bash
# 모든 테스트 실행
pytest backend/tests/test_extract_problem.py
pytest backend/tests/test_handwriting_removers.py

# 특정 레벨 테스트
pytest backend/tests/test_handwriting_removers.py::TestThresholdBasedRemover
```

