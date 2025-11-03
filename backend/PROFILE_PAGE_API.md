# 프로필 페이지 API 문서

## 개요

프로필 페이지에서 사용하는 3개의 API 엔드포인트를 제공합니다:
1. **사용자 프로필 정보** - 팔로워/팔로잉/영상 수, 총 좋아요 수 등 통계
2. **사용자 영상 목록** - 무한 스크롤 지원 (격자 탭 1)
3. **좋아요한 영상 목록** - 무한 스크롤 지원 (격자 탭 2)

## 1. 사용자 프로필 정보

### Endpoint
```
GET /v1/users/{user_id}
```

### 인증
- 불필요 (Public API)

### 응답 예시
```json
{
  "id": "9718982a-3de5-4b56-949c-92844e09928a",
  "username": "admin",
  "display_name": "Admin User",
  "bio": null,
  "profile_image_url": null,
  "follower_count": 0,
  "following_count": 0,
  "video_count": 0,
  "total_likes": 0,
  "created_at": "2025-10-29T09:35:42.123456Z"
}
```

## 2. 사용자 영상 목록 (격자 탭 1)

### Endpoint
```
GET /v1/users/{user_id}/videos
```

### 인증
- 선택적 (Optional)
- 본인이 아닌 경우: 공개된 완료 영상만 표시
- 본인인 경우: 모든 영상 표시 (비공개, 처리 중 포함)

### Query Parameters
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `page_size` | integer | 아니오 | 20 | 한 페이지당 영상 수 (1-100) |
| `cursor` | string | 아니오 | null | 다음 페이지를 위한 커서 (이전 응답의 `next_cursor` 사용) |

### 응답 예시
```json
{
  "videos": [
    {
      "id": "86c16e64-45b1-43b7-9aa8-881ac2beb240",
      "user": {
        "id": "0238e512-ec05-4ad6-9c8b-3405153d49e1",
        "username": "video_tester",
        "display_name": "video_tester",
        "profile_image_url": null
      },
      "video_url": "https://mock-s3.lokiz.dev/videos/example.mp4",
      "thumbnail_url": "https://mock-s3.lokiz.dev/thumbnails/example.jpg",
      "duration_seconds": 30,
      "caption": "My first video!",
      "view_count": 100,
      "like_count": 15,
      "comment_count": 3,
      "remix_count": 2,
      "glitch_count": 5,
      "original_video_id": null,
      "created_at": "2025-10-29T05:22:22.447074Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "has_more": false,
  "next_cursor": null
}
```

### 무한 스크롤 구현 예시 (JavaScript)
```javascript
let cursor = null;
let loading = false;

async function loadMoreVideos(userId) {
  if (loading) return;
  
  loading = true;
  
  const url = new URL(`/v1/users/${userId}/videos`, window.location.origin);
  if (cursor) {
    url.searchParams.set('cursor', cursor);
  }
  url.searchParams.set('page_size', '20');
  
  const response = await fetch(url);
  const data = await response.json();
  
  // 영상 격자에 추가
  appendVideosToGrid(data.videos);
  
  // 다음 커서 저장
  cursor = data.next_cursor;
  loading = false;
  
  // 더 이상 데이터가 없으면 스크롤 이벤트 제거
  if (!data.has_more) {
    removeScrollListener();
  }
}

// 스크롤 이벤트
window.addEventListener('scroll', () => {
  if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
    loadMoreVideos(currentUserId);
  }
});
```

## 3. 좋아요한 영상 목록 (격자 탭 2)

### Endpoint
```
GET /v1/users/{user_id}/liked-videos
```

### 인증
- 선택적 (Optional)
- 공개된 완료 영상만 표시 (본인/타인 구분 없음)

### Query Parameters
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `page_size` | integer | 아니오 | 20 | 한 페이지당 영상 수 (1-100) |
| `cursor` | string | 아니오 | null | 다음 페이지를 위한 커서 (이전 응답의 `next_cursor` 사용) |

### 응답 예시
```json
{
  "videos": [
    {
      "id": "f3a2b1c0-1234-5678-90ab-cdef12345678",
      "user": {
        "id": "a1b2c3d4-5678-90ab-cdef-123456789012",
        "username": "other_user",
        "display_name": "Other User",
        "profile_image_url": "https://example.com/profile.jpg"
      },
      "video_url": "https://mock-s3.lokiz.dev/videos/liked.mp4",
      "thumbnail_url": "https://mock-s3.lokiz.dev/thumbnails/liked.jpg",
      "duration_seconds": 15,
      "caption": "Amazing video! #trending",
      "view_count": 5000,
      "like_count": 250,
      "comment_count": 30,
      "remix_count": 10,
      "glitch_count": 20,
      "original_video_id": null,
      "created_at": "2025-10-28T10:00:00.000000Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "has_more": false,
  "next_cursor": null
}
```

### 특징
- 영상은 **좋아요를 누른 시간 순서**로 정렬됩니다 (최신순)
- 삭제되었거나 비공개 처리된 영상은 표시되지 않습니다

## 프론트엔드 구현 가이드

### React 예시 (무한 스크롤)

```typescript
import { useState, useEffect } from 'react';
import { useInView } from 'react-intersection-observer';

interface Video {
  id: string;
  user: {
    id: string;
    username: string;
    display_name: string;
    profile_image_url: string | null;
  };
  video_url: string;
  thumbnail_url: string;
  duration_seconds: number;
  caption: string | null;
  view_count: number;
  like_count: number;
  comment_count: number;
  remix_count: number;
  glitch_count: number;
  created_at: string;
}

interface VideoListResponse {
  videos: Video[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
  next_cursor: string | null;
}

export function UserVideosTab({ userId }: { userId: string }) {
  const [videos, setVideos] = useState<Video[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  
  const { ref, inView } = useInView({
    threshold: 0,
  });

  const loadVideos = async () => {
    if (loading || !hasMore) return;
    
    setLoading(true);
    
    const url = new URL(`/v1/users/${userId}/videos`, window.location.origin);
    if (cursor) {
      url.searchParams.set('cursor', cursor);
    }
    
    const response = await fetch(url);
    const data: VideoListResponse = await response.json();
    
    setVideos(prev => [...prev, ...data.videos]);
    setCursor(data.next_cursor);
    setHasMore(data.has_more);
    setLoading(false);
  };

  useEffect(() => {
    loadVideos();
  }, []);

  useEffect(() => {
    if (inView && hasMore) {
      loadVideos();
    }
  }, [inView]);

  return (
    <div className="grid grid-cols-3 gap-1">
      {videos.map(video => (
        <VideoThumbnail key={video.id} video={video} />
      ))}
      
      {hasMore && <div ref={ref} className="col-span-3 h-20" />}
      
      {loading && <LoadingSpinner />}
    </div>
  );
}
```

## 주의사항

1. **커서 기반 페이지네이션**: `next_cursor`를 다음 요청의 `cursor` 파라미터로 전달해야 합니다.
2. **has_more 확인**: `has_more`가 `false`일 때 추가 요청을 중단해야 합니다.
3. **인증 토큰**: 본인 프로필에서 비공개 영상을 보려면 Authorization 헤더에 Bearer 토큰을 포함해야 합니다.
4. **성능 최적화**: `page_size`를 너무 크게 설정하면 응답 시간이 길어질 수 있습니다 (권장: 20-50).

## 전체 API 엔드포인트 수

현재 LOKIZ 백엔드는 **41개의 API 엔드포인트**를 제공합니다.

