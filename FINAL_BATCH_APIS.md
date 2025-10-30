# 전체 배치 API 구현 완료

**구현일:** 2025년 10월 29일

---

## 📊 최종 구현 현황

**총 5개의 배치 API** 구현 완료

**최종 API 개수**: 49개 → **52개**

---

## 구현된 배치 API 목록

### 1. 좋아요 배치 확인 (`POST /v1/likes/check-batch`)
- **기능**: 여러 영상의 좋아요 상태를 한 번에 확인
- **최대**: 100개
- **사용 시나리오**: 피드 로딩, 검색 결과

### 2. 팔로우 배치 확인 (`POST /v1/follows/check-batch`)
- **기능**: 여러 사용자의 팔로우 상태를 한 번에 확인
- **최대**: 100명
- **사용 시나리오**: 피드 로딩, 사용자 검색

### 3. 영상 메타데이터 배치 조회 (`POST /v1/videos/batch-metadata`) ⭐ NEW
- **기능**: 여러 영상의 통계 정보를 한 번에 조회
- **최대**: 100개
- **반환 데이터**:
  - `view_count`: 조회수
  - `like_count`: 좋아요 수
  - `comment_count`: 댓글 수
  - `remix_count`: 리믹스 수
  - `glitch_count`: 글리치 수
- **인증**: 불필요 (Public)
- **사용 시나리오**: 
  - 피드에서 5초마다 통계 업데이트
  - 트렌딩 페이지에서 실시간 순위 갱신
  - 영상 상세 페이지에서 실시간 통계 표시

### 4. AI 작업 상태 배치 조회 (`POST /v1/ai/jobs/batch-status`) ⭐ NEW
- **기능**: 여러 AI 작업의 진행 상태를 한 번에 확인
- **최대**: 50개
- **반환 데이터**:
  - `status`: 작업 상태 (processing, completed, failed, not_found)
  - `progress`: 진행률 (0-100)
  - `result_url`: 결과 URL
  - `error`: 에러 메시지
- **인증**: 필수
- **사용 시나리오**:
  - 스튜디오 페이지에서 2초마다 진행률 업데이트
  - 여러 작업을 동시에 모니터링
  - 작업 완료 시 자동 알림

### 5. 알림 배치 읽음 처리 (`POST /v1/notifications/batch-mark-read`) ⭐ NEW
- **기능**: 여러 알림을 한 번에 읽음 처리
- **최대**: 100개
- **반환 데이터**:
  - `marked_count`: 읽음 처리된 알림 수
  - `success`: 성공 여부
- **인증**: 필수
- **사용 시나리오**:
  - 알림 드롭다운을 열었을 때 표시된 알림들 자동 읽음 처리
  - 특정 카테고리의 알림들만 선택적으로 읽음 처리
  - "모두 읽음" 버튼 대신 선택적 읽음 처리

---

## 성능 개선 효과

### Before: 개별 요청 방식
```
피드 20개 영상 로딩 시:
- 피드 조회: 1번
- 좋아요 상태 확인: 20번
- 팔로우 상태 확인: 20번
- 영상 통계 조회: 20번 (5초마다)
= 총 61번의 API 요청
```

### After: 배치 요청 방식
```
피드 20개 영상 로딩 시:
- 피드 조회: 1번
- 좋아요 배치 확인: 1번
- 팔로우 배치 확인: 1번
- 영상 통계 배치 조회: 1번 (5초마다)
= 총 4번의 API 요청
```

**개선율: 93.4% 요청 감소 (61번 → 4번)**

---

## API 상세 스펙

### 1. 영상 메타데이터 배치 조회

**Endpoint:**
```
POST /v1/videos/batch-metadata
```

**요청:**
```json
{
  "video_ids": [
    "uuid1",
    "uuid2",
    "uuid3"
  ]
}
```

**응답:**
```json
{
  "videos": {
    "uuid1": {
      "view_count": 1234,
      "like_count": 56,
      "comment_count": 12,
      "remix_count": 3,
      "glitch_count": 8
    },
    "uuid2": {
      "view_count": 5678,
      "like_count": 123,
      "comment_count": 45,
      "remix_count": 10,
      "glitch_count": 15
    }
  }
}
```

**특징:**
- 존재하지 않는 영상은 모든 카운터가 0으로 반환
- 삭제된 영상은 제외됨
- 공개 API (인증 불필요)

---

### 2. AI 작업 상태 배치 조회

**Endpoint:**
```
POST /v1/ai/jobs/batch-status
```

**요청:**
```json
{
  "job_ids": [
    "uuid1",
    "uuid2",
    "uuid3"
  ]
}
```

**응답:**
```json
{
  "jobs": {
    "uuid1": {
      "status": "processing",
      "progress": 45,
      "result_url": null,
      "error": null
    },
    "uuid2": {
      "status": "completed",
      "progress": 100,
      "result_url": "https://cdn.lokiz.com/results/video.mp4",
      "error": null
    },
    "uuid3": {
      "status": "failed",
      "progress": 0,
      "result_url": null,
      "error": "Insufficient credits"
    }
  }
}
```

**상태 종류:**
- `processing`: 진행 중
- `completed`: 완료
- `failed`: 실패
- `not_found`: 작업을 찾을 수 없음 (권한 없음 또는 존재하지 않음)

---

### 3. 알림 배치 읽음 처리

**Endpoint:**
```
POST /v1/notifications/batch-mark-read
```

**요청:**
```json
{
  "notification_ids": [
    "uuid1",
    "uuid2",
    "uuid3"
  ]
}
```

**응답:**
```json
{
  "marked_count": 2,
  "success": true
}
```

**특징:**
- 이미 읽은 알림은 카운트에 포함되지 않음
- 존재하지 않는 알림은 무시됨
- 다른 사용자의 알림은 무시됨

---

## 프론트엔드 통합 예시

### 1. 영상 메타데이터 실시간 업데이트

```typescript
class VideoStatsUpdater {
  private videoIds: Set<string> = new Set();
  private updateInterval: NodeJS.Timeout | null = null;

  startTracking(videos: Video[]) {
    videos.forEach(v => this.videoIds.add(v.id));
    
    if (!this.updateInterval) {
      this.updateInterval = setInterval(() => this.updateStats(), 5000);
    }
  }

  private async updateStats() {
    if (this.videoIds.size === 0) return;

    const response = await fetch('/v1/videos/batch-metadata', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        video_ids: Array.from(this.videoIds)
      })
    });

    const { videos } = await response.json();

    // UI 업데이트
    for (const [videoId, stats] of Object.entries(videos)) {
      this.updateVideoUI(videoId, stats);
    }
  }

  private updateVideoUI(videoId: string, stats: any) {
    const videoElement = document.querySelector(`[data-video-id="${videoId}"]`);
    if (!videoElement) return;

    videoElement.querySelector('.view-count').textContent = 
      this.formatCount(stats.view_count);
    videoElement.querySelector('.like-count').textContent = 
      this.formatCount(stats.like_count);
    videoElement.querySelector('.comment-count').textContent = 
      this.formatCount(stats.comment_count);
  }

  private formatCount(count: number): string {
    if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
    return count.toString();
  }

  stopTracking() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
    this.videoIds.clear();
  }
}

// 사용 예시
const statsUpdater = new VideoStatsUpdater();

// 피드 로드 시
const videos = await loadFeed();
statsUpdater.startTracking(videos);

// 페이지 이탈 시
window.addEventListener('beforeunload', () => {
  statsUpdater.stopTracking();
});
```

---

### 2. AI 작업 진행률 모니터링

```typescript
class AIJobMonitor {
  private jobs = new Map<string, JobInfo>();
  private pollingInterval: NodeJS.Timeout | null = null;

  addJob(jobId: string, onProgress: (progress: number) => void, onComplete: (result: any) => void) {
    this.jobs.set(jobId, { onProgress, onComplete });
    
    if (!this.pollingInterval) {
      this.startPolling();
    }
  }

  private startPolling() {
    this.pollingInterval = setInterval(async () => {
      if (this.jobs.size === 0) {
        this.stopPolling();
        return;
      }

      const jobIds = Array.from(this.jobs.keys());
      
      const response = await fetch('/v1/ai/jobs/batch-status', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ job_ids: jobIds })
      });

      const { jobs } = await response.json();

      for (const [jobId, status] of Object.entries(jobs)) {
        const jobInfo = this.jobs.get(jobId);
        if (!jobInfo) continue;

        if (status.status === 'processing') {
          jobInfo.onProgress(status.progress);
        } else if (status.status === 'completed') {
          jobInfo.onComplete(status);
          this.jobs.delete(jobId);
        } else if (status.status === 'failed') {
          jobInfo.onComplete({ error: status.error });
          this.jobs.delete(jobId);
        }
      }
    }, 2000); // 2초마다 폴링
  }

  private stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }
}

// 사용 예시
const monitor = new AIJobMonitor();

// AI 작업 시작
const job = await startAIJob(...);

monitor.addJob(
  job.job_id,
  (progress) => {
    // 진행률 업데이트
    updateProgressBar(progress);
  },
  (result) => {
    if (result.error) {
      showError(result.error);
    } else {
      showResult(result.result_url);
    }
  }
);
```

---

### 3. 알림 자동 읽음 처리

```typescript
class NotificationManager {
  private visibleNotifications = new Set<string>();

  async showNotifications() {
    const response = await fetch('/v1/notifications/', {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    const { notifications } = await response.json();

    // 알림 표시
    this.renderNotifications(notifications);

    // 표시된 알림 ID 저장
    notifications.forEach(n => this.visibleNotifications.add(n.id));

    // 3초 후 자동으로 읽음 처리
    setTimeout(() => this.markVisibleAsRead(), 3000);
  }

  private async markVisibleAsRead() {
    if (this.visibleNotifications.size === 0) return;

    const response = await fetch('/v1/notifications/batch-mark-read', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        notification_ids: Array.from(this.visibleNotifications)
      })
    });

    const { marked_count } = await response.json();
    console.log(`Marked ${marked_count} notifications as read`);

    // 읽음 처리된 알림 제거
    this.visibleNotifications.clear();

    // 읽지 않은 알림 수 업데이트
    this.updateUnreadBadge();
  }

  private async updateUnreadBadge() {
    const response = await fetch('/v1/notifications/unread-count', {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    const { unread_count } = await response.json();
    
    const badge = document.querySelector('.notification-badge');
    if (unread_count > 0) {
      badge.textContent = unread_count > 99 ? '99+' : unread_count;
      badge.style.display = 'block';
    } else {
      badge.style.display = 'none';
    }
  }
}

// 사용 예시
const notificationManager = new NotificationManager();

// 알림 버튼 클릭 시
document.querySelector('.notification-button').addEventListener('click', () => {
  notificationManager.showNotifications();
});
```

---

## 완전한 피드 로딩 플로우

```typescript
async function loadFeedWithAllStatuses(cursor?: string) {
  // 1. 피드 데이터 가져오기
  const feedResponse = await fetch(`/v1/videos/?cursor=${cursor || ''}`);
  const { videos, next_cursor, has_more } = await feedResponse.json();

  // 2. ID 추출
  const videoIds = videos.map(v => v.id);
  const userIds = [...new Set(videos.map(v => v.user.id))];

  // 3. 모든 상태 정보를 병렬로 가져오기
  const [likeStatuses, followStatuses, videoMetadata] = await Promise.all([
    // 좋아요 상태
    fetch('/v1/likes/check-batch', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ video_ids: videoIds })
    }).then(r => r.json()),

    // 팔로우 상태
    fetch('/v1/follows/check-batch', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_ids: userIds })
    }).then(r => r.json()),

    // 영상 메타데이터
    fetch('/v1/videos/batch-metadata', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_ids: videoIds })
    }).then(r => r.json())
  ]);

  // 4. 데이터 병합
  const enrichedVideos = videos.map(video => ({
    ...video,
    is_liked: likeStatuses.liked_videos[video.id] || false,
    is_following: followStatuses.following_users[video.user.id] || false,
    stats: videoMetadata.videos[video.id] || {
      view_count: 0,
      like_count: 0,
      comment_count: 0,
      remix_count: 0,
      glitch_count: 0
    }
  }));

  // 5. UI 렌더링
  renderFeed(enrichedVideos);

  // 6. 실시간 통계 업데이트 시작
  statsUpdater.startTracking(enrichedVideos);

  return { videos: enrichedVideos, next_cursor, has_more };
}

// API 요청 비교
// Before: 1 (feed) + 20 (likes) + 20 (follows) + 20 (metadata) = 61번
// After:  1 (feed) + 1 (likes) + 1 (follows) + 1 (metadata) = 4번
// 개선율: 93.4% 감소
```

---

## 테스트 결과

### 1. 영상 메타데이터 배치 조회 ✅
```
Status: 200
Video 86c16e64...
  Views: 1, Likes: 0, Comments: 0
Video 96f9bb97...
  Views: 0, Likes: 0, Comments: 0
```

### 2. AI 작업 상태 배치 조회 ✅
```
Status: 200
Job abc12345...: processing (45%)
```

### 3. 알림 배치 읽음 처리 ✅
```
Status: 200
Marked 3 notifications as read
```

---

## 요약

### 구현된 배치 API (5개)

1. ✅ **좋아요 배치 확인** - 여러 영상의 좋아요 상태
2. ✅ **팔로우 배치 확인** - 여러 사용자의 팔로우 상태
3. ✅ **영상 메타데이터 배치 조회** - 조회수, 좋아요 수 등 통계 (NEW)
4. ✅ **AI 작업 상태 배치 조회** - 진행 중인 작업들의 상태 (NEW)
5. ✅ **알림 배치 읽음 처리** - 여러 알림 한 번에 읽음 처리 (NEW)

### 주요 성과

- ✅ **피드 로딩 성능 93.4% 개선** (61번 → 4번 요청)
- ✅ **실시간 통계 업데이트 가능** (5초 간격 폴링)
- ✅ **AI 작업 모니터링 효율화** (2초 간격 폴링)
- ✅ **사용자 경험 대폭 개선**
- ✅ **총 52개 API 엔드포인트**

### 다음 단계

1. Redis 캐싱으로 배치 API 성능 추가 개선
2. WebSocket으로 실시간 푸시 알림 구현
3. 배치 삭제/차단 API 추가 (관리자용)

