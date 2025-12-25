"""Pipeline 전체 흐름 테스트."""

import pytest
from pathlib import Path
from analyze.pipeline import AnalyzePipeline
from analyze.models import PipelineContext


class TestAnalyzePipeline:
    """AnalyzePipeline 전체 흐름 테스트."""

    @pytest.fixture
    def pipeline(self):
        """AnalyzePipeline 인스턴스."""
        return AnalyzePipeline()

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
    async def test_pipeline_full_flow(self, pipeline, test_image_path):
        """전체 pipeline 흐름 테스트."""
        file_id = "test-file-id"
        result = await pipeline.analyze(file_id, test_image_path)

        # 결과 검증
        assert result.file_id == file_id
        assert result.analysis is not None
        assert hasattr(result.analysis, "clean_problem_image_url")
        assert hasattr(result.analysis, "answer")
        assert hasattr(result.analysis.answer, "text")
        assert hasattr(result.analysis.answer, "confidence")

        # 컨텍스트 검증
        assert result.context is not None
        assert result.context.file_id == file_id
        assert result.context.file_path == test_image_path

        # 각 단계 결과 검증
        assert result.context.preprocessed is not None
        assert result.context.separated_layers is not None
        assert result.context.cleaned_problem is not None
        assert result.context.extracted_answer is not None
        assert result.context.postprocessed is not None

    @pytest.mark.asyncio
    async def test_pipeline_context_progression(self, pipeline, test_image_path):
        """컨텍스트가 단계별로 올바르게 업데이트되는지 테스트."""
        file_id = "test-file-id"
        result = await pipeline.analyze(file_id, test_image_path)

        context = result.context

        # 각 단계의 결과가 순서대로 저장되었는지 확인
        assert context.preprocessed is not None
        assert context.preprocessed["status"] == "completed"

        assert context.separated_layers is not None
        assert context.separated_layers["status"] == "completed"

        assert context.cleaned_problem is not None
        assert context.cleaned_problem["status"] == "completed"

        assert context.extracted_answer is not None
        assert context.extracted_answer["status"] == "completed"

        assert context.postprocessed is not None
        assert context.postprocessed["status"] == "completed"

    @pytest.mark.asyncio
    async def test_pipeline_file_not_found(self, pipeline, tmp_path):
        """파일이 없는 경우 테스트."""
        non_existent_file = tmp_path / "nonexistent.png"

        with pytest.raises(FileNotFoundError):
            await pipeline.analyze("test-id", non_existent_file)

    @pytest.mark.asyncio
    async def test_pipeline_empty_file(self, pipeline, tmp_path):
        """빈 파일 테스트."""
        empty_file = tmp_path / "empty.png"
        empty_file.touch()

        with pytest.raises(ValueError, match="File is empty"):
            await pipeline.analyze("test-id", empty_file)

    @pytest.mark.asyncio
    async def test_pipeline_unsupported_format(self, pipeline, tmp_path):
        """지원하지 않는 파일 형식 테스트."""
        text_file = tmp_path / "test.txt"
        text_file.write_text("not an image")

        with pytest.raises(ValueError, match="Unsupported file format"):
            await pipeline.analyze("test-id", text_file)

    @pytest.mark.asyncio
    async def test_pipeline_result_structure(self, pipeline, test_image_path):
        """결과 구조가 올바른지 테스트."""
        result = await pipeline.analyze("test-id", test_image_path)

        # PipelineResult 구조 검증
        assert hasattr(result, "file_id")
        assert hasattr(result, "analysis")
        assert hasattr(result, "context")

        # analysis는 AnalyzeResult 객체여야 함
        assert hasattr(result.analysis, "clean_problem_image_url")
        assert hasattr(result.analysis, "answer")
        assert hasattr(result.analysis.answer, "text")
        assert hasattr(result.analysis.answer, "confidence")

        # context는 모든 단계 결과를 포함해야 함
        assert result.context.preprocessed is not None
        assert result.context.separated_layers is not None
        assert result.context.cleaned_problem is not None
        assert result.context.extracted_answer is not None
        assert result.context.postprocessed is not None

    @pytest.mark.asyncio
    async def test_pipeline_different_file_formats(self, pipeline, tmp_path):
        """다양한 파일 형식 테스트."""
        # PNG 파일
        png_file = tmp_path / "test.png"
        png_file.write_bytes(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        )

        result_png = await pipeline.analyze("png-id", png_file)
        assert result_png.context.preprocessed["file_format"] == ".png"

        # JPEG 파일 (확장자만 확인, 실제 JPEG 바이너리는 복잡)
        jpg_file = tmp_path / "test.jpg"
        jpg_file.write_bytes(b"\xff\xd8\xff\xe0")  # 간단한 JPEG 헤더

        result_jpg = await pipeline.analyze("jpg-id", jpg_file)
        assert result_jpg.context.preprocessed["file_format"] == ".jpg"
