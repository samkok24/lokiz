# LOKIZ 글리치 & 스튜디오 기능 완료 요약

**완료 날짜**: 2025년 10월 29일

---

## 📋 작업 목표

1. 리믹스 → 글리치로 용어 통일
2. 글리치 관계 자동 기록
3. 글리치 체인 조회 API
4. 스튜디오 편집바 API

---

## ✅ 완료된 작업

### 1. 데이터베이스 변경

#### VideoGlitch 모델 추가
- **파일**: `/home/ubuntu/lokiz-backend/app/models/social.py`
- **테이블**: `video_glitches`
- **필드**:
  - `id`: UUID (Primary Key)
  - `original_video_id`: UUID (원본 영상)
  - `glitch_video_id`: UUID (글리치 영상)
  - `glitch_type`: Text ('animate' or 'replace')
  - `created_at`: Timestamp

#### 마이그레이션
```bash
alembic revision --autogenerate -m "Add video_glitches table"
alembic upgrade head
```

---

### 2. 글리치 관계 자동 기록

#### AI 라우터 수정
- **파일**: `/home/ubuntu/lokiz-backend/app/routers/ai.py`
- **변경사항**:
  - 글리치 생성 시 새로운 Video 레코드 자동 생성
  - VideoGlitch 관계 자동 기록
  - 원본 영상과 글리치 영상 연결

#### 작동 방식
```python
# 글리치 생성 완료 후
new_video = Video(
    user_id=current_user.id,
    title=f"Glitch from {template_video.title}",
    url=result['output_url'],
    s3_key=f"glitch/{ai_job.id}.mp4",
    duration=5,
    status="completed"
)
db.add(new_video)
db.flush()

# 글리치 관계 기록
video_glitch = VideoGlitch(
    original_video_id=template_video.id,
    glitch_video_id=new_video.id,
    glitch_type="animate"  # or "replace"
)
db.add(video_glitch)
```

---

### 3. 글리치 체인 조회 API

#### 새로운 라우터
- **파일**: `/home/ubuntu/lokiz-backend/app/routers/glitch.py`
- **스키마**: `/home/ubuntu/lokiz-backend/app/schemas/glitch.py`

#### API 엔드포인트

##### A. 글리치 목록 조회
```
GET /v1/glitch/videos/{video_id}/glitches
```

**설명**: 이 영상을 템플릿으로 사용해서 만든 모든 글리치 목록

**응답**:
```json
{
  "original_video_id": "uuid",
  "glitch_count": 42,
  "glitches": [
    {
      "id": "uuid",
      "glitch_video_id": "uuid",
      "glitch_type": "animate",
      "created_at": "2025-10-29T...",
      "video": {
        "id": "uuid",
        "title": "Glitch from dance video",
        "url": "https://...",
        "user_id": "uuid",
        "created_at": "2025-10-29T..."
      }
    }
  ]
}
```

**사용 사례**:
- 피드에서 "이 영상으로 만든 글리치 42개" 표시
- 인기 있는 템플릿 영상 발견
- 글리치 체인 시각화

##### B. 글리치 원본 조회
```
GET /v1/glitch/videos/{video_id}/source
```

**설명**: 이 영상이 어떤 원본 영상에서 만들어졌는지 조회

**응답 (글리치인 경우)**:
```json
{
  "glitch_video_id": "uuid",
  "original_video_id": "uuid",
  "glitch_type": "animate",
  "original_video": {
    "id": "uuid",
    "title": "Original dance video",
    "url": "https://...",
    "user_id": "uuid",
    "created_at": "2025-10-29T..."
  }
}
```

**응답 (일반 영상인 경우)**:
```json
{
  "glitch_video_id": "uuid",
  "original_video_id": null,
  "glitch_type": null,
  "original_video": null
}
```

**사용 사례**:
- 피드에서 "Glitched from @username" 표시
- 원본 영상으로 이동
- 글리치 출처 표시

---

### 4. 스튜디오 편집바 API

#### 새로운 라우터
- **파일**: `/home/ubuntu/lokiz-backend/app/routers/studio.py`

#### API 엔드포인트

##### A. 타임라인 정보
```
GET /v1/studio/videos/{video_id}/timeline
```

**설명**: 비디오 타임라인 정보 조회 (편집바 렌더링용)

**응답**:
```json
{
  "video_id": "uuid",
  "title": "My video",
  "url": "https://...",
  "duration": 30.5,
  "status": "completed",
  "created_at": "2025-10-29T...",
  "timeline": {
    "total_duration": 30.5,
    "frame_rate": 30,
    "total_frames": 915
  }
}
```

**사용 사례**:
- 스튜디오 편집바 렌더링
- 타임라인 슬라이더 초기화
- 프레임 수 계산

##### B. 미리보기
```
GET /v1/studio/videos/{video_id}/preview?timestamp=5.5
```

**설명**: 특정 시간대의 비디오 미리보기 URL

**응답**:
```json
{
  "video_id": "uuid",
  "url": "https://...",
  "timestamp": 5.5,
  "duration": 30.5,
  "preview_url": "https://...#t=5.5"
}
```

**사용 사례**:
- 타임라인 스크러빙 (마우스로 드래그)
- 프레임 캡처 전 미리보기
- 특정 시간대 확인

##### C. 구간 선택
```
POST /v1/studio/videos/{video_id}/select-range
```

**요청**:
```json
{
  "start_time": 5.0,
  "end_time": 15.0
}
```

**응답**:
```json
{
  "video_id": "uuid",
  "start_time": 5.0,
  "end_time": 15.0,
  "duration": 10.0,
  "url": "https://...",
  "range_url": "https://...#t=5.0,15.0"
}
```

**제약사항**:
- 최대 10초 구간 (AI 처리 제한)
- start_time < end_time
- end_time ≤ video.duration

**사용 사례**:
- AI 처리할 구간 선택
- 10초 클립 추출
- 구간 유효성 검증

---

## 🎯 전체 워크플로우

### 글리치 생성 워크플로우

1. **피드에서 영상 발견**
   ```
   GET /v1/videos/
   ```

2. **글리치 버튼 클릭**
   - 템플릿 영상 ID 저장

3. **스튜디오 진입**
   ```
   GET /v1/studio/videos/{my_video_id}/timeline
   ```

4. **타임라인 스크러빙**
   ```
   GET /v1/studio/videos/{my_video_id}/preview?timestamp=5.5
   ```

5. **프레임 캡처**
   ```
   POST /v1/ai/capture-frame
   {
     "video_id": "my_video_id",
     "timestamp": 5.5
   }
   ```

6. **글리치 생성**
   ```
   POST /v1/ai/glitch/animate
   {
     "template_video_id": "template_video_id",
     "user_image_url": "captured_frame_url"
   }
   ```

7. **자동 처리**
   - AI 작업 생성
   - Replicate API 호출
   - 새로운 Video 레코드 생성
   - VideoGlitch 관계 기록

8. **결과 확인**
   ```
   GET /v1/ai/jobs/{job_id}
   ```

9. **글리치 체인 확인**
   ```
   GET /v1/glitch/videos/{template_video_id}/glitches
   ```

---

## 📊 데이터베이스 구조

### video_glitches 테이블
```sql
CREATE TABLE video_glitches (
    id UUID PRIMARY KEY,
    original_video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    glitch_video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    glitch_type TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_glitch_video UNIQUE (glitch_video_id)
);

CREATE INDEX ix_video_glitches_original_video_id ON video_glitches(original_video_id);
CREATE INDEX ix_video_glitches_glitch_video_id ON video_glitches(glitch_video_id);
```

---

## 🔧 코드 품질

### Lint 검사
```bash
flake8 app/routers/ai.py app/routers/glitch.py app/routers/studio.py \
       app/schemas/glitch.py app/models/social.py --max-line-length=120
```
**결과**: ✅ 0개 오류

### 네이밍 규칙
- ✅ 모델: `VideoGlitch` (PascalCase)
- ✅ 테이블: `video_glitches` (snake_case)
- ✅ 함수: `get_video_glitches` (snake_case)
- ✅ 변수: `glitch_video_id` (snake_case)

---

## 📈 API 전체 목록

### 인증 (3개)
- `POST /v1/auth/register`
- `POST /v1/auth/login`
- `GET /v1/auth/me`

### 비디오 (5개)
- `POST /v1/videos/upload-url`
- `PATCH /v1/videos/{video_id}`
- `GET /v1/videos/{video_id}`
- `GET /v1/videos/`
- `DELETE /v1/videos/{video_id}`

### AI 작업 (6개)
- `POST /v1/ai/capture-frame`
- `POST /v1/ai/template`
- `POST /v1/ai/glitch/animate`
- `POST /v1/ai/glitch/replace`
- `POST /v1/ai/music`
- `GET /v1/ai/jobs/{job_id}`

### 글리치 (2개) ⭐ NEW
- `GET /v1/glitch/videos/{video_id}/glitches`
- `GET /v1/glitch/videos/{video_id}/source`

### 스튜디오 (3개) ⭐ NEW
- `GET /v1/studio/videos/{video_id}/timeline`
- `GET /v1/studio/videos/{video_id}/preview`
- `POST /v1/studio/videos/{video_id}/select-range`

**총 19개 API 엔드포인트**

---

## 🎉 완료!

모든 글리치 및 스튜디오 기능이 성공적으로 구현되었습니다!

### 다음 단계
- Phase 4: 소셜 기능 API (좋아요, 댓글, 팔로우)
- Phase 5: 프론트엔드 개발

