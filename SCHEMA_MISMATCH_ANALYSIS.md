# 데이터베이스 스키마 불일치 분석

## 문제 요약

Video 모델의 데이터베이스 스키마와 코드에서 사용하는 필드 간에 심각한 불일치가 발견되었습니다.

## 현재 데이터베이스 스키마 (videos 테이블)

```sql
id                  UUID        NOT NULL (PK)
user_id             UUID        NOT NULL (FK -> users.id)
caption             TEXT        NULL
video_url           VARCHAR(500) NOT NULL
thumbnail_url       VARCHAR(500) NOT NULL
duration_seconds    INTEGER     NOT NULL
view_count          INTEGER     NOT NULL (default: 0)
like_count          INTEGER     NOT NULL (default: 0)
comment_count       INTEGER     NOT NULL (default: 0)
remix_count         INTEGER     NOT NULL (default: 0)
original_video_id   UUID        NULL (FK -> videos.id)
created_at          TIMESTAMP   NOT NULL
updated_at          TIMESTAMP   NOT NULL
```

## 코드에서 사용 중인 필드 (실제 존재하지 않음)

### 1. `status` 필드 (8회 사용)
- **사용 위치:**
  - `app/routers/video.py`: 피드 필터링 (status == "completed")
  - `app/routers/ai.py`: Video 생성 시 status="processing" 설정
  - `app/routers/glitch.py`: 접근 제어 (status == "private")
  - `app/routers/studio.py`: 접근 제어 및 응답 반환
  - `app/routers/search.py`: 검색 필터링
  - `app/routers/hashtag.py`: 해시태그 비디오 필터링
  - `app/routers/user.py`: 사용자 프로필 통계

- **예상 값:**
  - "processing": AI 작업 진행 중
  - "completed": 완료됨 (공개 가능)
  - "failed": 실패
  - "private": 비공개

### 2. `is_public` 필드 (3회 사용)
- **사용 위치:**
  - `app/routers/video.py`: Soft delete 시 is_public=False 설정
  - `app/routers/search.py`: 비인증 사용자 검색 필터링
  - `app/routers/hashtag.py`: 해시태그 비디오 필터링

- **예상 값:**
  - True: 공개
  - False: 비공개 (삭제된 비디오 포함)

### 3. `title` 필드 (5회 사용)
- **사용 위치:**
  - `app/routers/ai.py`: I2V 템플릿, 글리치 생성 시 title 설정

- **예상 값:**
  - "Template: {template_name}"
  - "Glitch from {original_title}"

### 4. `url` 필드 (11회 사용)
- **사용 위치:**
  - `app/routers/ai.py`: Video 생성 시 url 설정
  - 여러 라우터에서 video.url 참조

- **참고:** 현재 DB에는 `video_url` 필드가 존재

### 5. `duration` 필드 (11회 사용)
- **사용 위치:**
  - 여러 라우터에서 video.duration 참조

- **참고:** 현재 DB에는 `duration_seconds` 필드가 존재

### 6. 기타 필드
- `width`, `height`: VideoCreateRequest에 정의되어 있으나 DB에 없음
- `s3_key`: AI 라우터에서 사용하나 DB에 없음
- `glitch_count`: VideoResponse에 정의되어 있으나 DB에 없음 (계산 필드로 추정)

## 누락된 필드 (DB에 없지만 필요한 필드)

### 필수 추가 필드:
1. **status** (VARCHAR(20), NOT NULL, default='processing')
   - 값: 'processing', 'completed', 'failed'
   - 인덱스 필요 (필터링에 자주 사용)

2. **is_public** (BOOLEAN, NOT NULL, default=True)
   - Soft delete 구현에 필요
   - 인덱스 필요 (필터링에 자주 사용)

3. **deleted_at** (TIMESTAMP, NULL)
   - Soft delete 시점 기록
   - 인덱스 필요

### 선택적 추가 필드:
4. **title** (VARCHAR(200), NULL)
   - AI 생성 비디오 제목
   
5. **width** (INTEGER, NULL)
   - 비디오 해상도 (가로)

6. **height** (INTEGER, NULL)
   - 비디오 해상도 (세로)

7. **s3_key** (VARCHAR(500), NULL)
   - S3 저장 키 (향후 S3 통합 시 필요)

## 필드명 불일치

### 현재 DB vs 코드 사용:
- `video_url` (DB) vs `url` (코드)
- `duration_seconds` (DB) vs `duration` (코드)

### 해결 방안:
**옵션 1:** DB 필드명 변경 (권장하지 않음 - 마이그레이션 복잡)
**옵션 2:** 코드에서 올바른 필드명 사용 (권장)
**옵션 3:** SQLAlchemy property 사용하여 별칭 제공

## 권장 수정 사항

### 1단계: Video 모델 수정
```python
# app/models/video.py
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean

class Video(Base):
    __tablename__ = "videos"
    
    # 기존 필드...
    status = Column(String(20), nullable=False, default="processing", index=True)
    is_public = Column(Boolean, nullable=False, default=True, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    title = Column(String(200), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    s3_key = Column(String(500), nullable=True)
```

### 2단계: Alembic 마이그레이션 생성
```bash
alembic revision --autogenerate -m "Add status, is_public, deleted_at, title, width, height, s3_key to videos"
alembic upgrade head
```

### 3단계: 코드 수정
- `video.url` → `video.video_url`
- `video.duration` → `video.duration_seconds`
- 모든 라우터에서 일관성 있게 수정

### 4단계: 기존 데이터 마이그레이션
```sql
-- 기존 비디오는 모두 completed, public 상태로 설정
UPDATE videos SET status = 'completed', is_public = true WHERE status IS NULL;
```

## 영향 범위

### 수정 필요한 파일:
1. `app/models/video.py` - Video 모델 필드 추가
2. `app/routers/video.py` - status, is_public 사용 부분
3. `app/routers/ai.py` - Video 생성 부분
4. `app/routers/glitch.py` - status 체크 부분
5. `app/routers/studio.py` - status 체크 부분
6. `app/routers/search.py` - status, is_public 필터링
7. `app/routers/hashtag.py` - status, is_public 필터링
8. `app/routers/user.py` - status 필터링
9. Alembic 마이그레이션 파일 생성

### 테스트 필요 항목:
- [ ] 비디오 생성 (AI 템플릿)
- [ ] 비디오 피드 조회
- [ ] 비디오 삭제 (soft delete)
- [ ] 비인증 사용자 접근
- [ ] 검색 기능
- [ ] 해시태그 비디오 조회
- [ ] 사용자 프로필 통계

## 우선순위

### P0 (즉시 수정 필요):
- status 필드 추가 및 마이그레이션
- is_public 필드 추가 및 마이그레이션
- 필드명 불일치 수정 (url, duration)

### P1 (중요):
- deleted_at 필드 추가 (soft delete 개선)
- title 필드 추가 (AI 비디오 구분)

### P2 (선택적):
- width, height 필드 추가 (향후 반응형 플레이어)
- s3_key 필드 추가 (향후 S3 통합)

## 다음 단계

1. ✅ 분석 완료
2. ⏳ Video 모델 수정
3. ⏳ Alembic 마이그레이션 생성 및 실행
4. ⏳ 코드 전체 수정 (필드명 통일)
5. ⏳ 통합 테스트
6. ⏳ 문서 업데이트

