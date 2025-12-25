"""Pipeline 단계별 단위 테스트."""

import pytest
from pathlib import Path
from analyze.models import PipelineContext
from analyze.steps.preprocess import PreprocessStep
from analyze.steps.detect_answer import DetectAnswerStep
from analyze.steps.detect_work import DetectWorkStep
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


class TestDetectAnswerStep:
    """DetectAnswerStep 테스트."""

    @pytest.fixture
    def step(self):
        """DetectAnswerStep 인스턴스."""
        return DetectAnswerStep()

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
            "file_format": ".png",
        }
        return context

    @pytest.mark.asyncio
    async def test_detect_answer_success(self, step, context_with_preprocess):
        """정상적인 답안 감지 테스트."""
        result = await step.execute(context_with_preprocess)

        assert result.detected_answers is not None
        assert result.detected_answers["status"] == "completed"
        assert "answer_regions" in result.detected_answers
        assert len(result.detected_answers["answer_regions"]) > 0
        assert "checkmarks" in result.detected_answers
        assert "total_problems_detected" in result.detected_answers

        # 답안 영역 검증
        for region in result.detected_answers["answer_regions"]:
            assert "problem_number" in region
            assert "bbox" in region
            assert "answer_type" in region
            assert "detected_value" in region
            assert "confidence" in region

    @pytest.mark.asyncio
    async def test_detect_answer_preserves_context(self, step, context_with_preprocess):
        """컨텍스트의 다른 데이터가 보존되는지 테스트."""
        original_preprocessed = context_with_preprocess.preprocessed

        result = await step.execute(context_with_preprocess)

        assert result.preprocessed == original_preprocessed
        assert result.file_id == "test-id"
        assert result.file_path == context_with_preprocess.file_path

    def test_get_name(self, step):
        """단계 이름 반환 테스트."""
        assert step.get_name() == "detect_answer"


class TestDetectWorkStep:
    """DetectWorkStep 테스트."""

    @pytest.fixture
    def step(self):
        """DetectWorkStep 인스턴스."""
        return DetectWorkStep()

    @pytest.fixture
    def context_with_answers(self, tmp_path):
        """답안 감지가 완료된 컨텍스트."""
        image_path = tmp_path / "test.png"
        image_path.write_bytes(b"fake image data")

        context = PipelineContext(
            file_id="test-id",
            file_path=image_path,
        )
        context.preprocessed = {"status": "completed"}
        context.detected_answers = {
            "answer_regions": [
                {"problem_number": 1, "bbox": [100, 200, 150, 250]},
                {"problem_number": 2, "bbox": [100, 300, 150, 350]},
            ],
            "status": "completed",
        }
        return context

    @pytest.mark.asyncio
    async def test_detect_work_success(self, step, context_with_answers):
        """정상적인 작업 영역 감지 테스트."""
        result = await step.execute(context_with_answers)

        assert result.detected_work is not None
        assert result.detected_work["status"] == "completed"
        assert "work_regions" in result.detected_work
        assert len(result.detected_work["work_regions"]) > 0
        assert "calculation_regions" in result.detected_work
        assert "doodle_regions" in result.detected_work
        assert "total_work_regions" in result.detected_work

        # 작업 영역 검증
        for region in result.detected_work["work_regions"]:
            assert "region_id" in region
            assert "bbox" in region
            assert "work_type" in region
            assert "confidence" in region

    @pytest.mark.asyncio
    async def test_detect_work_preserves_context(self, step, context_with_answers):
        """컨텍스트의 다른 데이터가 보존되는지 테스트."""
        original_answers = context_with_answers.detected_answers

        result = await step.execute(context_with_answers)

        assert result.detected_answers == original_answers
        assert result.preprocessed == context_with_answers.preprocessed

    def test_get_name(self, step):
        """단계 이름 반환 테스트."""
        assert step.get_name() == "detect_work"


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
        context.detected_answers = {
            "answer_regions": [
                {
                    "problem_number": 1,
                    "bbox": [100, 200, 150, 250],
                    "detected_value": "5",
                    "answer_type": "number",
                    "confidence": 0.92,
                },
                {
                    "problem_number": 2,
                    "bbox": [100, 300, 150, 350],
                    "detected_value": "○",
                    "answer_type": "checkmark",
                    "confidence": 0.88,
                },
            ],
            "status": "completed",
        }
        context.detected_work = {
            "work_regions": [
                {
                    "region_id": "work_1",
                    "bbox": [400, 200, 800, 600],
                    "work_type": "calculation",
                    "problem_number": 1,
                },
                {
                    "region_id": "work_2",
                    "bbox": [400, 700, 800, 1100],
                    "work_type": "calculation",
                    "problem_number": 2,
                },
            ],
            "status": "completed",
        }
        return context

    @pytest.mark.asyncio
    async def test_postprocess_success(self, step, context_with_all_steps):
        """정상적인 후처리 테스트."""
        result = await step.execute(context_with_all_steps)

        assert result.postprocessed is not None
        assert result.postprocessed["status"] == "completed"
        assert "problems" in result.postprocessed
        assert "summary" in result.postprocessed
        assert "for_print" in result.postprocessed
        assert "for_answer_sheet" in result.postprocessed

        # 문제 데이터 검증
        problems = result.postprocessed["problems"]
        assert len(problems) > 0
        for problem in problems:
            assert "problem_number" in problem
            assert "answer" in problem
            assert "work_regions" in problem
            assert "is_correct" in problem

        # 요약 정보 검증
        summary = result.postprocessed["summary"]
        assert "total_problems" in summary
        assert "correct_count" in summary
        assert "incorrect_count" in summary
        assert "total_work_regions" in summary

        # 프린트용 데이터 검증
        assert "problems_detected" in result.postprocessed["for_print"]
        assert "note" in result.postprocessed["for_print"]

        # 해답지용 데이터 검증
        answer_sheet = result.postprocessed["for_answer_sheet"]
        assert "answers" in answer_sheet
        assert len(answer_sheet["answers"]) == len(problems)

    @pytest.mark.asyncio
    async def test_postprocess_with_empty_answers(self, step, tmp_path):
        """답안이 없는 경우 테스트."""
        image_path = tmp_path / "test.png"
        image_path.write_bytes(b"fake image data")

        context = PipelineContext(
            file_id="test-id",
            file_path=image_path,
        )
        context.preprocessed = {"status": "completed"}
        context.detected_answers = {"answer_regions": [], "status": "completed"}
        context.detected_work = {"work_regions": [], "status": "completed"}

        result = await step.execute(context)

        assert result.postprocessed is not None
        assert len(result.postprocessed["problems"]) == 0
        assert result.postprocessed["summary"]["total_problems"] == 0

    @pytest.mark.asyncio
    async def test_postprocess_links_work_to_problems(
        self, step, context_with_all_steps
    ):
        """작업 영역이 문제에 올바르게 연결되는지 테스트."""
        result = await step.execute(context_with_all_steps)

        problems = result.postprocessed["problems"]
        problem_1 = next(p for p in problems if p["problem_number"] == 1)
        problem_2 = next(p for p in problems if p["problem_number"] == 2)

        # 문제 1에 연결된 작업 영역 확인
        assert len(problem_1["work_regions"]) == 1
        assert problem_1["work_regions"][0]["region_id"] == "work_1"

        # 문제 2에 연결된 작업 영역 확인
        assert len(problem_2["work_regions"]) == 1
        assert problem_2["work_regions"][0]["region_id"] == "work_2"

    def test_get_name(self, step):
        """단계 이름 반환 테스트."""
        assert step.get_name() == "postprocess"
