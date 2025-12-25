"""Pipeline 단계별 단위 테스트."""

import pytest
from analyze.models import PipelineContext
from analyze.steps.preprocess import PreprocessStep
from analyze.steps.separate_print_hand import SeparatePrintHandStep
from analyze.steps.clean_problem import CleanProblemStep
from analyze.steps.extract_answer import ExtractAnswerStep
from analyze.steps.postprocess import PostprocessStep


class TestPreprocessStep:
    """PreprocessStep 테스트."""

    @pytest.fixture
    def step(self):
        """PreprocessStep 인스턴스."""
        return PreprocessStep()

    @pytest.fixture
    def test_image_path(self, tmp_path):
        """테스트용 이미지 파일 생성."""
        image_path = tmp_path / "test.png"
        # 최소한의 유효한 PNG 바이너리
        image_path.write_bytes(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        return image_path

    @pytest.mark.asyncio
    async def test_preprocess_success(self, step, test_image_path):
        """정상적인 전처리 테스트."""
        context = PipelineContext(
            file_id="test-id",
            file_path=test_image_path,
        )

        result = await step.execute(context)

        assert result.preprocessed is not None
        assert result.preprocessed["status"] == "completed"
        assert result.preprocessed["file_format"] == ".png"
        assert result.preprocessed["file_size"] > 0
        assert result.preprocessed["original_path"] == str(test_image_path)

    @pytest.mark.asyncio
    async def test_preprocess_file_not_found(self, step, tmp_path):
        """파일이 없는 경우 테스트."""
        context = PipelineContext(
            file_id="test-id",
            file_path=tmp_path / "nonexistent.png",
        )

        with pytest.raises(FileNotFoundError):
            await step.execute(context)

    @pytest.mark.asyncio
    async def test_preprocess_empty_file(self, step, tmp_path):
        """빈 파일 테스트."""
        empty_file = tmp_path / "empty.png"
        empty_file.touch()

        context = PipelineContext(
            file_id="test-id",
            file_path=empty_file,
        )

        with pytest.raises(ValueError, match="File is empty"):
            await step.execute(context)

    @pytest.mark.asyncio
    async def test_preprocess_unsupported_format(self, step, tmp_path):
        """지원하지 않는 파일 형식 테스트."""
        text_file = tmp_path / "test.txt"
        text_file.write_text("not an image")

        context = PipelineContext(
            file_id="test-id",
            file_path=text_file,
        )

        with pytest.raises(ValueError, match="Unsupported file format"):
            await step.execute(context)

    def test_get_name(self, step):
        """단계 이름 반환 테스트."""
        assert step.get_name() == "preprocess"


class TestSeparatePrintHandStep:
    """SeparatePrintHandStep 테스트."""

    @pytest.fixture
    def step(self):
        """SeparatePrintHandStep 인스턴스."""
        return SeparatePrintHandStep()

    @pytest.fixture
    def context_with_preprocess(self, tmp_path):
        """전처리가 완료된 컨텍스트."""
        image_path = tmp_path / "test.png"
        image_path.write_bytes(b"fake image data")

        context = PipelineContext(
            file_id="test-id",
            file_path=image_path,
        )
        context.preprocessed = {
            "status": "completed",
            "processed_path": str(image_path),
        }
        return context

    @pytest.mark.asyncio
    async def test_separate_print_hand_success(self, step, context_with_preprocess):
        """정상적인 인쇄물/손글씨 분리 테스트."""
        result = await step.execute(context_with_preprocess)

        assert result.separated_layers is not None
        assert result.separated_layers["status"] == "completed"
        assert "print_layer_path" in result.separated_layers
        assert "hand_layer_path" in result.separated_layers

    @pytest.mark.asyncio
    async def test_separate_print_hand_preserves_context(
        self,
        step,
        context_with_preprocess,
    ):
        """컨텍스트의 다른 데이터가 보존되는지 테스트."""
        original_preprocessed = context_with_preprocess.preprocessed

        result = await step.execute(context_with_preprocess)

        assert result.preprocessed == original_preprocessed
        assert result.file_id == "test-id"

    def test_get_name(self, step):
        """단계 이름 반환 테스트."""
        assert step.get_name() == "separate_print_hand"


class TestCleanProblemStep:
    """CleanProblemStep 테스트."""

    @pytest.fixture
    def step(self):
        """CleanProblemStep 인스턴스."""
        return CleanProblemStep()

    @pytest.fixture
    def context_with_separation(self, tmp_path):
        """분리가 완료된 컨텍스트."""
        image_path = tmp_path / "test.png"
        image_path.write_bytes(b"fake image data")

        context = PipelineContext(
            file_id="test-id",
            file_path=image_path,
        )
        context.preprocessed = {"status": "completed"}
        context.separated_layers = {
            "print_layer_path": str(image_path),
            "hand_layer_path": str(image_path),
            "status": "completed",
        }
        return context

    @pytest.mark.asyncio
    async def test_clean_problem_success(self, step, context_with_separation):
        """정상적인 문제 이미지 정리 테스트."""
        result = await step.execute(context_with_separation)

        assert result.cleaned_problem is not None
        assert result.cleaned_problem["status"] == "completed"
        assert "clean_image_path" in result.cleaned_problem
        assert "clean_image_url" in result.cleaned_problem

    def test_get_name(self, step):
        """단계 이름 반환 테스트."""
        assert step.get_name() == "clean_problem"


class TestExtractAnswerStep:
    """ExtractAnswerStep 테스트."""

    @pytest.fixture
    def step(self):
        """ExtractAnswerStep 인스턴스."""
        return ExtractAnswerStep()

    @pytest.fixture
    def context_with_separation(self, tmp_path):
        """분리가 완료된 컨텍스트."""
        image_path = tmp_path / "test.png"
        image_path.write_bytes(b"fake image data")

        context = PipelineContext(
            file_id="test-id",
            file_path=image_path,
        )
        context.preprocessed = {"status": "completed"}
        context.separated_layers = {
            "print_layer_path": str(image_path),
            "hand_layer_path": str(image_path),
            "status": "completed",
        }
        return context

    @pytest.mark.asyncio
    async def test_extract_answer_success(self, step, context_with_separation):
        """정상적인 답안 추출 테스트."""
        result = await step.execute(context_with_separation)

        assert result.extracted_answer is not None
        assert result.extracted_answer["status"] == "completed"
        assert "answer_text" in result.extracted_answer
        assert "confidence" in result.extracted_answer

    def test_get_name(self, step):
        """단계 이름 반환 테스트."""
        assert step.get_name() == "extract_answer"


class TestPostprocessStep:
    """PostprocessStep 테스트."""

    @pytest.fixture
    def step(self):
        """PostprocessStep 인스턴스."""
        return PostprocessStep()

    @pytest.fixture
    def context_with_all_steps(self, tmp_path):
        """모든 단계가 완료된 컨텍스트."""
        image_path = tmp_path / "test.png"
        image_path.write_bytes(b"fake image data")

        context = PipelineContext(
            file_id="test-id",
            file_path=image_path,
        )
        context.preprocessed = {"status": "completed"}
        context.separated_layers = {
            "print_layer_path": str(image_path),
            "hand_layer_path": str(image_path),
            "status": "completed",
        }
        context.cleaned_problem = {
            "clean_image_path": str(image_path),
            "clean_image_url": "/uploads/test-id_clean.png",
            "status": "completed",
        }
        context.extracted_answer = {
            "answer_text": "642",
            "confidence": 0.92,
            "status": "completed",
        }
        return context

    @pytest.mark.asyncio
    async def test_postprocess_success(self, step, context_with_all_steps):
        """정상적인 후처리 테스트."""
        result = await step.execute(context_with_all_steps)

        assert result.postprocessed is not None
        assert result.postprocessed["status"] == "completed"
        assert "result" in result.postprocessed

        # AnalyzeResult 형식 검증
        analysis_result = result.postprocessed["result"]
        assert hasattr(analysis_result, "clean_problem_image_url")
        assert hasattr(analysis_result, "answer")
        assert hasattr(analysis_result.answer, "text")
        assert hasattr(analysis_result.answer, "confidence")

    @pytest.mark.asyncio
    async def test_postprocess_with_empty_data(self, step, tmp_path):
        """데이터가 없는 경우 테스트."""
        image_path = tmp_path / "test.png"
        image_path.write_bytes(b"fake image data")

        context = PipelineContext(
            file_id="test-id",
            file_path=image_path,
        )
        context.preprocessed = {"status": "completed"}
        context.separated_layers = {"status": "completed"}
        context.cleaned_problem = {"clean_image_url": ""}
        context.extracted_answer = {"answer_text": "", "confidence": 0.0}

        result = await step.execute(context)

        assert result.postprocessed is not None
        assert result.postprocessed["result"].clean_problem_image_url == ""
        assert result.postprocessed["result"].answer.text == ""

    def test_get_name(self, step):
        """단계 이름 반환 테스트."""
        assert step.get_name() == "postprocess"
