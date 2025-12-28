from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import uuid
from PIL import Image
from services.file_storage import save_upload_file, get_file_path_by_id
from analyze import AnalyzePipeline
from analyze.models import PipelineContext
from analyze.steps import PreprocessStep, ExtractProblemStep, ExtractAnswerStep

app = FastAPI()

# CORS 설정 (프론트 연결용 – 중요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계에서는 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pipeline 인스턴스 생성 (싱글톤 패턴 고려 가능)
analyze_pipeline = AnalyzePipeline()


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_info = await save_upload_file(file, file_id=file_id)

    return {
        "file_id": file_id,
        "stored_path": file_info["stored_path"],
        "original_filename": file_info["original_filename"],
    }


class CropRequest(BaseModel):
    """Crop 요청 모델."""

    image_id: str
    crop: dict  # {"x": int, "y": int, "w": int, "h": int}


class AnalyzeRequest(BaseModel):
    file_id: str


class ProblemRequest(BaseModel):
    """문제 저장 요청 모델."""

    problem_image_file_id: str
    answer_value: str


@app.post("/crop")
async def crop(request: CropRequest):
    """
    이미지 crop 처리.

    원본 이미지를 crop하여 새 이미지로 저장합니다.
    Phase 1 - 사용자 주도 crop 단계.

    Args:
        request: CropRequest (image_id, crop: {x, y, w, h})

    Returns:
        crop된 이미지의 file_id와 저장 경로
    """
    try:
        # 원본 이미지 경로 찾기
        original_path = get_file_path_by_id(request.image_id)
        if original_path is None or not original_path.exists():
            raise HTTPException(
                status_code=404, detail=f"File not found: {request.image_id}"
            )

        # crop 파라미터 검증
        crop_params = request.crop
        x = crop_params.get("x", 0)
        y = crop_params.get("y", 0)
        w = crop_params.get("w")
        h = crop_params.get("h")

        if w is None or h is None or w <= 0 or h <= 0:
            raise HTTPException(
                status_code=400,
                detail="Invalid crop parameters: w and h must be positive",
            )

        # 이미지 로드 및 crop
        try:
            img = Image.open(original_path)
            img_width, img_height = img.size

            # crop 영역 검증
            if x < 0 or y < 0 or x + w > img_width or y + h > img_height:
                detail_msg = (
                    f"Crop area out of bounds. "
                    f"Image size: {img_width}x{img_height}, "
                    f"Crop: x={x}, y={y}, w={w}, h={h}"
                )
                raise HTTPException(status_code=400, detail=detail_msg)

            # crop 수행
            cropped_img = img.crop((x, y, x + w, y + h))

            # 새 file_id 생성
            cropped_file_id = str(uuid.uuid4())

            # 저장 경로 생성 (원본과 동일한 구조)
            from datetime import datetime
            from services.file_storage import UPLOAD_ROOT

            date_dir = datetime.now().strftime("%Y-%m-%d")
            upload_dir = UPLOAD_ROOT / date_dir
            upload_dir.mkdir(parents=True, exist_ok=True)

            ext = original_path.suffix or ".png"
            stored_name = f"{cropped_file_id}{ext}"
            cropped_path = upload_dir / stored_name

            # crop된 이미지 저장
            cropped_img.save(cropped_path)

            return {
                "file_id": cropped_file_id,
                "stored_path": str(cropped_path),
                "original_image_id": request.image_id,
                "crop": crop_params,
            }

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Image processing failed: {str(e)}"
            ) from e

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        detail = f"Crop failed: {str(e)}"
        raise HTTPException(status_code=500, detail=detail) from e


@app.get("/files/{file_id}")
async def get_file(file_id: str):
    """
    file_id로 저장된 파일을 반환합니다.
    """
    file_path = get_file_path_by_id(file_id)
    if file_path is None or not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_id}")

    # 이미지 타입 결정
    suffix = file_path.suffix.lower()
    media_type = "image/jpeg" if suffix in [".jpg", ".jpeg"] else "image/png"

    return FileResponse(path=file_path, media_type=media_type)


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        file_path = get_file_path_by_id(request.file_id)
        if file_path is None or not file_path.exists():
            raise HTTPException(
                status_code=404, detail=f"File not found: {request.file_id}"
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # Pipeline 실행
    try:
        result = await analyze_pipeline.analyze(
            file_id=request.file_id,
            file_path=file_path,
        )
        # extract_problem 단계에서 생성된 problem_file_id 가져오기
        problem_file_id = None
        if result.context and result.context.extracted_problem:
            problem_file_id = result.context.extracted_problem.get("problem_file_id")

        # Frontend에서 사용하기 좋은 형식으로 응답
        return {
            "message": "분석 완료",
            "file_id": result.file_id,  # 원본 crop된 이미지 file_id
            "problem_image_file_id": problem_file_id,  # 문제 이미지 file_id
            "problem_image_url": result.analysis.clean_problem_image_url,
            "answer": {
                "text": result.analysis.answer.text,
                "confidence": result.analysis.answer.confidence,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}",
        ) from e


# 문제 리스트 저장 (더미 구현)
# 실제로는 DB에 저장하지만, 현재는 메모리에 저장
problems_list = []


@app.post("/problems")
async def create_problem(request: ProblemRequest):
    """
    문제를 저장합니다.

    이 시점에만:
    - DB 저장 (현재는 메모리)
    - "문제 리스트"에 쌓임
    - 시험지 생성 대상이 됨

    Args:
        request: ProblemRequest (problem_image_file_id, answer_value)

    Returns:
        저장된 문제 정보
    """
    # 문제 이미지 파일 존재 확인
    problem_file_path = get_file_path_by_id(request.problem_image_file_id)
    if problem_file_path is None or not problem_file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Problem image not found: {request.problem_image_file_id}",
        )

    # 문제 ID 생성
    problem_id = str(uuid.uuid4())

    # 더미: 메모리에 저장 (실제로는 DB에 저장)
    problem_data = {
        "problem_id": problem_id,
        "problem_image_file_id": request.problem_image_file_id,
        "answer_value": request.answer_value,
        "created_at": datetime.now().isoformat(),
        "status": "pending",  # 시험지 생성 대기 상태
    }

    problems_list.append(problem_data)

    return {
        "message": "문제가 저장되었습니다",
        "problem_id": problem_id,
        "problem_image_file_id": request.problem_image_file_id,
        "answer_value": request.answer_value,
    }


@app.get("/problems")
async def get_problems():
    """
    저장된 문제 리스트를 반환합니다.

    Returns:
        문제 리스트
    """
    return {
        "count": len(problems_list),
        "problems": problems_list,
    }


# ========== Debug Endpoints ==========
# 개발/테스트용 엔드포인트 - 각 단계를 독립적으로 테스트할 수 있음


@app.post("/debug/extract_problem")
async def debug_extract_problem(
    file: UploadFile = File(None, description="이미지 파일 (직접 업로드)"),
    image_id: str = Form(None, description="이미지 ID (이미 업로드된 파일)"),
    remover_level: int = Form(1, description="필기 제거 레벨 (1, 2, 3)"),
):
    """
    extract_problem 단계만 독립적으로 실행합니다.

    Swagger UI에서 이미지 파일을 직접 업로드하거나,
    이미 업로드된 파일의 image_id를 사용할 수 있습니다.

    Args:
        file: 이미지 파일 (직접 업로드) - file 또는 image_id 중 하나 필수
        image_id: 이미지 ID (이미 업로드된 파일) - file 또는 image_id 중 하나 필수
        remover_level: 필기 제거 레벨 (1, 2, 3), 기본값: 1

    Returns:
        extract_problem 결과 (문제 이미지 URL, 메타데이터)
    """
    # 파일 경로 결정: file 또는 image_id 중 하나 필수
    file_path = None
    actual_file_id = None

    if file is not None:
        # 파일을 직접 업로드한 경우
        file_id = str(uuid.uuid4())
        file_info = await save_upload_file(file, file_id=file_id)
        file_path = Path(file_info["stored_path"])
        actual_file_id = file_id
    elif image_id:
        # image_id를 사용한 경우
        file_path = get_file_path_by_id(image_id)
        if file_path is None or not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {image_id}")
        actual_file_id = image_id
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'file' or 'image_id' must be provided",
        )

    try:
        # PipelineContext 생성
        context = PipelineContext(
            file_id=actual_file_id,
            file_path=file_path,
        )

        # 1. PreprocessStep 실행 (필수)
        preprocess_step = PreprocessStep()
        context = await preprocess_step.execute(context)

        # 2. ExtractProblemStep 실행
        extract_problem_step = ExtractProblemStep(remover_level=remover_level)
        context = await extract_problem_step.execute(context)

        # 결과 반환
        if context.extracted_problem is None:
            raise HTTPException(status_code=500, detail="extract_problem failed")

        return {
            "message": "extract_problem 완료",
            "image_id": actual_file_id,
            "result": {
                "problem_file_id": context.extracted_problem.get("problem_file_id"),
                "problem_image_url": context.extracted_problem.get("problem_image_url"),
                "problem_image_path": context.extracted_problem.get(
                    "problem_image_path"
                ),
                "handwriting_removed": context.extracted_problem.get(
                    "handwriting_removed"
                ),
                "separation_method": context.extracted_problem.get("separation_method"),
                "confidence": context.extracted_problem.get("confidence"),
                "status": context.extracted_problem.get("status"),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"extract_problem failed: {str(e)}",
        ) from e


@app.post("/debug/extract_answer")
async def debug_extract_answer(
    file: UploadFile = File(None, description="이미지 파일 (직접 업로드)"),
    image_id: str = Form(None, description="이미지 ID (이미 업로드된 파일)"),
    min_confidence: float = Form(0.3, description="최소 신뢰도 (0.0 ~ 1.0)"),
):
    """
    extract_answer 단계만 독립적으로 실행합니다.

    Swagger UI에서 이미지 파일을 직접 업로드하거나,
    이미 업로드된 파일의 image_id를 사용할 수 있습니다.

    Args:
        file: 이미지 파일 (직접 업로드) - file 또는 image_id 중 하나 필수
        image_id: 이미지 ID (이미 업로드된 파일) - file 또는 image_id 중 하나 필수
        min_confidence: 최소 신뢰도 (0.0 ~ 1.0), 기본값: 0.3

    Returns:
        extract_answer 결과 (답안 텍스트, confidence)
    """
    # 파일 경로 결정: file 또는 image_id 중 하나 필수
    file_path = None
    actual_file_id = None

    if file is not None:
        # 파일을 직접 업로드한 경우
        file_id = str(uuid.uuid4())
        file_info = await save_upload_file(file, file_id=file_id)
        file_path = Path(file_info["stored_path"])
        actual_file_id = file_id
    elif image_id:
        # image_id를 사용한 경우
        file_path = get_file_path_by_id(image_id)
        if file_path is None or not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {image_id}")
        actual_file_id = image_id
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'file' or 'image_id' must be provided",
        )

    try:
        # PipelineContext 생성
        context = PipelineContext(
            file_id=actual_file_id,
            file_path=file_path,
        )

        # 1. PreprocessStep 실행 (필수)
        preprocess_step = PreprocessStep()
        context = await preprocess_step.execute(context)

        # 2. ExtractAnswerStep 실행
        extract_answer_step = ExtractAnswerStep(min_confidence=min_confidence)
        context = await extract_answer_step.execute(context)

        # 결과 반환
        if context.extracted_answer is None:
            raise HTTPException(status_code=500, detail="extract_answer failed")

        return {
            "message": "extract_answer 완료",
            "image_id": actual_file_id,
            "result": {
                "answer_text": context.extracted_answer.get("answer_text"),
                "confidence": context.extracted_answer.get("confidence"),
                "ocr_method": context.extracted_answer.get("ocr_method"),
                "status": context.extracted_answer.get("status"),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"extract_answer failed: {str(e)}",
        ) from e
