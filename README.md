# redo

Redo is an AI-powered app that turns mistakes into personalized practice tests.

## What it does
- Capture solved paper problems using a smartphone
- Extract original questions
- Remove handwritten solutions
- Re-generate practice tests and answer sheets

## Tech Stack
- Frontend: Vue 3 + Vite
- Backend: FastAPI
- AI: Vision OCR, segmentation, inpainting

## Status
MVP in progress

## Quick Start

### 방법 1: 자동 실행 스크립트 (추천)

```bash
# Backend과 Frontend를 동시에 실행
./dev.sh

# 종료하려면 Ctrl+C
```

### 방법 2: 별도 터미널에서 실행

**Backend:**
```bash
cd backend
pipenv install  # 최초 1회만
pipenv run uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install  # 최초 1회만
npm run dev
```

### 방법 3: Alias 설정 (선택사항)

`~/.zshrc` 또는 `~/.bashrc`에 추가:
```bash
alias redo-dev='cd /Users/kiwon/Kiwon/Projects/coding/redo && ./dev.sh'
alias redo-stop='cd /Users/kiwon/Kiwon/Projects/coding/redo && ./stop.sh'
```

그 후:
```bash
redo-dev    # 개발 서버 시작
redo-stop   # 개발 서버 종료
```

## URLs
- Backend API: http://127.0.0.1:8000
- Frontend: http://localhost:5173
- API Docs: http://127.0.0.1:8000/docs
