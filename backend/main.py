from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.file_storage import save_upload_file

app = FastAPI()

# CORS 설정 (프론트 연결용 – 중요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계에서는 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        file_info = await save_upload_file(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message": "업로드 성공",
        "file": file_info,
        "analysis": {
            "problems_detected": 5,
            "note": "더미 데이터",
        },
    }
