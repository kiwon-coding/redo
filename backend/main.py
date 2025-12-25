from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 (프론트 연결용 – 중요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계에서는 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="File is required")

    # 파일 기본 정보
    filename = file.filename
    content_type = file.content_type

    # 실제 파일 내용을 읽어보기 (바이트)
    contents = await file.read()
    file_size = len(contents)

    # ⚠️ 지금은 분석 안 함 (더미 응답)
    return {
        "filename": filename,
        "content_type": content_type,
        "file_size": file_size,
        "message": "이미지 업로드 및 수신 성공",
        "analysis": {"problems_detected": 5, "note": "현재는 더미 데이터입니다"},
    }
