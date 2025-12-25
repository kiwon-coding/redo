# Backend

## Run server
pipenv install
pipenv run uvicorn main:app --reload

## Test
# backend 디렉토리에서 실행
cd backend
pipenv install  # dev-packages 포함 설치
pipenv run pytest tests/ -v

## Manual test
curl -X POST "http://127.0.0.1:8000/analyze" -F "file=@/Users/kiwon/Kiwon/Projects/coding/redo/backend/test.png"