from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from services.file_storage import save_upload_file, get_file_path_by_id

app = FastAPI()

# CORS 설정 (프론트 연결용 – 중요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계에서는 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_info = await save_upload_file(file, file_id=file_id)

    return {
        "file_id": file_id,
        "stored_path": file_info["stored_path"],
        "original_filename": file_info["original_filename"],
    }


class AnalyzeRequest(BaseModel):
    file_id: str


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

    return {
        "message": "분석 완료",
        "file_id": request.file_id,
        "analysis": {
            "problems_detected": 5,
            "note": "더미 데이터",
        },
    }
