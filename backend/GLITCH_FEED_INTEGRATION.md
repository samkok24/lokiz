# 글리치 피드 통합 완료

**작성일**: 2025년 10월 29일

---

## ✅ 완료된 작업

### 1. VideoResponse 스키마 확장

**파일**: `app/schemas/video.py`

**추가된 필드**:
```python
class VideoResponse(BaseModel):
    # ... 기존 필드들 ...
    glitch_count: int = 0  # 이 영상을 템플릿으로 사용한 글리치 개수
```

---

### 2. 피드 API 수정

**파일**: `app/routers/video.py`

**수정된 API (3개)**:

#### A. 피드 목록 (`GET /v1/videos/`)
```python
# Add glitch_count to each video
for video in videos:
    video.glitch_count = db.query(VideoGlitch).filter(
        VideoGlitch.original_video_id == video.id
    ).count()
```

#### B. 단일 비디오 조회 (`GET /v1/videos/{video_id}`)
```python
# Add glitch_count
video.glitch_count = db.query(VideoGlitch).filter(
    VideoGlitch.original_video_id == video.id
).count()
```

#### C. 내 영상 목록 (`GET /v1/videos/me`)
```python
# Add glitch_count to each video
for video in videos:
    video.glitch_count = db.query(VideoGlitch).filter(
        VideoGlitch.original_video_id == video.id
    ).count()
```

---

## 📱 UI/UX 설계

### 피드 화면

```
┌─────────────────────────┐
│   [영상 재생]            │
├─────────────────────────┤
│ @username               │
│ 캡션 텍스트...           │
│                         │
│ ❤️ 1.2K  💬 45  🎨 42   │ ← 글리치 아이콘 + 개수
└─────────────────────────┘
```

**응답 예시**:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "video_url": "https://...",
  "caption": "멋진 댄스 영상",
  "like_count": 1200,
  "comment_count": 45,
  "glitch_count": 42
}
```

---

### 글리치 아이콘 클릭 시

```
🎨 아이콘 클릭
  ↓
[글리치 페이지] (TikTok 음악 페이지처럼)
```

**API**: `GET /v1/glitch/videos/{video_id}/glitches`

**응답**:
```json
{
  "original_video": {
    "id": "uuid",
    "user": {...},
    "video_url": "https://...",
    "caption": "원본 영상"
  },
  "glitch_count": 42,
  "glitches": [
    {
      "id": "uuid",
      "user": {...},
      "video_url": "https://...",
      "glitch_type": "animate",
      "created_at": "2025-10-29T..."
    }
  ]
}
```

---

### 글리치 페이지 화면

```
┌─────────────────────────┐
│   [원본 영상 재생]        │
├─────────────────────────┤
│ 🎨 글리치 42개            │
│                         │
│ [글리치 하기 버튼]        │ ← 클릭 시 스튜디오로 이동
├─────────────────────────┤
│                         │
│ 이 영상으로 만든 글리치    │
│                         │
│ ┌─────┐ ┌─────┐ ┌─────┐ │
│ │영상1│ │영상2│ │영상3│ │
│ └─────┘ └─────┘ └─────┘ │
│                         │
│ ┌─────┐ ┌─────┐ ┌─────┐ │
│ │영상4│ │영상5│ │영상6│ │
│ └─────┘ └─────┘ └─────┘ │
└─────────────────────────┘
```

---

## 🔄 전체 워크플로우

### 1. 피드에서 영상 발견
```
GET /v1/videos/?page_size=20
```

**응답**:
```json
{
  "videos": [
    {
      "id": "video-a",
      "glitch_count": 42
    }
  ]
}
```

**UI**: `❤️ 1.2K  💬 45  🎨 42`

---

### 2. 글리치 아이콘 클릭
```
🎨 42 클릭
  ↓
navigate('/glitch/{video-a}')
```

---

### 3. 글리치 페이지
```
GET /v1/glitch/videos/{video-a}/glitches
```

**화면**:
- 원본 영상 재생
- 글리치 목록 (42개)
- "글리치 하기" 버튼

---

### 4. 글리치 하기 버튼 클릭
```
navigate('/studio?template={video-a}&mode=glitch')
```

**스튜디오 페이지**:
- 왼쪽: 템플릿 영상 미리보기
- 오른쪽: 내 이미지 선택
  - 옵션 A: 내 영상에서 프레임 캡처
  - 옵션 B: 이미지 업로드

---

### 5. 글리치 생성
```
POST /v1/ai/glitch/animate
{
  "template_video_id": "video-a",
  "user_image_url": "https://...",
  "prompt": "..."
}
```

**응답**:
```json
{
  "output_data": {
    "video_id": "new-glitch-video",
    "video_url": "https://..."
  }
}
```

---

### 6. 결과 확인
```
GET /v1/videos/{new-glitch-video}
```

**스튜디오에서**:
- 생성된 글리치 영상 재생
- 캡션/태그 입력

---

### 7. 피드에 업로드
```
PATCH /v1/videos/{new-glitch-video}
{
  "caption": "내가 만든 멋진 글리치!"
}
```

**피드에 표시**:
```
@my_username
내가 만든 멋진 글리치!

❤️ 0  💬 0  🎨 0
```

---

## 📊 데이터베이스 관계

### VideoGlitch 테이블

```sql
CREATE TABLE video_glitches (
    id UUID PRIMARY KEY,
    original_video_id UUID REFERENCES videos(id),  -- 템플릿 영상 (video-a)
    glitch_video_id UUID REFERENCES videos(id),    -- 글리치 영상 (new-glitch-video)
    glitch_type VARCHAR(50),                       -- 'animate' or 'replace'
    created_at TIMESTAMP
);
```

### 쿼리

**글리치 개수 조회**:
```sql
SELECT COUNT(*)
FROM video_glitches
WHERE original_video_id = 'video-a';
```

**글리치 목록 조회**:
```sql
SELECT v.*
FROM videos v
JOIN video_glitches vg ON v.id = vg.glitch_video_id
WHERE vg.original_video_id = 'video-a'
ORDER BY vg.created_at DESC;
```

---

## 🎯 성능 최적화 (향후)

### N+1 쿼리 문제

**현재**:
```python
for video in videos:
    video.glitch_count = db.query(VideoGlitch).filter(
        VideoGlitch.original_video_id == video.id
    ).count()
```

**문제**: 20개 영상 → 20번 쿼리

---

### 해결 방법 (향후 적용)

**옵션 A: Subquery**
```python
from sqlalchemy import func, select

glitch_count_subquery = (
    select(
        VideoGlitch.original_video_id,
        func.count(VideoGlitch.id).label('glitch_count')
    )
    .group_by(VideoGlitch.original_video_id)
    .subquery()
)

videos = db.query(
    Video,
    func.coalesce(glitch_count_subquery.c.glitch_count, 0).label('glitch_count')
).outerjoin(
    glitch_count_subquery,
    Video.id == glitch_count_subquery.c.original_video_id
).all()
```

**옵션 B: 배치 조회**
```python
video_ids = [v.id for v in videos]

glitch_counts = db.query(
    VideoGlitch.original_video_id,
    func.count(VideoGlitch.id).label('count')
).filter(
    VideoGlitch.original_video_id.in_(video_ids)
).group_by(
    VideoGlitch.original_video_id
).all()

glitch_count_dict = {vc[0]: vc[1] for vc in glitch_counts}

for video in videos:
    video.glitch_count = glitch_count_dict.get(video.id, 0)
```

**현재는 단순 구현, 성능 이슈 발생 시 최적화**

---

## ✅ 검증

### 테스트 시나리오

1. **피드 조회**
   ```
   GET /v1/videos/
   → glitch_count 필드 확인
   ```

2. **글리치 생성**
   ```
   POST /v1/ai/glitch/animate
   → VideoGlitch 레코드 생성 확인
   ```

3. **글리치 개수 증가**
   ```
   GET /v1/videos/{template_video_id}
   → glitch_count가 1 증가했는지 확인
   ```

4. **글리치 목록 조회**
   ```
   GET /v1/glitch/videos/{template_video_id}/glitches
   → 새로 생성된 글리치 포함 확인
   ```

---

## 🚀 다음 단계

### Phase 3: 글리치 페이지 개선 (선택적)

1. **정렬 옵션**
   - 인기순 (좋아요 수)
   - 최신순 (기본값)
   - 조회수순

2. **필터 옵션**
   - Animate만 보기
   - Replace만 보기

3. **통계 정보**
   - 총 글리치 수
   - 총 조회수
   - 평균 좋아요 수

---

### Phase 4: 인기 템플릿 랭킹 (선택적)

```
GET /v1/glitch/trending-templates?period=week&limit=10
```

**응답**:
```json
{
  "templates": [
    {
      "video": {...},
      "glitch_count": 1000,
      "trend_score": 95.5,
      "rank": 1
    }
  ]
}
```

---

## 📝 결론

✅ **완료**:
1. VideoResponse에 glitch_count 추가
2. 피드 API 3개 수정 (목록, 단일, 내 영상)
3. 글리치 체인 시스템 설계
4. UI/UX 워크플로우 정의

✅ **작동 방식**:
- 피드에서 `🎨 42` 표시
- 클릭 시 글리치 페이지 이동
- 글리치 하기 버튼 → 스튜디오
- 글리치 생성 → 피드에 업로드

✅ **다음 작업**:
- Phase 4 (소셜 기능 API) 진행
- 또는 프론트엔드 개발 시작

