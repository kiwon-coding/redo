# Backend

## Run server
pipenv install
pipenv run uvicorn main:app --reload

## test
curl -X POST "http://127.0.0.1:8000/analyze" -F "file=@/Users/kiwon/Kiwon/Projects/coding/redo/backend/test.png"