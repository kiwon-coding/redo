"""HandwritingRemover 전략 패턴 테스트."""

import pytest
import numpy as np
from PIL import Image
from analyze.steps.image_processing import (
    ThresholdBasedRemover,
    MorphologyBasedRemover,
    AIBasedRemover,
)


class TestThresholdBasedRemover:
    """ThresholdBasedRemover (Level 1) 테스트."""

    @pytest.fixture
    def remover(self):
        """ThresholdBasedRemover 인스턴스."""
        return ThresholdBasedRemover()

    @pytest.fixture
    def test_image(self):
        """테스트용 이미지 생성."""
        # 흰색 배경에 검정 사각형
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        img[40:60, 40:60] = [0, 0, 0]
        return img

    def test_remove_basic(self, remover, test_image):
        """기본 필기 제거 테스트."""
        result = remover.remove(test_image)
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 2  # Grayscale
        assert result.dtype == np.uint8

    def test_get_method_name(self, remover):
        """방법 이름 반환 테스트."""
        assert remover.get_method_name() == "grayscale_adaptive_threshold"

    def test_get_confidence(self, remover):
        """신뢰도 반환 테스트."""
        confidence = remover.get_confidence()
        assert 0.0 <= confidence <= 1.0
        assert confidence == 0.7  # Level 1 기본값

    def test_custom_parameters(self):
        """커스텀 파라미터 테스트."""
        remover = ThresholdBasedRemover(
            threshold_block_size=15, threshold_c=5, noise_kernel_size=5
        )
        test_img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        result = remover.remove(test_img)
        assert isinstance(result, np.ndarray)


class TestMorphologyBasedRemover:
    """MorphologyBasedRemover (Level 2) 테스트."""

    @pytest.fixture
    def remover(self):
        """MorphologyBasedRemover 인스턴스."""
        return MorphologyBasedRemover()

    @pytest.fixture
    def test_image(self):
        """테스트용 이미지 생성."""
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        img[40:60, 40:60] = [0, 0, 0]
        return img

    def test_remove_fallback(self, remover, test_image):
        """현재는 fallback으로 동작하는지 테스트."""
        result = remover.remove(test_image)
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 2

    def test_get_method_name(self, remover):
        """방법 이름 반환 테스트."""
        assert remover.get_method_name() == "morphology_based"

    def test_get_confidence(self, remover):
        """신뢰도 반환 테스트 (아직 구현되지 않음)."""
        assert remover.get_confidence() == 0.0


class TestAIBasedRemover:
    """AIBasedRemover (Level 3) 테스트."""

    @pytest.fixture
    def remover(self):
        """AIBasedRemover 인스턴스."""
        return AIBasedRemover()

    @pytest.fixture
    def test_image(self):
        """테스트용 이미지 생성."""
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        img[40:60, 40:60] = [0, 0, 0]
        return img

    def test_remove_fallback(self, remover, test_image):
        """현재는 fallback으로 동작하는지 테스트."""
        result = remover.remove(test_image)
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 2

    def test_get_method_name(self, remover):
        """방법 이름 반환 테스트."""
        assert remover.get_method_name() == "ai_based"

    def test_get_confidence(self, remover):
        """신뢰도 반환 테스트 (아직 구현되지 않음)."""
        assert remover.get_confidence() == 0.0


class TestRemoverStrategy:
    """전략 패턴 통합 테스트."""

    def test_remover_interchangeability(self):
        """다양한 remover가 동일한 인터페이스를 가지는지 테스트."""
        removers = [
            ThresholdBasedRemover(),
            MorphologyBasedRemover(),
            AIBasedRemover(),
        ]

        test_img = np.ones((50, 50, 3), dtype=np.uint8) * 255

        for remover in removers:
            result = remover.remove(test_img)
            assert isinstance(result, np.ndarray)
            assert len(result.shape) == 2
            assert result.dtype == np.uint8

            method_name = remover.get_method_name()
            assert isinstance(method_name, str)
            assert len(method_name) > 0

            confidence = remover.get_confidence()
            assert 0.0 <= confidence <= 1.0
