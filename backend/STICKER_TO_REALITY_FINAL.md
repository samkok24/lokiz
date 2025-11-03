# AI 자동 통합 (Sticker to Reality) 최종 구현

**작업일:** 2025년 10월 30일  
**상태:** ✅ 완료 및 검증됨

---

## 📋 구현 개요

### 기획서 요구사항

> **C. AI 자동 통합 (Sticker to Reality)**
> - 영상에 다른 이미지를 AI가 자연스럽게 합성하여 '현실에 스티커가 붙은 듯한' 효과를 구현
> - **길이 제한**: 10초 (사용자가 60초 영상 중 10초 구간 선택)
> - **크레딧**: 40-50 크레딧

### 구현 완료 ✅

**API 엔드포인트:**
```
POST /v1/ai/sticker-to-reality
```

**두 가지 사용 모드 지원:**
1. **글리치 모드** - 다른 사람 영상을 템플릿으로 사용
2. **편집 모드** - 내 영상(업로드 또는 I2V 생성)에 이미지 합성

---

## 🎯 API 스펙

### 엔드포인트

```http
POST /v1/ai/sticker-to-reality
Content-Type: application/json
Authorization: Bearer {token}
```

### 요청 파라미터

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `video_id` | UUID | ✅ | - | 대상 영상 ID (글리치 또는 편집) |
| `user_image_url` | string | ✅ | - | 합성할 이미지 URL |
| `start_time` | float | ✅ | - | 시작 시간 (초) |
| `end_time` | float | ✅ | - | 종료 시간 (초, 최대 10초) |
| `prompt` | string | ✅ | - | 합성 방법 지시 |
| `is_glitch` | boolean | ❌ | `false` | 글리치 모드 여부 |

### 요청 예시

**글리치 모드 (다른 사람 영상):**
```json
{
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_image_url": "https://example.com/my-sticker.png",
  "start_time": 5.0,
  "end_time": 15.0,
  "prompt": "Make the sticker follow the person's hand movement naturally with realistic shadows",
  "is_glitch": true
}
```

**편집 모드 (내 영상):**
```json
{
  "video_id": "660e8400-e29b-41d4-a716-446655440000",
  "user_image_url": "https://example.com/my-sticker.png",
  "start_time": 0.0,
  "end_time": 10.0,
  "prompt": "Place the sticker in the center and make it rotate smoothly",
  "is_glitch": false
}
```

### 응답

**성공 (200 OK):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "user_id": "880e8400-e29b-41d4-a716-446655440000",
  "job_type": "sticker_to_reality",
  "status": "completed",
  "input_data": {
    "video_id": "550e8400-e29b-41d4-a716-446655440000",
    "video_url": "https://...",
    "user_image_url": "https://...",
    "start_time": 5.0,
    "end_time": 15.0,
    "prompt": "Make the sticker follow...",
    "is_glitch": true
  },
  "output_data": {
    "video_url": "https://replicate.delivery/...",
    "model": "luma/modify-video",
    "video_id": "990e8400-e29b-41d4-a716-446655440000"
  },
  "credits_used": 45,
  "created_at": "2025-10-30T12:00:00Z",
  "updated_at": "2025-10-30T12:02:30Z"
}
```

**크레딧 부족 (402 Payment Required):**
```json
{
  "detail": "Insufficient credits. Required: 45, Available: 20"
}
```

**권한 없음 (403 Forbidden):**
```json
{
  "detail": "You can only edit your own videos. Set is_glitch=True to glitch others' videos."
}
```

**영상 없음 (404 Not Found):**
```json
{
  "detail": "Video not found"
}
```

**구간 초과 (400 Bad Request):**
```json
{
  "detail": "Duration cannot exceed 10 seconds"
}
```

---

## 🎨 사용 시나리오

### 시나리오 1: 글리치 (피드에서 다른 사람 영상)

**워크플로우:**

1. **피드에서 영상 발견**
   ```
   사용자가 피드를 스크롤하다가 재미있는 영상 발견
   ```

2. **글리치 버튼 클릭**
   ```
   "글리치" 버튼 클릭 → 글리치 모달 표시
   GET /v1/glitch/videos/{video_id}/glitches
   → 이 영상으로 만든 다른 글리치들 표시
   ```

3. **스튜디오 진입**
   ```
   "글리치 만들기" 버튼 클릭
   → 스튜디오 페이지로 이동
   → 템플릿 영상이 메인 영상 위치에 로드
   → "글리치 모드" 배지 표시
   ```

4. **구간 선택 (최대 10초)**
   ```
   타임라인 스크러빙으로 구간 선택
   start_time: 5.0, end_time: 15.0
   ```

5. **이미지 레이어 추가**
   ```
   "이미지 추가" 버튼 클릭
   → 갤러리에서 이미지 선택 또는 업로드
   → 레이어에 이미지 추가
   ```

6. **텍스트 프롬프트 입력**
   ```
   "손 움직임을 따라가도록 스티커를 자연스럽게 합성해줘"
   ```

7. **글리치 버튼 클릭**
   ```
   POST /v1/ai/sticker-to-reality
   {
     "video_id": "template-video-id",
     "user_image_url": "...",
     "start_time": 5.0,
     "end_time": 15.0,
     "prompt": "...",
     "is_glitch": true
   }
   ```

8. **결과 영상 생성**
   ```
   - 새 Video 레코드 생성
   - VideoGlitch 관계 기록
   - 템플릿 영상의 glitch_count += 1
   - 템플릿 영상 소유자에게 알림
   ```

---

### 시나리오 2: 편집 (내 영상)

**워크플로우:**

1. **스튜디오에서 영상 업로드 또는 I2V 생성**
   ```
   POST /v1/videos/upload
   또는
   POST /v1/ai/template (I2V)
   ```

2. **편집 모드 진입**
   ```
   업로드/생성된 영상이 메인 영상 위치에 표시
   ```

3. **구간 선택 (최대 10초)**
   ```
   타임라인 스크러빙으로 구간 선택
   start_time: 0.0, end_time: 10.0
   ```

4. **이미지 레이어 추가**
   ```
   "이미지 추가" 버튼 클릭
   → 갤러리에서 이미지 선택
   → 레이어에 이미지 추가
   ```

5. **텍스트 프롬프트 입력**
   ```
   "중앙에 스티커를 배치하고 부드럽게 회전시켜줘"
   ```

6. **적용 버튼 클릭**
   ```
   POST /v1/ai/sticker-to-reality
   {
     "video_id": "my-video-id",
     "user_image_url": "...",
     "start_time": 0.0,
     "end_time": 10.0,
     "prompt": "...",
     "is_glitch": false
   }
   ```

7. **결과 영상 생성**
   ```
   - 새 Video 레코드 생성 (내 계정)
   - 글리치 관계 없음
   - 알림 없음
   ```

---

## 🔒 보안 및 권한

### 글리치 모드 (`is_glitch=true`)
- ✅ 누구나 다른 사람 영상을 글리치 가능
- ✅ VideoGlitch 관계 기록
- ✅ 원본 소유자에게 알림

### 편집 모드 (`is_glitch=false`)
- ✅ **소유권 확인** - 본인 영상만 편집 가능
- ❌ 다른 사람 영상 편집 시도 → 403 Forbidden
- ✅ 글리치 관계 없음
- ✅ 알림 없음

### 권한 검증 로직
```python
# If not glitch mode, verify ownership
if not request.is_glitch and source_video.user_id != current_user.id:
    raise HTTPException(
        status_code=403,
        detail="You can only edit your own videos. Set is_glitch=True to glitch others' videos."
    )
```

---

## 💰 크레딧 시스템

### 비용
- **45 크레딧** (기획서: 40-50 크레딧 범위 내)

### 크레딧 차감 정책
1. ✅ **성공 시에만 차감**
2. ❌ 실패 시 차감 안 함
3. ⏳ 처리 중에는 차감 안 함

### 크레딧 확인 흐름
```python
# 1. Check credits before processing
if current_user.credits < CREDITS_REQUIRED:
    raise HTTPException(status_code=402, ...)

# 2. Create AI job (no credit deduction yet)
ai_job = AIJob(...)
db.add(ai_job)
db.commit()

# 3. Generate video using Replicate
result = replicate_service.generate_sticker_to_reality(...)

# 4. Success: Deduct credits
current_user.credits -= CREDITS_REQUIRED
db.commit()
```

---

## 🤖 AI 모델

### Luma Dream Machine

**모델:** `luma/modify-video`

**기능:**
- ✅ 자동 배경 제거 (`remove_background: true`)
- ✅ 맥락 인식 (`context_aware: true`)
- ✅ 움직임 분석
- ✅ 조명/그림자 적용
- ✅ 자연스러운 통합

**API 호출:**
```python
def generate_sticker_to_reality(
    self,
    video_url: str,
    image_url: str,
    start_time: float,
    end_time: float,
    prompt: str
) -> dict:
    """Generate Sticker to Reality video"""
    output = self.client.run(
        "luma/modify-video",
        input={
            "video_url": video_url,
            "image_url": image_url,
            "start_time": start_time,
            "end_time": end_time,
            "prompt": prompt,
            "remove_background": True,
            "context_aware": True
        }
    )
    return {
        "output_url": output,
        "model": "luma/modify-video"
    }
```

---

## 📊 데이터베이스

### Video 테이블
```sql
-- 새 영상 레코드 생성
INSERT INTO videos (
  id,
  user_id,
  title,
  video_url,
  thumbnail_url,
  s3_key,
  duration_seconds,
  status
) VALUES (
  'new-video-id',
  'user-id',
  'Sticker to Reality from video',
  'https://replicate.delivery/...',
  'https://replicate.delivery/...',
  'sticker/job-id.mp4',
  10,
  'processing'
);
```

### VideoGlitch 테이블 (글리치 모드만)
```sql
-- 글리치 관계 기록
INSERT INTO video_glitches (
  original_video_id,
  glitch_video_id,
  glitch_type
) VALUES (
  'template-video-id',
  'new-video-id',
  'sticker_to_reality'
);

-- 원본 영상의 glitch_count 증가
UPDATE videos
SET glitch_count = glitch_count + 1
WHERE id = 'template-video-id';
```

### Glitch Type 종류
1. `animate` - WAN 2.2 Animate (이미지 → 영상)
2. `replace` - WAN 2.2 Replace (영상 → 영상)
3. **`sticker_to_reality`** - AI 자동 통합 (영상 + 이미지 → 영상) ⭐ NEW

---

## 🧪 테스트 케이스

### 1. 글리치 모드 - 정상 케이스
```bash
# 1. 크레딧 확인
curl -X GET http://localhost:8000/v1/credits/balance \
  -H "Authorization: Bearer {token}"
# → 100 credits

# 2. Sticker to Reality 생성 (글리치)
curl -X POST http://localhost:8000/v1/ai/sticker-to-reality \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "template-video-id",
    "user_image_url": "https://example.com/sticker.png",
    "start_time": 5.0,
    "end_time": 15.0,
    "prompt": "Make the sticker follow the person naturally",
    "is_glitch": true
  }'
# → Status: 200, Job created

# 3. 크레딧 차감 확인
curl -X GET http://localhost:8000/v1/credits/balance \
  -H "Authorization: Bearer {token}"
# → 55 credits (100 - 45)

# 4. 글리치 관계 확인
curl -X GET http://localhost:8000/v1/glitch/videos/{template-video-id}/glitches \
  -H "Authorization: Bearer {token}"
# → 새 글리치 포함
```

### 2. 편집 모드 - 정상 케이스
```bash
# 1. 내 영상 업로드
curl -X POST http://localhost:8000/v1/videos/upload \
  -H "Authorization: Bearer {token}" \
  -F "file=@my-video.mp4"
# → video_id: "my-video-id"

# 2. Sticker to Reality 적용 (편집)
curl -X POST http://localhost:8000/v1/ai/sticker-to-reality \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "my-video-id",
    "user_image_url": "https://example.com/sticker.png",
    "start_time": 0.0,
    "end_time": 10.0,
    "prompt": "Place the sticker in the center and rotate it",
    "is_glitch": false
  }'
# → Status: 200, Job created

# 3. 글리치 관계 없음 확인
curl -X GET http://localhost:8000/v1/glitch/videos/{my-video-id}/glitches \
  -H "Authorization: Bearer {token}"
# → 빈 배열 (글리치 아님)
```

### 3. 권한 오류 - 다른 사람 영상 편집 시도
```bash
curl -X POST http://localhost:8000/v1/ai/sticker-to-reality \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "others-video-id",
    "user_image_url": "https://example.com/sticker.png",
    "start_time": 0.0,
    "end_time": 10.0,
    "prompt": "...",
    "is_glitch": false
  }'
# → Status: 403 Forbidden
# → "You can only edit your own videos. Set is_glitch=True to glitch others' videos."
```

### 4. 크레딧 부족
```bash
# 크레딧: 20
curl -X POST http://localhost:8000/v1/ai/sticker-to-reality \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{...}'
# → Status: 402 Payment Required
# → "Insufficient credits. Required: 45, Available: 20"
```

### 5. 구간 초과 (> 10초)
```bash
curl -X POST http://localhost:8000/v1/ai/sticker-to-reality \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "...",
    "user_image_url": "...",
    "start_time": 0.0,
    "end_time": 15.0,
    "prompt": "...",
    "is_glitch": true
  }'
# → Status: 400 Bad Request
# → "Duration cannot exceed 10 seconds"
```

---

## 📈 최종 현황

### API 개수
**총 74개 API 엔드포인트** (64개 → 74개로 증가)

### AI 기능 API (7개)

1. ✅ `POST /v1/ai/capture-frame` - 프레임 캡처
2. ✅ `POST /v1/ai/template` - I2V 템플릿
3. ✅ `POST /v1/ai/glitch/animate` - 글리치 Animate
4. ✅ `POST /v1/ai/glitch/replace` - 글리치 Replace
5. ✅ **`POST /v1/ai/sticker-to-reality`** - AI 자동 통합 ⭐ NEW
6. ✅ `POST /v1/ai/music` - 음악 생성
7. ✅ `GET /v1/ai/jobs/{job_id}` - 작업 상태 조회

---

## 🎯 기획서 MVP 완성도

| 기능 | 상태 | 비고 |
|------|------|------|
| ✅ 크레딧 일일 무료 지급 | **완료** | 매일 10 크레딧 |
| ✅ AI 자동 통합 (Sticker to Reality) | **완료** ⭐ | 45 크레딧, 2가지 모드 |
| ⚠️ 글리치 추적 시스템 | 부분 완료 | 프로필 통합 필요 |

**MVP 핵심 기능 2/3 완료!**

---

## 🚀 다음 단계

### 남은 작업
1. ⚠️ **글리치 추적 시스템 완성**
   - 프로필 페이지에 글리치 통계 표시
   - 글리치 트리 시각화

### 선택적 개선
- 피드 알고리즘 (For You / Following)
- 신고/차단 시스템
- 관리자 대시보드

---

## 📝 변경 이력

### 2025-10-30
- ✅ Sticker to Reality API 구현
- ✅ 글리치/편집 모드 분리
- ✅ 소유권 검증 추가
- ✅ 크레딧 시스템 통합
- ✅ 서버 재시작 및 검증 완료

---

**작업자:** Manus AI  
**완료일:** 2025년 10월 30일  
**검증:** 통과 ✅  
**서버 상태:** 정상 작동 (74 API)

