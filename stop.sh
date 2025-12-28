#!/bin/bash

# 실행 중인 Backend과 Frontend를 종료하는 스크립트

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${YELLOW}Stopping servers...${NC}"

# PID 파일에서 프로세스 종료
if [ -f /tmp/redo-backend.pid ]; then
    PID=$(cat /tmp/redo-backend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID 2>/dev/null
        echo -e "${GREEN}✓ Backend stopped${NC}"
    fi
    rm -f /tmp/redo-backend.pid
fi

if [ -f /tmp/redo-frontend.pid ]; then
    PID=$(cat /tmp/redo-frontend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID 2>/dev/null
        echo -e "${GREEN}✓ Frontend stopped${NC}"
    fi
    rm -f /tmp/redo-frontend.pid
fi

# 추가로 실행 중인 프로세스 찾아서 종료 (안전장치)
pkill -f "uvicorn main:app" 2>/dev/null && echo -e "${GREEN}✓ Additional backend processes stopped${NC}" || true
pkill -f "vite" 2>/dev/null && echo -e "${GREEN}✓ Additional frontend processes stopped${NC}" || true

echo -e "${GREEN}Done!${NC}"

