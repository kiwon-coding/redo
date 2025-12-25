from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from PIL import Image
from services.file_storage import save_upload_file, get_file_path_by_id
from analyze import AnalyzePipeline

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
        raise HTTPException(status_code=500, detail=f"Crop failed: {str(e)}") from e


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
        return {
            "message": "분석 완료",
            "file_id": result.file_id,
            "analysis": result.analysis,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}",
        ) from e
