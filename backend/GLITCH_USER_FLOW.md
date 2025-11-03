# LOKIZ 글리치 완전 유저 플로우

**작성일**: 2025년 10월 29일

---

## 📱 전체 유저 플로우

### 시나리오 A: 내 영상 프레임으로 글리치 만들기

```
[피드 화면]
  ↓ 스크롤
[마음에 드는 영상 발견]
  ↓ "글리치" 버튼 클릭
[글리치 모드 선택 화면]
  ↓ "내 영상 사용" 선택
[내 영상 목록 화면]
  ↓ 영상 선택
[프레임 선택 화면 (타임라인)]
  ↓ 원하는 프레임 선택
[글리치 타입 선택]
  ↓ Animate or Replace 선택
[AI 생성 중...]
  ↓ 완료
[결과 확인 화면]
  ↓ 피드에 업로드
[피드 화면]
```

### 시나리오 B: 이미지 업로드로 글리치 만들기

```
[피드 화면]
  ↓ 스크롤
[마음에 드는 영상 발견]
  ↓ "글리치" 버튼 클릭
[글리치 모드 선택 화면]
  ↓ "이미지 업로드" 선택
[이미지 선택 화면]
  ↓ 갤러리에서 이미지 선택
[글리치 타입 선택]
  ↓ Animate or Replace 선택
[AI 생성 중...]
  ↓ 완료
[결과 확인 화면]
  ↓ 피드에 업로드
[피드 화면]
```

---

## 🔧 필요한 API 및 구현 상태

### 1단계: 피드 화면
**화면**: 비디오 목록 (무한 스크롤)

**API**:
```
GET /v1/videos/?page_size=20&cursor={cursor}
```

**응답**:
```json
{
  "videos": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "video_url": "https://...",
      "thumbnail_url": "https://...",
      "duration_seconds": 30,
      "caption": "멋진 댄스 영상",
      "view_count": 1000,
      "like_count": 100,
      "comment_count": 20,
      "remix_count": 5
    }
  ],
  "has_more": true,
  "next_cursor": "2025-10-29T..."
}
```

**상태**: ✅ 구현 완료

---

### 2단계: 글리치 버튼 클릭
**화면**: 글리치 모드 선택 모달

**프론트엔드 상태 저장**:
```javascript
// 템플릿 비디오 ID를 로컬 상태에 저장
const [templateVideoId, setTemplateVideoId] = useState(null);

const handleGlitchClick = (videoId) => {
  setTemplateVideoId(videoId);
  navigate('/glitch/select-mode');
};
```

**필요한 API**: ❌ 없음 (프론트엔드 상태 관리)

**상태**: ✅ 프론트엔드 구현 필요

---

### 3A단계: 내 영상 목록 (시나리오 A)
**화면**: 내가 업로드한 영상 목록

**API**:
```
GET /v1/videos/me
```

**응답**:
```json
{
  "videos": [
    {
      "id": "uuid",
      "video_url": "https://...",
      "thumbnail_url": "https://...",
      "duration_seconds": 15,
      "created_at": "2025-10-29T..."
    }
  ]
}
```

**상태**: ❌ **구현 필요** (새로운 엔드포인트)

---

### 3B단계: 이미지 업로드 (시나리오 B)
**화면**: 이미지 업로드 화면

**API**:
```
POST /v1/images/upload-url
```

**요청**:
```json
{
  "file_type": "image/jpeg"
}
```

**응답**:
```json
{
  "upload_url": "https://mock-s3.../upload/...",
  "file_url": "https://mock-s3.../images/..."
}
```

**상태**: ❌ **구현 필요** (새로운 엔드포인트)

---

### 4A단계: 프레임 선택 (시나리오 A)
**화면**: 비디오 타임라인 + 프레임 미리보기

**API 1**: 타임라인 정보
```
GET /v1/studio/videos/{video_id}/timeline
```

**상태**: ✅ 구현 완료

**API 2**: 프레임 미리보기
```
GET /v1/studio/videos/{video_id}/preview?timestamp=5.5
```

**상태**: ✅ 구현 완료

**API 3**: 프레임 캡처
```
POST /v1/ai/capture-frame
```

**요청**:
```json
{
  "video_id": "uuid",
  "timestamp": 5.5
}
```

**응답**:
```json
{
  "image_url": "https://mock-s3.../frames/...",
  "timestamp": 5.5,
  "video_id": "uuid"
}
```

**상태**: ✅ 구현 완료

---

### 5단계: 글리치 타입 선택
**화면**: Animate vs Replace 선택

**프론트엔드 상태**:
```javascript
const [glitchType, setGlitchType] = useState(null); // 'animate' or 'replace'
const [userImageUrl, setUserImageUrl] = useState(null); // 3A 또는 3B에서 얻은 이미지 URL
```

**필요한 API**: ❌ 없음 (프론트엔드 상태 관리)

**상태**: ✅ 프론트엔드 구현 필요

---

### 6단계: AI 생성
**화면**: 로딩 화면

**API**:
```
POST /v1/ai/glitch/animate
또는
POST /v1/ai/glitch/replace
```

**요청**:
```json
{
  "template_video_id": "uuid",  // 1단계에서 선택한 영상
  "user_image_url": "https://...",  // 3A 또는 3B에서 얻은 이미지
  "prompt": "Apply dance motion"  // 선택적
}
```

**응답**:
```json
{
  "id": "job-uuid",
  "status": "completed",
  "output_data": {
    "video_url": "https://...",
    "model": "wan-video/wan-2.2-animate-animation",
    "video_id": "new-video-uuid"
  },
  "credits_used": 30
}
```

**상태**: ✅ 구현 완료

---

### 7단계: 결과 확인
**화면**: 생성된 글리치 비디오 재생

**API**: 6단계 응답에서 `video_id` 사용
```
GET /v1/videos/{video_id}
```

**응답**:
```json
{
  "id": "new-video-uuid",
  "video_url": "https://...",
  "status": "processing",  // 또는 "completed"
  ...
}
```

**상태**: ✅ 구현 완료

---

### 8단계: 피드에 업로드
**화면**: 캡션 입력 후 업로드

**API**:
```
PATCH /v1/videos/{video_id}
```

**요청**:
```json
{
  "caption": "내가 만든 멋진 글리치!",
  "duration": 5.0
}
```

**상태**: ✅ 구현 완료

---

## ❌ 누락된 API (2개)

### 1. 내 영상 목록 조회
**엔드포인트**: `GET /v1/videos/me`

**설명**: 현재 사용자가 업로드한 영상 목록

**필요성**: 시나리오 A에서 필수

**우선순위**: 🔴 High

---

### 2. 이미지 업로드 URL 생성
**엔드포인트**: `POST /v1/images/upload-url`

**설명**: 이미지 업로드를 위한 presigned URL 생성

**필요성**: 시나리오 B에서 필수

**우선순위**: 🔴 High

---

## 🎯 프론트엔드 상태 관리

### 글리치 생성 Context
```javascript
const GlitchContext = createContext();

const GlitchProvider = ({ children }) => {
  const [glitchState, setGlitchState] = useState({
    templateVideoId: null,      // 1단계에서 선택
    mode: null,                  // 'my-video' or 'upload-image'
    userImageUrl: null,          // 3A 또는 3B에서 얻음
    glitchType: null,            // 'animate' or 'replace'
    resultVideoId: null,         // 6단계에서 얻음
  });

  return (
    <GlitchContext.Provider value={{ glitchState, setGlitchState }}>
      {children}
    </GlitchContext.Provider>
  );
};
```

---

## 🔄 완전한 API 호출 시퀀스

### 시나리오 A: 내 영상 프레임 사용

```javascript
// 1. 피드에서 템플릿 영상 선택
const templateVideo = await fetch('/v1/videos/?page_size=20');

// 2. 글리치 버튼 클릭 (로컬 상태 저장)
setGlitchState({ templateVideoId: video.id });

// 3. 내 영상 목록 조회
const myVideos = await fetch('/v1/videos/me');

// 4. 내 영상 선택 후 타임라인 조회
const timeline = await fetch(`/v1/studio/videos/${myVideoId}/timeline`);

// 5. 프레임 미리보기
const preview = await fetch(`/v1/studio/videos/${myVideoId}/preview?timestamp=5.5`);

// 6. 프레임 캡처
const frame = await fetch('/v1/ai/capture-frame', {
  method: 'POST',
  body: JSON.stringify({
    video_id: myVideoId,
    timestamp: 5.5
  })
});

// 7. 글리치 타입 선택 (로컬 상태)
setGlitchState({ glitchType: 'animate' });

// 8. AI 생성
const job = await fetch('/v1/ai/glitch/animate', {
  method: 'POST',
  body: JSON.stringify({
    template_video_id: templateVideoId,
    user_image_url: frame.image_url
  })
});

// 9. 결과 확인
const resultVideo = await fetch(`/v1/videos/${job.output_data.video_id}`);

// 10. 캡션 추가 후 완료
await fetch(`/v1/videos/${resultVideo.id}`, {
  method: 'PATCH',
  body: JSON.stringify({
    caption: '내가 만든 글리치!'
  })
});
```

---

### 시나리오 B: 이미지 업로드 사용

```javascript
// 1-2. 동일

// 3. 이미지 업로드 URL 생성
const uploadUrl = await fetch('/v1/images/upload-url', {
  method: 'POST',
  body: JSON.stringify({
    file_type: 'image/jpeg'
  })
});

// 4. 이미지 업로드
await fetch(uploadUrl.upload_url, {
  method: 'PUT',
  body: imageFile
});

// 5. 이미지 URL 저장
setGlitchState({ userImageUrl: uploadUrl.file_url });

// 6-10. 시나리오 A와 동일
```

---

## 📊 구현 상태 요약

| 단계 | API | 상태 | 우선순위 |
|------|-----|------|----------|
| 1. 피드 조회 | `GET /v1/videos/` | ✅ 완료 | - |
| 2. 글리치 버튼 | (프론트엔드) | ⚠️ 미구현 | Medium |
| 3A. 내 영상 목록 | `GET /v1/videos/me` | ❌ 누락 | 🔴 High |
| 3B. 이미지 업로드 | `POST /v1/images/upload-url` | ❌ 누락 | 🔴 High |
| 4. 타임라인 조회 | `GET /v1/studio/videos/{id}/timeline` | ✅ 완료 | - |
| 4. 프레임 미리보기 | `GET /v1/studio/videos/{id}/preview` | ✅ 완료 | - |
| 4. 프레임 캡처 | `POST /v1/ai/capture-frame` | ✅ 완료 | - |
| 5. 타입 선택 | (프론트엔드) | ⚠️ 미구현 | Medium |
| 6. AI 생성 | `POST /v1/ai/glitch/{type}` | ✅ 완료 | - |
| 7. 결과 확인 | `GET /v1/videos/{id}` | ✅ 완료 | - |
| 8. 캡션 추가 | `PATCH /v1/videos/{id}` | ✅ 완료 | - |

---

## 🚀 다음 작업

### 즉시 구현 필요 (2개)
1. ✅ `GET /v1/videos/me` - 내 영상 목록 조회
2. ✅ `POST /v1/images/upload-url` - 이미지 업로드 URL 생성

### 프론트엔드 구현 필요
1. 글리치 Context/State 관리
2. 글리치 모드 선택 화면
3. 프레임 선택 타임라인 UI
4. 글리치 타입 선택 UI
5. AI 생성 로딩 화면

---

## 💡 추가 개선 아이디어

### 1. 글리치 미리보기
- AI 생성 전 간단한 미리보기 제공
- 크레딧 소모 전 확인 가능

### 2. 글리치 템플릿 추천
- 인기 있는 템플릿 영상 큐레이션
- "이 영상으로 만든 글리치 100개" 표시

### 3. 빠른 글리치
- 최근 사용한 내 이미지 저장
- 원클릭 글리치 생성

### 4. 글리치 체인 시각화
- 원본 → 글리치 → 글리치의 글리치
- 트리 구조로 표시

---

## ✅ 결론

**현재 상태**:
- 핵심 AI API는 모두 구현 완료
- 누락된 API 2개 발견
- 프론트엔드 구현 필요

**다음 단계**:
1. 누락된 API 2개 구현
2. 프론트엔드 개발 시작
3. 통합 테스트

**예상 작업 시간**:
- 백엔드 API 2개: 30분
- 프론트엔드 구현: 2-3일

