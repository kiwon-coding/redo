#!/bin/bash

# Backend과 Frontend를 동시에 실행하는 스크립트

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# 종료 함수
cleanup() {
    echo -e "\n${YELLOW}종료 중...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    rm -f /tmp/redo-backend.pid /tmp/redo-frontend.pid
    exit 0
}

# 시그널 핸들러 등록
trap cleanup SIGINT SIGTERM

# 의존성 확인
check_dependencies() {
    # pipenv 확인
    if ! command -v pipenv &> /dev/null; then
        echo -e "${RED}✗ pipenv가 설치되어 있지 않습니다.${NC}"
        echo -e "${YELLOW}설치: pip install pipenv${NC}"
        exit 1
    fi
    
    # npm 확인
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}✗ npm이 설치되어 있지 않습니다.${NC}"
        echo -e "${YELLOW}Node.js를 설치해주세요: https://nodejs.org/${NC}"
        exit 1
    fi
}

check_dependencies

# Backend 실행
echo -e "${BLUE}🚀 Starting Backend...${NC}"
cd "$BACKEND_DIR"
if [ ! -f "Pipfile.lock" ]; then
    echo -e "${YELLOW}📦 Installing backend dependencies...${NC}"
    pipenv install
fi
pipenv run uvicorn main:app --reload --host 127.0.0.1 --port 8000 > /tmp/redo-backend.log 2>&1 &
BACKEND_PID=$!

# 잠시 대기 (서버 시작 확인)
sleep 2

# Frontend 실행
echo -e "${BLUE}🚀 Starting Frontend...${NC}"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm install
fi
npm run dev > /tmp/redo-frontend.log 2>&1 &
FRONTEND_PID=$!

# PID 저장 (나중에 종료하기 위해)
echo $BACKEND_PID > /tmp/redo-backend.pid
echo $FRONTEND_PID > /tmp/redo-frontend.pid

echo -e "\n${GREEN}✓ Backend: http://127.0.0.1:8000${NC}"
echo -e "${GREEN}✓ Frontend: http://localhost:5173${NC}"
echo -e "${GREEN}✓ API Docs: http://127.0.0.1:8000/docs${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo -e "${YELLOW}Logs: tail -f /tmp/redo-{backend,frontend}.log${NC}\n"

# 두 프로세스가 종료될 때까지 대기
wait

