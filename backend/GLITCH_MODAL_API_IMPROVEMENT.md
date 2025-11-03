# 글리치 모달 API 개선 완료

**작업일:** 2025년 10월 30일  
**목적:** 틱톡 UI/UX와 동일한 그리드 뷰 구현을 위한 API 개선

---

## 🎯 개선 목표

### 틱톡 UI 분석

**세 가지 이미지 분석:**

1. **첫 번째 이미지** - "원음 - w" 사운드 페이지
   - 이 사운드를 사용한 영상들의 그리드 뷰
   - 썸네일, 사용자 프로필, 조회수 표시

2. **두 번째 이미지** - "#출계" 해시태그 페이지
   - 이 해시태그를 사용한 영상들의 그리드 뷰
   - 썸네일, 사용자 프로필, 조회수 표시

3. **세 번째 이미지** - 피드 영상
   - 우측 하단에 좋아요/글리치/공유 카운팅 인디케이터
   - 글리치 버튼 클릭 → 글리치 모달

### 요구사항

**글리치 버튼 클릭 시:**
- 해당 영상을 템플릿으로 사용한 다른 글리치 영상들을 그리드 형태로 표시
- 틱톡의 "원음" 기능과 동일한 UX

**해시태그 클릭 시:**
- 해당 해시태그를 사용한 영상들을 그리드 형태로 표시

---

## ✅ 구현 완료

### 1. 해시태그 API (이미 완벽하게 구현됨)

**엔드포인트:**
```
GET /v1/hashtags/{hashtag_name}/videos
```

**응답 형식:**
```json
{
  "hashtag": {
    "id": "uuid",
    "name": "출계",
    "use_count": 17000,
    "created_at": "2025-10-30T..."
  },
  "videos": [
    {
      "id": "uuid",
      "user": {
        "id": "uuid",
        "username": "peach.com099",
        "profile_image": "https://..."
      },
      "video_url": "https://...",
      "thumbnail_url": "https://...",
      "duration_seconds": 15,
      "caption": "다들 트위터 남들한테 보여...",
      "view_count": 125000,
      "like_count": 10300,
      "comment_count": 41,
      "glitch_count": 2809,
      "original_video_id": null,
      "created_at": "2025-10-30T..."
    }
  ],
  "total": 17000
}
```

**특징:**
- ✅ 썸네일 (thumbnail_url)
- ✅ 사용자 정보 (username, profile_image)
- ✅ 통계 (view_count, like_count, comment_count, glitch_count)
- ✅ 영상 길이 (duration_seconds)
- ✅ 그리드 뷰에 필요한 모든 정보 제공

---

### 2. 글리치 API (개선 완료) ⭐

**엔드포인트:**
```
GET /v1/glitch/videos/{video_id}/glitches
```

**개선 전 (기본 정보만):**
```json
{
  "original_video_id": "uuid",
  "glitch_count": 28,
  "glitches": [
    {
      "id": "glitch-uuid",
      "glitch_video_id": "video-uuid",
      "glitch_type": "animate",
      "created_at": "2025-10-30T...",
      "video": {
        "id": "video-uuid",
        "title": "My Glitch",
        "url": "https://...",
        "user_id": "user-uuid",
        "created_at": "2025-10-30T..."
      }
    }
  ]
}
```

**개선 후 (VideoResponse 형식):**
```json
{
  "original_video_id": "uuid",
  "glitch_count": 28,
  "glitches": [
    {
      "id": "uuid",
      "user": {
        "id": "uuid",
        "username": "kks_5985",
        "profile_image": "https://..."
      },
      "video_url": "https://...",
      "thumbnail_url": "https://...",
      "duration_seconds": 10,
      "caption": "p-2 이슈🔥didi🔥",
      "view_count": 45000,
      "like_count": 3200,
      "comment_count": 156,
      "glitch_count": 12,
      "original_video_id": "template-video-uuid",
      "created_at": "2025-10-30T..."
    }
  ]
}
```

**개선 사항:**
- ✅ **썸네일 추가** (thumbnail_url)
- ✅ **사용자 정보 추가** (username, profile_image)
- ✅ **통계 추가** (view_count, like_count, comment_count, glitch_count)
- ✅ **영상 길이 추가** (duration_seconds)
- ✅ **해시태그 API와 동일한 형식**

---

## 📊 API 비교

### 해시태그 API vs 글리치 API

| 항목 | 해시태그 API | 글리치 API (개선 전) | 글리치 API (개선 후) |
|------|-------------|-------------------|-------------------|
| 썸네일 | ✅ | ❌ | ✅ |
| 사용자 정보 | ✅ | ❌ | ✅ |
| 조회수 | ✅ | ❌ | ✅ |
| 좋아요 수 | ✅ | ❌ | ✅ |
| 댓글 수 | ✅ | ❌ | ✅ |
| 글리치 수 | ✅ | ❌ | ✅ |
| 영상 길이 | ✅ | ❌ | ✅ |
| 그리드 뷰 지원 | ✅ | ❌ | ✅ |

**결과:** 두 API가 동일한 형식으로 통일됨! ✅

---

## 🎨 프론트엔드 통합 가이드

### 1. 글리치 모달 (피드에서 글리치 버튼 클릭)

**워크플로우:**

```javascript
// 1. 피드 영상 우측 하단의 글리치 버튼 클릭
const handleGlitchButtonClick = async (videoId) => {
  // 2. 글리치 목록 API 호출
  const response = await fetch(`/v1/glitch/videos/${videoId}/glitches?sort=popular`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  
  // 3. 모달 표시 (PC는 페이지, 모바일은 모달)
  showGlitchModal({
    originalVideoId: data.original_video_id,
    glitchCount: data.glitch_count,
    videos: data.glitches  // VideoResponse[] 형식
  });
};

// 4. 그리드 뷰 렌더링
const renderGlitchGrid = (videos) => {
  return videos.map(video => (
    <VideoGridItem
      key={video.id}
      thumbnail={video.thumbnail_url}
      username={video.user.username}
      profileImage={video.user.profile_image}
      viewCount={video.view_count}
      likeCount={video.like_count}
      glitchCount={video.glitch_count}
      duration={video.duration_seconds}
      onClick={() => playVideo(video.id)}
    />
  ));
};
```

---

### 2. 해시태그 모달 (캡션의 해시태그 클릭)

**워크플로우:**

```javascript
// 1. 캡션의 해시태그 클릭
const handleHashtagClick = async (hashtagName) => {
  // 2. 해시태그 영상 목록 API 호출
  const response = await fetch(`/v1/hashtags/${hashtagName}/videos?limit=50`);
  
  const data = await response.json();
  
  // 3. 모달 표시 (PC는 페이지, 모바일은 모달)
  showHashtagModal({
    hashtag: data.hashtag,
    videos: data.videos  // VideoResponse[] 형식
  });
};

// 4. 그리드 뷰 렌더링 (글리치와 동일한 컴포넌트 사용)
const renderHashtagGrid = (videos) => {
  return videos.map(video => (
    <VideoGridItem
      key={video.id}
      thumbnail={video.thumbnail_url}
      username={video.user.username}
      profileImage={video.user.profile_image}
      viewCount={video.view_count}
      likeCount={video.like_count}
      glitchCount={video.glitch_count}
      duration={video.duration_seconds}
      onClick={() => playVideo(video.id)}
    />
  ));
};
```

---

### 3. 공통 그리드 아이템 컴포넌트

**React 예시:**

```jsx
const VideoGridItem = ({
  thumbnail,
  username,
  profileImage,
  viewCount,
  likeCount,
  glitchCount,
  duration,
  onClick
}) => {
  return (
    <div className="video-grid-item" onClick={onClick}>
      {/* 썸네일 */}
      <div className="thumbnail-container">
        <img src={thumbnail} alt="Video thumbnail" />
        
        {/* 영상 길이 */}
        <div className="duration-badge">
          {formatDuration(duration)}
        </div>
      </div>
      
      {/* 사용자 정보 */}
      <div className="user-info">
        <img src={profileImage} alt={username} className="profile-image" />
        <span className="username">{username}</span>
      </div>
      
      {/* 통계 */}
      <div className="stats">
        <span className="view-count">
          <EyeIcon /> {formatCount(viewCount)}
        </span>
        <span className="like-count">
          <HeartIcon /> {formatCount(likeCount)}
        </span>
        <span className="glitch-count">
          <GlitchIcon /> {formatCount(glitchCount)}
        </span>
      </div>
    </div>
  );
};

// 숫자 포맷팅 (10.1K, 2.8M 등)
const formatCount = (count) => {
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(1)}M`;
  } else if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}K`;
  }
  return count.toString();
};

// 시간 포맷팅 (00:15, 01:23 등)
const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};
```

---

## 🔧 API 파라미터

### 글리치 목록 API

**엔드포인트:**
```
GET /v1/glitch/videos/{video_id}/glitches
```

**파라미터:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `video_id` | UUID | ✅ | - | 원본 영상 ID |
| `sort` | string | ❌ | `latest` | 정렬 방식 (`latest`, `popular`) |

**정렬 옵션:**
- `latest` - 최신순 (created_at desc)
- `popular` - 인기순 (like_count desc)

**인증:**
- ✅ 필수 (Bearer token)

**예시:**
```bash
# 최신순
curl -X GET "http://localhost:8000/v1/glitch/videos/{video_id}/glitches?sort=latest" \
  -H "Authorization: Bearer {token}"

# 인기순
curl -X GET "http://localhost:8000/v1/glitch/videos/{video_id}/glitches?sort=popular" \
  -H "Authorization: Bearer {token}"
```

---

### 해시태그 영상 목록 API

**엔드포인트:**
```
GET /v1/hashtags/{hashtag_name}/videos
```

**파라미터:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `hashtag_name` | string | ✅ | - | 해시태그 이름 (# 제외) |
| `limit` | int | ❌ | `20` | 최대 결과 개수 (1-100) |

**정렬:**
- 최신순 (created_at desc) 고정

**인증:**
- ❌ 불필요 (공개 API)

**예시:**
```bash
curl -X GET "http://localhost:8000/v1/hashtags/출계/videos?limit=50"
```

---

## 📱 UI/UX 가이드

### 그리드 레이아웃

**틱톡 스타일:**
```
┌─────────┬─────────┬─────────┐
│ Video 1 │ Video 2 │ Video 3 │
│ [thumb] │ [thumb] │ [thumb] │
│ @user1  │ @user2  │ @user3  │
│ 👁 10K  │ 👁 25K  │ 👁 5K   │
├─────────┼─────────┼─────────┤
│ Video 4 │ Video 5 │ Video 6 │
│ [thumb] │ [thumb] │ [thumb] │
│ @user4  │ @user5  │ @user6  │
│ 👁 15K  │ 👁 30K  │ 👁 8K   │
└─────────┴─────────┴─────────┘
```

**CSS 예시:**
```css
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  padding: 16px;
}

.video-grid-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.video-grid-item:hover {
  transform: scale(1.05);
}

.thumbnail-container {
  position: relative;
  aspect-ratio: 9 / 16;
  overflow: hidden;
  border-radius: 8px;
}

.thumbnail-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.duration-badge {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.profile-image {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.username {
  font-size: 14px;
  font-weight: 500;
}

.stats {
  display: flex;
  gap: 12px;
  margin-top: 4px;
  font-size: 12px;
  color: #666;
}
```

---

## 🧪 테스트 시나리오

### 1. 글리치 모달 테스트

```bash
# 1. 테스트 영상 업로드
VIDEO_ID="550e8400-e29b-41d4-a716-446655440000"

# 2. 글리치 목록 조회 (최신순)
curl -X GET "http://localhost:8000/v1/glitch/videos/${VIDEO_ID}/glitches?sort=latest" \
  -H "Authorization: Bearer ${TOKEN}" \
  | jq '.glitches[] | {id, thumbnail_url, username: .user.username, view_count, glitch_count}'

# 3. 글리치 목록 조회 (인기순)
curl -X GET "http://localhost:8000/v1/glitch/videos/${VIDEO_ID}/glitches?sort=popular" \
  -H "Authorization: Bearer ${TOKEN}" \
  | jq '.glitches[] | {id, thumbnail_url, username: .user.username, like_count, glitch_count}'
```

### 2. 해시태그 모달 테스트

```bash
# 1. 해시태그 영상 목록 조회
curl -X GET "http://localhost:8000/v1/hashtags/출계/videos?limit=20" \
  | jq '.videos[] | {id, thumbnail_url, username: .user.username, view_count, glitch_count}'

# 2. 트렌딩 해시태그 조회
curl -X GET "http://localhost:8000/v1/hashtags/trending?limit=10" \
  | jq '.hashtags[] | {name, use_count}'
```

---

## 📈 성능 최적화

### 현재 구현

**N+1 쿼리 문제:**
```python
# 각 글리치마다 개별 쿼리 실행
for glitch in glitches:
    glitch_video = db.query(Video).filter(...).first()  # Query 1
    user = db.query(User).filter(...).first()  # Query 2
    video_glitch_count = db.query(VideoGlitch).filter(...).count()  # Query 3
```

**개선 방안 (향후):**
```python
# Eager loading으로 한 번에 조회
glitches = db.query(VideoGlitch).filter(
    VideoGlitch.original_video_id == video_id
).join(
    Video, VideoGlitch.glitch_video_id == Video.id
).join(
    User, Video.user_id == User.id
).options(
    joinedload(VideoGlitch.glitch_video),
    joinedload(VideoGlitch.glitch_video.user)
).all()
```

**예상 성능 개선:**
- 현재: O(n) 쿼리 (n = 글리치 개수)
- 개선 후: O(1) 쿼리 (단일 JOIN 쿼리)

---

## 🎯 완성도

### 기능 완성도

| 기능 | 상태 | 비고 |
|------|------|------|
| ✅ 글리치 목록 API | **완료** | VideoResponse 형식 |
| ✅ 해시태그 영상 목록 API | **완료** | VideoResponse 형식 |
| ✅ 썸네일 제공 | **완료** | thumbnail_url |
| ✅ 사용자 정보 제공 | **완료** | username, profile_image |
| ✅ 통계 제공 | **완료** | view/like/comment/glitch count |
| ✅ 정렬 옵션 | **완료** | latest, popular |
| ⚠️ 페이지네이션 | 부분 완료 | limit만 지원 |
| ⚠️ 성능 최적화 | 부분 완료 | N+1 쿼리 개선 필요 |

---

## 🚀 다음 단계

### 선택적 개선 사항

1. **페이지네이션 추가**
   - 커서 기반 무한 스크롤
   - `cursor` 파라미터 추가

2. **성능 최적화**
   - Eager loading으로 N+1 쿼리 해결
   - Redis 캐싱 추가

3. **필터 옵션 추가**
   - 기간별 필터 (오늘, 이번 주, 이번 달)
   - 글리치 타입별 필터 (animate, replace, sticker_to_reality)

4. **배치 API 추가**
   - 여러 영상의 글리치 목록을 한 번에 조회
   - 피드 최적화

---

**작업자:** Manus AI  
**완료일:** 2025년 10월 30일  
**검증:** 통과 ✅  
**서버 상태:** 정상 작동 (74 API)

