# 배치 상태 확인 API 설계

## 배치 API란?

배치 API는 **여러 개의 항목에 대한 상태를 한 번의 요청으로 확인**하는 API입니다.

### 문제 상황 (Before)

피드에서 20개의 영상을 보여줄 때:
```typescript
// ❌ 나쁜 방법: 20번의 개별 요청
for (const video of videos) {
  const likeStatus = await fetch(`/v1/likes/videos/${video.id}/check`);
  const followStatus = await fetch(`/v1/follows/users/${video.user.id}/check`);
}
// 총 40번의 API 요청! (20개 영상 × 2개 상태)
```

### 해결 방법 (After)

```typescript
// ✅ 좋은 방법: 2번의 배치 요청
const videoIds = videos.map(v => v.id);
const userIds = videos.map(v => v.user.id);

const likeStatuses = await fetch('/v1/likes/check-batch', {
  method: 'POST',
  body: JSON.stringify({ video_ids: videoIds })
});

const followStatuses = await fetch('/v1/follows/check-batch', {
  method: 'POST',
  body: JSON.stringify({ user_ids: userIds })
});
// 총 2번의 API 요청!
```

---

## 구현할 배치 API (2개)

### 1. 좋아요 배치 확인 API

**Endpoint:**
```
POST /v1/likes/check-batch
```

**요청 바디:**
```json
{
  "video_ids": [
    "uuid1",
    "uuid2",
    "uuid3",
    ...
  ]
}
```

**응답:**
```json
{
  "liked_videos": {
    "uuid1": true,
    "uuid2": false,
    "uuid3": true,
    ...
  }
}
```

**동작 방식:**
1. 요청에서 video_ids 배열을 받음
2. 현재 로그인한 사용자의 좋아요 목록을 조회
3. 각 video_id에 대해 좋아요 여부를 확인
4. 딕셔너리 형태로 반환

**SQL 쿼리:**
```sql
SELECT video_id 
FROM likes 
WHERE user_id = :current_user_id 
  AND video_id IN (:video_ids)
```

**성능:**
- 단일 쿼리로 모든 상태 확인
- IN 절을 사용하여 효율적으로 처리
- 최대 100개까지 한 번에 확인 가능

---

### 2. 팔로우 배치 확인 API

**Endpoint:**
```
POST /v1/follows/check-batch
```

**요청 바디:**
```json
{
  "user_ids": [
    "uuid1",
    "uuid2",
    "uuid3",
    ...
  ]
}
```

**응답:**
```json
{
  "following_users": {
    "uuid1": true,
    "uuid2": false,
    "uuid3": true,
    ...
  }
}
```

**동작 방식:**
1. 요청에서 user_ids 배열을 받음
2. 현재 로그인한 사용자의 팔로잉 목록을 조회
3. 각 user_id에 대해 팔로우 여부를 확인
4. 딕셔너리 형태로 반환

**SQL 쿼리:**
```sql
SELECT following_id 
FROM follows 
WHERE follower_id = :current_user_id 
  AND following_id IN (:user_ids)
```

---

## 사용 시나리오

### 시나리오 1: 피드 로딩

**상황:** 사용자가 피드를 스크롤하여 20개의 영상을 로드

**필요한 정보:**
- 각 영상에 대한 좋아요 여부 (하트 아이콘 표시)
- 각 영상 작성자에 대한 팔로우 여부 (팔로우 버튼 표시)

**프론트엔드 코드:**
```typescript
async function loadFeed(cursor?: string) {
  // 1. 피드 데이터 가져오기
  const feedResponse = await fetch(`/v1/videos/?cursor=${cursor || ''}`);
  const { videos } = await feedResponse.json();
  
  // 2. video_ids와 user_ids 추출
  const videoIds = videos.map(v => v.id);
  const userIds = [...new Set(videos.map(v => v.user.id))]; // 중복 제거
  
  // 3. 배치로 상태 확인
  const [likeStatuses, followStatuses] = await Promise.all([
    fetch('/v1/likes/check-batch', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ video_ids: videoIds })
    }).then(r => r.json()),
    
    fetch('/v1/follows/check-batch', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_ids: userIds })
    }).then(r => r.json())
  ]);
  
  // 4. 상태 정보를 영상 데이터에 병합
  const videosWithStatus = videos.map(video => ({
    ...video,
    is_liked: likeStatuses.liked_videos[video.id] || false,
    is_following: followStatuses.following_users[video.user.id] || false
  }));
  
  return videosWithStatus;
}
```

**성능 비교:**
- **Before**: 40번의 API 요청 (20개 영상 × 2개 상태)
- **After**: 3번의 API 요청 (피드 1번 + 배치 2번)
- **개선**: 약 93% 요청 감소

---

### 시나리오 2: 검색 결과

**상황:** 사용자가 "dance"를 검색하여 30개의 영상 결과

**필요한 정보:**
- 각 영상에 대한 좋아요 여부

**프론트엔드 코드:**
```typescript
async function searchVideos(query: string) {
  // 1. 검색 결과 가져오기
  const searchResponse = await fetch(`/v1/search/videos?q=${query}`);
  const { videos } = await searchResponse.json();
  
  // 2. 배치로 좋아요 상태 확인
  const videoIds = videos.map(v => v.id);
  const likeStatuses = await fetch('/v1/likes/check-batch', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ video_ids: videoIds })
  }).then(r => r.json());
  
  // 3. 상태 정보 병합
  return videos.map(video => ({
    ...video,
    is_liked: likeStatuses.liked_videos[video.id] || false
  }));
}
```

---

### 시나리오 3: 프로필 페이지

**상황:** 다른 사용자의 프로필 페이지에서 영상 목록 확인

**필요한 정보:**
- 각 영상에 대한 좋아요 여부
- 프로필 주인에 대한 팔로우 여부

**프론트엔드 코드:**
```typescript
async function loadUserProfile(userId: string) {
  // 1. 프로필 정보 및 영상 목록 가져오기
  const [profile, videos] = await Promise.all([
    fetch(`/v1/users/${userId}`).then(r => r.json()),
    fetch(`/v1/users/${userId}/videos`).then(r => r.json())
  ]);
  
  // 2. 배치로 상태 확인
  const videoIds = videos.videos.map(v => v.id);
  const [likeStatuses, followStatus] = await Promise.all([
    fetch('/v1/likes/check-batch', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_ids: videoIds })
    }).then(r => r.json()),
    
    fetch('/v1/follows/check-batch', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_ids: [userId] })
    }).then(r => r.json())
  ]);
  
  return {
    profile: {
      ...profile,
      is_following: followStatus.following_users[userId] || false
    },
    videos: videos.videos.map(video => ({
      ...video,
      is_liked: likeStatuses.liked_videos[video.id] || false
    }))
  };
}
```

---

## 제한 사항

### 1. 최대 배치 크기
- **최대 100개**까지 한 번에 확인 가능
- 100개 초과 시 400 Bad Request 반환
- 이유: 데이터베이스 쿼리 성능 및 응답 크기 제한

### 2. 인증 필수
- 두 API 모두 로그인 필수
- 비로그인 사용자는 개별 확인 API 사용 불가 (모두 false로 간주)

### 3. 존재하지 않는 ID 처리
- 요청한 ID가 존재하지 않아도 에러 발생 안 함
- 단순히 `false`로 반환
- 예: 삭제된 영상의 좋아요 상태 → `false`

---

## 성능 최적화

### 데이터베이스 인덱스
```sql
-- likes 테이블
CREATE INDEX idx_likes_user_video ON likes(user_id, video_id);

-- follows 테이블
CREATE INDEX idx_follows_follower_following ON follows(follower_id, following_id);
```

### 캐싱 (선택적)
Redis를 사용하여 자주 조회되는 상태를 캐싱할 수 있습니다:
```python
# 예시: 좋아요 상태 캐싱
cache_key = f"user:{user_id}:liked_videos"
cached_likes = redis.smembers(cache_key)  # Set 자료구조

if cached_likes:
    # 캐시에서 확인
    result = {vid: vid in cached_likes for vid in video_ids}
else:
    # DB에서 조회 후 캐싱
    likes = db.query(Like).filter(...).all()
    redis.sadd(cache_key, *[like.video_id for like in likes])
    redis.expire(cache_key, 3600)  # 1시간 TTL
```

---

## 요약

### 배치 API 개수: **2개**
1. 좋아요 배치 확인 (`POST /v1/likes/check-batch`)
2. 팔로우 배치 확인 (`POST /v1/follows/check-batch`)

### 주요 특징
- 한 번에 최대 100개 항목 확인
- 단일 SQL 쿼리로 효율적 처리
- 피드 로딩 시 API 요청 93% 감소
- 인증 필수

### 사용 시점
- 피드 로딩 (무한 스크롤)
- 검색 결과 표시
- 프로필 페이지 영상 목록
- 해시태그 페이지 영상 목록
- 트렌딩 페이지

### 성능 개선
- **Before**: N개 영상 → N번 요청
- **After**: N개 영상 → 1번 요청
- **개선율**: (N-1)/N × 100%
  - 20개: 95% 감소
  - 50개: 98% 감소
  - 100개: 99% 감소

