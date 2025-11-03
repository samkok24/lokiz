# 추가 배치 API 설계

## 필요한 배치 API (3개 추가)

### 1. 영상 메타데이터 배치 조회 API

**문제:**
- 피드에서 20개 영상을 보여줄 때, 각 영상의 조회수, 좋아요 수, 댓글 수가 필요
- 현재는 개별 영상 조회 API를 20번 호출해야 함
- 또는 피드 API에 모든 정보가 포함되어 있지만, 실시간 업데이트가 안 됨

**해결:**
```
POST /v1/videos/batch-metadata
```

**요청:**
```json
{
  "video_ids": ["uuid1", "uuid2", "uuid3", ...]
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
    "uuid2": { ... }
  }
}
```

**사용 시나리오:**
- 피드 스크롤 시 주기적으로 카운터 업데이트 (5초마다)
- 영상 상세 페이지에서 실시간 통계 갱신
- 트렌딩 페이지에서 조회수 기반 정렬

---

### 2. AI 작업 상태 배치 조회 API

**문제:**
- 사용자가 여러 개의 AI 작업을 동시에 요청할 수 있음
- 각 작업의 진행 상태를 개별적으로 확인하면 비효율적
- 스튜디오 페이지에서 진행 중인 모든 작업을 표시해야 함

**해결:**
```
POST /v1/ai/jobs/batch-status
```

**요청:**
```json
{
  "job_ids": ["uuid1", "uuid2", "uuid3", ...]
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
      "result_url": "https://...",
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

**사용 시나리오:**
- 스튜디오 페이지에서 진행 중인 모든 작업 표시
- 2초마다 폴링하여 진행률 업데이트
- 작업 완료 시 자동으로 결과 표시

---

### 3. 알림 배치 조회 API

**문제:**
- 현재 `/v1/notifications/` API는 페이지네이션만 지원
- 특정 알림들의 읽음 상태를 확인하거나 업데이트하려면 개별 요청 필요
- 알림 목록을 표시할 때 모든 알림의 상태를 한 번에 가져와야 함

**해결:**
```
POST /v1/notifications/batch-mark-read
```

**요청:**
```json
{
  "notification_ids": ["uuid1", "uuid2", "uuid3", ...]
}
```

**응답:**
```json
{
  "marked_count": 3,
  "success": true
}
```

**사용 시나리오:**
- 알림 드롭다운을 열었을 때 표시된 알림들을 모두 읽음 처리
- 알림 페이지에서 "모두 읽음" 버튼 클릭 시
- 특정 카테고리의 알림들만 선택적으로 읽음 처리

---

## 구현 우선순위

### 🔴 High Priority
1. **AI 작업 상태 배치 조회** - 사용자 경험에 직접적인 영향
2. **영상 메타데이터 배치 조회** - 실시간 통계 업데이트

### 🟡 Medium Priority
3. **알림 배치 읽음 처리** - 편의성 개선

---

## 추가 고려사항

### 4. 영상 배치 삭제 API (관리자용)

**문제:**
- 관리자가 부적절한 영상을 대량으로 삭제해야 할 때
- 신고된 영상들을 한 번에 처리해야 할 때

**해결:**
```
POST /v1/admin/videos/batch-delete
```

**요청:**
```json
{
  "video_ids": ["uuid1", "uuid2", "uuid3", ...],
  "reason": "Inappropriate content"
}
```

---

### 5. 사용자 배치 차단 API

**문제:**
- 스팸 계정들을 한 번에 차단해야 할 때
- 특정 사용자 그룹을 차단해야 할 때

**해결:**
```
POST /v1/blocks/batch
```

**요청:**
```json
{
  "user_ids": ["uuid1", "uuid2", "uuid3", ...]
}
```

---

## 성능 최적화 전략

### 폴링 vs WebSocket

**폴링 (현재 방식):**
- 장점: 구현 간단, 서버 부하 예측 가능
- 단점: 실시간성 떨어짐, 불필요한 요청 발생

**WebSocket (향후 개선):**
- 장점: 실시간 업데이트, 서버 푸시 가능
- 단점: 구현 복잡, 연결 관리 필요

**권장:**
- AI 작업 상태: 폴링 (2초 간격) → 향후 WebSocket
- 영상 메타데이터: 폴링 (5초 간격)
- 알림: WebSocket (실시간 푸시)

---

## 프론트엔드 통합 예시

### AI 작업 상태 모니터링

```typescript
class AIJobMonitor {
  private jobIds: Set<string> = new Set();
  private pollingInterval: NodeJS.Timeout | null = null;

  addJob(jobId: string) {
    this.jobIds.add(jobId);
    if (!this.pollingInterval) {
      this.startPolling();
    }
  }

  removeJob(jobId: string) {
    this.jobIds.delete(jobId);
    if (this.jobIds.size === 0) {
      this.stopPolling();
    }
  }

  private startPolling() {
    this.pollingInterval = setInterval(async () => {
      if (this.jobIds.size === 0) return;

      const response = await fetch('/v1/ai/jobs/batch-status', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          job_ids: Array.from(this.jobIds)
        })
      });

      const { jobs } = await response.json();

      for (const [jobId, status] of Object.entries(jobs)) {
        if (status.status === 'completed' || status.status === 'failed') {
          this.removeJob(jobId);
          this.onJobComplete(jobId, status);
        } else {
          this.onJobProgress(jobId, status);
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

  private onJobProgress(jobId: string, status: any) {
    // UI 업데이트: 진행률 표시
    console.log(`Job ${jobId}: ${status.progress}%`);
  }

  private onJobComplete(jobId: string, status: any) {
    // UI 업데이트: 완료/실패 처리
    if (status.status === 'completed') {
      console.log(`Job ${jobId} completed: ${status.result_url}`);
    } else {
      console.error(`Job ${jobId} failed: ${status.error}`);
    }
  }
}

// 사용 예시
const monitor = new AIJobMonitor();

// AI 작업 시작
const job = await startAIJob(...);
monitor.addJob(job.job_id);
```

### 영상 메타데이터 실시간 업데이트

```typescript
class VideoMetadataUpdater {
  private videoIds: Set<string> = new Set();
  private updateInterval: NodeJS.Timeout | null = null;

  trackVideos(videos: Video[]) {
    videos.forEach(v => this.videoIds.add(v.id));
    if (!this.updateInterval) {
      this.startUpdating();
    }
  }

  private startUpdating() {
    this.updateInterval = setInterval(async () => {
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
      for (const [videoId, metadata] of Object.entries(videos)) {
        this.updateVideoUI(videoId, metadata);
      }
    }, 5000); // 5초마다 업데이트
  }

  private updateVideoUI(videoId: string, metadata: any) {
    // DOM 업데이트
    document.querySelector(`[data-video-id="${videoId}"] .view-count`)
      .textContent = metadata.view_count;
    document.querySelector(`[data-video-id="${videoId}"] .like-count`)
      .textContent = metadata.like_count;
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
const updater = new VideoMetadataUpdater();

// 피드 로드 시
const videos = await loadFeed();
updater.trackVideos(videos);

// 페이지 이탈 시
window.addEventListener('beforeunload', () => {
  updater.stopTracking();
});
```

---

## 요약

### 추가 구현 필요한 배치 API (3개)

1. **영상 메타데이터 배치 조회** (`POST /v1/videos/batch-metadata`)
   - 조회수, 좋아요 수, 댓글 수 등 실시간 통계
   - 5초 간격 폴링

2. **AI 작업 상태 배치 조회** (`POST /v1/ai/jobs/batch-status`)
   - 진행 중인 여러 작업의 상태 확인
   - 2초 간격 폴링

3. **알림 배치 읽음 처리** (`POST /v1/notifications/batch-mark-read`)
   - 여러 알림을 한 번에 읽음 처리
   - 사용자 편의성 개선

### 선택적 배치 API (2개)

4. **영상 배치 삭제** (관리자용)
5. **사용자 배치 차단**

### 구현 순서

1. AI 작업 상태 배치 조회 (가장 중요)
2. 영상 메타데이터 배치 조회
3. 알림 배치 읽음 처리

