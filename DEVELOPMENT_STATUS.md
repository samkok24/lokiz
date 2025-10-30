# LOKIZ Backend Development Status

**마지막 업데이트**: 2025년 10월 29일

---

## 프로젝트 정보
- **프로젝트명**: LOKIZ (로키즈)
- **슬로건**: "Play like a trickster"
- **컨셉**: AI 비디오 리믹스 플랫폼 (Gen Z 타겟)

---

## ✅ 완료된 작업

### Phase 1: 데이터베이스 스키마 및 인증 API

**완료 항목**:
1. PostgreSQL 데이터베이스 설정
2. SQLAlchemy 모델 작성
   - User (사용자)
   - Video (비디오)
   - AIJob (AI 작업)
   - Like, Comment, Follow (소셜 기능)
3. Alembic 마이그레이션 설정 및 적용
4. 이메일 기반 인증 시스템
   - 회원가입 API
   - 로그인 API (JWT)
   - 사용자 정보 조회 API
5. 코드 품질 검수
   - flake8 lint 검사 통과 (0개 오류)
   - 네이밍 규칙 준수
   - 코드 스타일 통일

**API 엔드포인트**:
- `POST /v1/auth/register` - 회원가입
- `POST /v1/auth/login` - 로그인
- `GET /v1/auth/me` - 현재 사용자 정보

**테스트 결과**: ✅ 모든 API 정상 작동

---

### Phase 2: 비디오 업로드 API

**완료 항목**:
1. Mock S3 서비스 구현
   - 개발 환경용 Mock S3 서비스
   - Pre-signed URL 생성 (Mock)
2. 비디오 스키마 작성
   - VideoUploadRequest
   - VideoUploadResponse
   - VideoResponse
   - VideoListResponse
3. 비디오 라우터 구현
   - 업로드 URL 생성 API
   - 비디오 메타데이터 업데이트 API
   - 비디오 조회 API
   - 비디오 목록 API
   - 비디오 삭제 API
4. 코드 품질 검수
   - flake8 lint 검사 통과
   - 스키마와 모델 필드 일치 확인

**API 엔드포인트**:
- `POST /v1/videos/upload-url` - 업로드 URL 생성
- `PATCH /v1/videos/{video_id}` - 비디오 메타데이터 업데이트
- `GET /v1/videos/{video_id}` - 비디오 조회
- `GET /v1/videos/` - 비디오 목록 (피드)
- `DELETE /v1/videos/{video_id}` - 비디오 삭제

**테스트 결과**: ✅ 업로드 URL 생성 API 정상 작동

---

## 📊 API 테스트 결과

### 회원가입 (POST /v1/auth/register)
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": "0238e512-ec05-4ad6-9c8b-3405153d49e1",
    "username": "video_tester",
    "email": "video@test.com",
    "display_name": "video_tester",
    "credits": 100,
    "created_at": "2025-10-29T05:18:17.263629-04:00"
  }
}
```

### 비디오 업로드 URL 생성 (POST /v1/videos/upload-url)
```json
{
  "upload_url": "https://mock-s3.lokiz.dev/upload/videos/728df723-3ea8-4326-b5d8-16ac726518d7.mp4?mock=true",
  "file_key": "videos/728df723-3ea8-4326-b5d8-16ac726518d7.mp4",
  "file_url": "https://mock-s3.lokiz.dev/lokiz-videos-mock/videos/728df723-3ea8-4326-b5d8-16ac726518d7.mp4",
  "video_id": "86c16e64-45b1-43b7-9aa8-881ac2beb240"
}
```

---

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 14
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic
- **Authentication**: JWT (PyJWT)
- **Password Hashing**: bcrypt
- **Validation**: Pydantic

### Development Tools
- **Linter**: flake8
- **Formatter**: autopep8
- **Type Checker**: mypy

### Infrastructure (개발 환경)
- **File Storage**: Mock S3 (개발용)
- **Cache**: Redis (예정)
- **Task Queue**: Celery (예정)

---

## 📁 데이터베이스 스키마

### 테이블 목록
1. **users** - 사용자 정보
2. **videos** - 비디오 메타데이터
3. **ai_jobs** - AI 작업 (I2V, VTV, 음악 생성 등)
4. **likes** - 좋아요
5. **comments** - 댓글
6. **follows** - 팔로우
7. **alembic_version** - 마이그레이션 버전

---

## 🚀 서버 실행 방법

### 개발 서버 시작
```bash
cd /home/ubuntu/lokiz-backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### API 문서 확인
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

---

## ✅ 코드 품질 검사

### Lint 검사
```bash
flake8 app/ --max-line-length=120 --exclude=venv,alembic --count
```

**결과**: ✅ 0개 오류

### 자동 포맷팅
```bash
autopep8 --in-place --aggressive --aggressive --recursive app/
```

---

### Phase 3: AI 작업 API

**완료 항목**:
1. Replicate API 통합
   - API 키 설정 완료
   - replicate 패키지 설치
2. Replicate 서비스 구현
   - I2V 템플릿 생성 (veo-3-fast)
   - 글리치 모션 적용 (WAN 2.2 Animate)
   - 글리치 주체 교체 (WAN 2.2 Replace)
   - 음악 생성 (suno-ai/bark)
3. 프레임 캡처 유틸리티
   - ffmpeg 기반 프레임 추출
   - 비디오 길이 확인
4. AI 작업 스키마 업데이트
   - I2V 템플릿 요청/응답
   - 글리치 요청/응답
   - 프레임 캡처 요청/응답
5. 코드 품질 검수
   - flake8 lint 검사 통과
   - 네이밍 규칙 준수

**API 엔드포인트**:
- `POST /v1/ai/capture-frame` - 프레임 캡처 (0 크레딧)
- `POST /v1/ai/template` - 모션/스타일 템플릿 (20 크레딧)
- `POST /v1/ai/glitch/animate` - 글리치 모션 적용 (30 크레딧)
- `POST /v1/ai/glitch/replace` - 글리치 주체 교체 (30 크레딧)
- `POST /v1/ai/music` - 음악 생성 (5 크레딧)
- `GET /v1/ai/jobs/{job_id}` - AI 작업 상태 조회

**테스트 결과**: ✅ 모든 API 엔드포인트 등록 완료

**중요 변경사항**:
- VTV → I2V 기반으로 전환
- 스튜디오 워크플로우: 영상 업로드 → 프레임 캡처 → 템플릿 프롬프트 + I2V
- 글리치 기능 추가 (피드 → 스튜디오 워크플로우)

---

### Phase 3.5: 글리치 및 스튜디오 기능

**완료 항목**:
1. 데이터베이스 변경
   - `video_remixes` → `video_glitches` 테이블로 변경
   - VideoGlitch 모델 추가
   - Alembic 마이그레이션 적용
2. 글리치 관계 자동 기록
   - AI 라우터에서 자동으로 Video 레코드 생성
   - VideoGlitch 관계 자동 기록
3. 글리치 체인 조회 API
   - 글리치 목록 조회
   - 글리치 원본 조회
4. 스튜디오 편집바 API
   - 타임라인 정보
   - 미리보기
   - 구간 선택 (10초 제한)
5. 코드 품질 검수
   - flake8 lint 검사 통과
   - 네이밍 규칙 준수

**API 엔드포인트**:
- `GET /v1/glitch/videos/{video_id}/glitches` - 글리치 목록 조회
- `GET /v1/glitch/videos/{video_id}/source` - 글리치 원본 조회
- `GET /v1/studio/videos/{video_id}/timeline` - 타임라인 정보
- `GET /v1/studio/videos/{video_id}/preview` - 미리보기
- `POST /v1/studio/videos/{video_id}/select-range` - 구간 선택

**테스트 결과**: ✅ 모든 API 엔드포인트 등록 완료

**중요 변경사항**:
- 리믹스 → 글리치로 용어 통일
- 글리치 = AI 기반 2차 창작 (다른 사람 영상을 템플릿으로 사용)
- 글리치 체인 추적 가능 (원본 → 글리치 → 글리치의 글리치)

---

### Phase 4: 소셜 기능 API (완료 ✅)

**완료 항목**:
1. 좋아요 API (3개)
   - POST /v1/likes/videos/{video_id}
   - DELETE /v1/likes/videos/{video_id}
   - GET /v1/likes/videos/{video_id}/check
2. 댓글 API (5개)
   - POST /v1/comments/videos/{video_id}
   - GET /v1/comments/videos/{video_id}
   - PATCH /v1/comments/{comment_id}
   - DELETE /v1/comments/{comment_id}
3. 팔로우 API (5개)
   - POST /v1/follows/users/{user_id}
   - DELETE /v1/follows/users/{user_id}
   - GET /v1/follows/users/{user_id}/followers
   - GET /v1/follows/users/{user_id}/following
   - GET /v1/follows/users/{user_id}/check
4. 자동 카운트 관리
   - like_count, comment_count 자동 증감
5. 중복 방지 (UniqueConstraint)
6. 권한 검증 (본인만 수정/삭제)
7. 페이지네이션 지원

**테스트 결과**: ✅ 총 29개 API 엔드포인트 정상 작동

---

## 🚧 다음 단계

### Phase 5: 프론트엔드 개발 (예정)
1. React + TypeScript 설정
2. 인증 UI
3. 비디오 업로드 UI
4. 피드 UI
5. AI 편집 UI

---

## ⚠️ 주의사항

### 개발 환경
- Mock S3 사용 중 (실제 AWS S3 연동 필요)
- LocalStack 미사용 (Docker 미설치)
- 실제 배포 시 S3 엔드포인트 변경 필요

### 보안
- `.env` 파일은 Git에 커밋하지 않음
- 프로덕션 환경에서는 SECRET_KEY 변경 필수
- JWT 토큰 만료 시간: 7일 (개발용)

---

## 🔧 문제 해결

### 서버 포트 충돌
```bash
# 포트 8000이 사용 중일 경우 8001 사용
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 데이터베이스 연결 오류
```bash
# PostgreSQL 시작
sudo service postgresql start

# 데이터베이스 재생성
sudo -u postgres psql -c "DROP DATABASE IF EXISTS lokiz_db;"
sudo -u postgres psql -c "CREATE DATABASE lokiz_db;"
```

### 마이그레이션 오류
```bash
# 마이그레이션 재생성
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## 📚 참고 문서
- [LOKIZ 기획 문서](/home/ubuntu/lokiz_planning_document.md)
- [API 명세서](/home/ubuntu/lokiz_api_specification.md)
- [데이터베이스 스키마](/home/ubuntu/lokiz_database_schema.md)
- [개발 로드맵](/home/ubuntu/lokiz_development_roadmap.md)
- [코드 검수 체크리스트](/home/ubuntu/lokiz-backend/CODE_REVIEW_CHECKLIST.md)




---

## Phase 4: 소셜 기능 API

**상태**: ✅ 완료

**완료 날짜**: 2025-10-29

---

## Phase 5: 추가 기능 (알림, 검색, 해시태그)

**상태**: ✅ 완료

**완료 날짜**: 2025-10-29

### 완료된 작업
1. ✅ 알림 시스템 (4개 API)
   - 좋아요, 댓글, 팔로우, 글리치 알림
   - 읽음/읽지 않음 상태 관리
   - 자동 알림 생성
2. ✅ 검색 기능 (3개 API)
   - 사용자 검색
   - 비디오 검색
   - 통합 검색
3. ✅ 해시태그 시스템 (2개 API)
   - Caption에서 자동 추출
   - 트렌딩 해시태그
   - 해시태그별 비디오 목록

---

## 🎉 백엔드 개발 완료!

**총 39개 API 엔드포인트**

모든 핵심 기능이 구현되었습니다. 자세한 내용은 `FINAL_BACKEND_SUMMARY.md`를 참조하세요.

### 주요 성과
- ✅ 완전한 인증 시스템
- ✅ AI 기반 영상 편집 (I2V, 글리치)
- ✅ TikTok 스타일 글리치 체인
- ✅ 소셜 기능 (좋아요, 댓글, 팔로우)
- ✅ 실시간 알림
- ✅ 검색 및 해시태그
- ✅ 비로그인 접근 정책
- ✅ 코드 품질 검수 완료

### 다음 단계
- 프론트엔드 개발 (React + TypeScript)
- 배포 준비 (Docker, AWS S3, CI/CD)

