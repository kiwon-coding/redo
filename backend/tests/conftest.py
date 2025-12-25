"""Pytest configuration for backend tests."""

import sys
from pathlib import Path

# backend 디렉토리를 Python 경로에 추가
# 이렇게 하면 backend 디렉토리에서 실행해도 services 모듈을 찾을 수 있음
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# 프로젝트 루트도 추가 (backend.main import를 위해)
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
