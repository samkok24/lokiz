# LOKIZ - AI Video Glitch Platform

AI 기반 비디오 글리치 효과 플랫폼

## 프로젝트 구조

```
lokiz/
├── frontend/     # React + TypeScript 프론트엔드
└── backend/      # FastAPI Python 백엔드
```

## Frontend

틱톡 스타일의 AI 비디오 글리치 플랫폼 프론트엔드

**기술 스택:**
- React 19
- TypeScript
- Tailwind CSS 4
- Vite
- shadcn/ui

**실행 방법:**
```bash
cd frontend
pnpm install
pnpm dev
```

## Backend

FastAPI 기반 RESTful API 서버

**기술 스택:**
- Python 3.11+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

**실행 방법:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 라이선스

MIT

