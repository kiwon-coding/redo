"""이미지 처리 유틸리티 함수들.

연필/색연필 필기 제거를 위한 이미지 처리 함수들.

구조:
- HandwritingRemover: 추상 인터페이스
- ThresholdBasedRemover (Level 1): Grayscale + Adaptive Threshold
- MorphologyBasedRemover (Level 2): 형태 기반 분리 (미래 구현)
- AIBasedRemover (Level 3): AI 기반 inpainting (미래 구현)
"""

from abc import ABC, abstractmethod
from typing import Union
import numpy as np
from PIL import Image
import cv2


class HandwritingRemover(ABC):
    """필기 제거 전략 추상 클래스."""

    @abstractmethod
    def remove(self, image: np.ndarray) -> np.ndarray:
        """
        필기를 제거하고 인쇄된 문제만 남기는 메서드.

        Args:
            image: 입력 이미지 (BGR 또는 Grayscale numpy array)

        Returns:
            필기가 제거된 이미지 (Grayscale numpy array, uint8)
        """
        pass

    @abstractmethod
    def get_method_name(self) -> str:
        """사용된 방법 이름 반환."""
        pass

    @abstractmethod
    def get_confidence(self) -> float:
        """처리 신뢰도 반환 (0.0 ~ 1.0)."""
        pass


class ThresholdBasedRemover(HandwritingRemover):
    """Level 1: Grayscale + Adaptive Threshold 기반 필기 제거."""

    def __init__(
        self,
        threshold_block_size: int = 11,
        threshold_c: int = 2,
        noise_kernel_size: int = 3,
    ):
        """
        Args:
            threshold_block_size: Adaptive threshold 블록 크기 (홀수)
            threshold_c: Adaptive threshold 상수
            noise_kernel_size: Noise removal 커널 크기
        """
        self.threshold_block_size = threshold_block_size
        self.threshold_c = threshold_c
        self.noise_kernel_size = noise_kernel_size

    def remove(self, image: np.ndarray) -> np.ndarray:
        """
        Grayscale + Adaptive Threshold 기반 필기 제거.

        처리 흐름:
        1. Grayscale 변환 (연필은 흐려지고 인쇄 텍스트는 선명해짐)
        2. Adaptive Threshold (인쇄 텍스트 → 검정, 연필 → 흰색으로 제거)
        3. Noise Removal (작은 노이즈 제거)
        """
        # 1. Grayscale 변환
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # 2. Adaptive Threshold
        # 인쇄 텍스트 → 검정 (진하고 굵음)
        # 연필 → 흰색으로 날아감 (밝고 얇음)
        binary = cv2.adaptiveThreshold(
            gray,
            maxValue=255,
            adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            thresholdType=cv2.THRESH_BINARY_INV,
            blockSize=self.threshold_block_size,
            C=self.threshold_c,
        )

        # 3. Noise Removal
        kernel = np.ones((self.noise_kernel_size, self.noise_kernel_size), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        # 다시 원래 형태로 변환 (검정 텍스트, 흰색 배경)
        result = cv2.bitwise_not(cleaned)

        return result

    def get_method_name(self) -> str:
        """방법 이름 반환."""
        return "grayscale_adaptive_threshold"

    def get_confidence(self) -> float:
        """신뢰도 반환 (MVP 수준)."""
        return 0.7


class MorphologyBasedRemover(HandwritingRemover):
    """Level 2: 형태 기반 필기 제거 (미래 구현).

    아이디어:
    - 인쇄 텍스트: 일정한 두께, 일정한 폰트, 수평 정렬
    - 필기: 선 두께 불균일, 기울어짐, 곡선 많음
    → 형태적 특징으로 필기 제거
    """

    def __init__(self):
        """형태 기반 remover 초기화."""
        # TODO: Level 2 구현 시 파라미터 추가
        pass

    def remove(self, image: np.ndarray) -> np.ndarray:
        """
        형태 기반 필기 제거 (미래 구현).

        TODO: 구현 예정
        - 선 두께 분석
        - 기울기 분석
        - 곡률 분석
        - 인쇄 텍스트 특징 추출
        """
        # 현재는 Level 1 방식으로 fallback
        fallback = ThresholdBasedRemover()
        return fallback.remove(image)

    def get_method_name(self) -> str:
        """방법 이름 반환."""
        return "morphology_based"

    def get_confidence(self) -> float:
        """신뢰도 반환 (아직 구현되지 않음)."""
        return 0.0


class AIBasedRemover(HandwritingRemover):
    """Level 3: AI 기반 필기 제거 (미래 구현).

    아이디어:
    - Diffusion 기반 inpainting
    - Vision-language 모델로 "문제 복원"
    """

    def __init__(self, model_path: str = None):
        """
        Args:
            model_path: AI 모델 경로 (미래 구현)
        """
        self.model_path = model_path
        # TODO: Level 3 구현 시 모델 로드

    def remove(self, image: np.ndarray) -> np.ndarray:
        """
        AI 기반 필기 제거 (미래 구현).

        TODO: 구현 예정
        - Diffusion inpainting
        - Vision-language 모델 사용
        """
        # 현재는 Level 1 방식으로 fallback
        fallback = ThresholdBasedRemover()
        return fallback.remove(image)

    def get_method_name(self) -> str:
        """방법 이름 반환."""
        return "ai_based"

    def get_confidence(self) -> float:
        """신뢰도 반환 (아직 구현되지 않음)."""
        return 0.0


# 편의 함수들 (하위 호환성 유지)
def remove_handwriting(
    image_path: Union[str, bytes, np.ndarray],
    threshold_block_size: int = 11,
    threshold_c: int = 2,
    noise_kernel_size: int = 3,
) -> np.ndarray:
    """
    연필/색연필 필기를 제거하고 인쇄된 문제만 남기는 함수.

    레거시 함수 - 내부적으로 ThresholdBasedRemover 사용.

    Args:
        image_path: 이미지 경로, bytes, 또는 numpy array
        threshold_block_size: Adaptive threshold 블록 크기 (홀수)
        threshold_c: Adaptive threshold 상수
        noise_kernel_size: Noise removal 커널 크기

    Returns:
        필기가 제거된 이미지 (numpy array, uint8, 0-255)
    """
    # 이미지 로드
    if isinstance(image_path, (str, bytes)):
        if isinstance(image_path, str):
            img = cv2.imread(image_path)
        else:
            nparr = np.frombuffer(image_path, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
    elif isinstance(image_path, np.ndarray):
        img = image_path.copy()
    else:
        raise TypeError(
            f"Unsupported image type: {type(image_path)}. "
            "Expected str, bytes, or numpy.ndarray"
        )

    # ThresholdBasedRemover 사용
    remover = ThresholdBasedRemover(
        threshold_block_size=threshold_block_size,
        threshold_c=threshold_c,
        noise_kernel_size=noise_kernel_size,
    )
    return remover.remove(img)


def remove_handwriting_from_pil(
    image: Image.Image, remover: HandwritingRemover = None, **kwargs
) -> Image.Image:
    """
    PIL Image를 받아서 필기를 제거한 PIL Image를 반환.

    Args:
        image: PIL Image 객체
        remover: 사용할 HandwritingRemover 인스턴스 (None이면 기본값 사용)
        **kwargs: ThresholdBasedRemover에 전달할 파라미터 (remover가 None일 때만)

    Returns:
        필기가 제거된 PIL Image
    """
    # PIL Image를 numpy array로 변환
    img_array = np.array(image)

    # BGR로 변환 (PIL은 RGB, OpenCV는 BGR)
    if len(img_array.shape) == 3:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    # Remover 선택
    if remover is None:
        remover = ThresholdBasedRemover(**kwargs)

    # 필기 제거
    result_array = remover.remove(img_array)

    # numpy array를 PIL Image로 변환
    result_image = Image.fromarray(result_array)

    return result_image


# OCR 전처리 함수들
def preprocess_for_ocr(image: Image.Image) -> Image.Image:
    """
    OCR을 위해 이미지를 전처리합니다.

    처리 과정:
    1. Grayscale 변환
    2. 색상 반전 (검정 텍스트 → 흰색 배경)
    3. 대비 증가
    4. 이진화 (threshold)

    Args:
        image: PIL Image 객체

    Returns:
        OCR에 최적화된 PIL Image (Grayscale)
    """
    # PIL Image를 numpy array로 변환
    img_array = np.array(image)

    # 1. Grayscale 변환
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array.copy()

    # 2. 색상 반전 (검정 텍스트 → 흰색 배경으로)
    inverted = cv2.bitwise_not(gray)

    # 3. 대비 증가 (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(inverted)

    # 4. 이진화 (Adaptive Threshold)
    binary = cv2.adaptiveThreshold(
        enhanced,
        maxValue=255,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv2.THRESH_BINARY,
        blockSize=11,
        C=2,
    )

    # numpy array를 PIL Image로 변환
    result_image = Image.fromarray(binary)

    return result_image
