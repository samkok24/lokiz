# LOKIZ 백엔드 누락 API 및 개선 사항 분석

**분석일:** 2025년 10월 29일

## 분석 방법

현재 코드베이스를 다음 관점에서 분석했습니다:
1. **사용자 경험**: 프론트엔드에서 필요할 것으로 예상되는 기능
2. **데이터 일관성**: 모델에 있지만 API가 없는 필드
3. **비즈니스 로직**: 크레딧 관리, 구독 시스템 등
4. **성능 최적화**: 피드 로딩, 캐싱, 배치 처리
5. **보안 및 관리**: 신고, 차단, 관리자 기능

---

## 1. 크리티컬 누락 API (즉시 구현 권장)

### 1.1. 조회수 증가 API ⚠️ **HIGH PRIORITY**

**문제**: `view_count` 필드는 Video 모델에 존재하지만, 증가시키는 로직이 전혀 없습니다.

**필요 API**:
```
POST /v1/videos/{video_id}/view
```

**구현 방안**:
- 비인증 사용자도 호출 가능
- IP 기반 중복 방지 (Redis 캐시, 24시간 TTL)
- 또는 세션 기반 중복 방지
- 본인 영상은 조회수 증가 안 함

**영향**: 조회수는 트렌딩, 추천 알고리즘의 핵심 지표입니다.

---

### 1.2. 사용자 프로필 수정 API ⚠️ **HIGH PRIORITY**

**문제**: 프로필 조회는 가능하지만, 수정 API가 없습니다.

**필요 API**:
```
PATCH /v1/users/me
```

**수정 가능 필드**:
- `display_name` (표시 이름)
- `bio` (자기소개)
- `profile_image_url` (프로필 이미지)

**구현 방안**:
- 본인만 수정 가능
- username, email은 변경 불가 (또는 별도 API)
- 프로필 이미지는 `/v1/images/upload-url` 사용 후 URL 업데이트

---

### 1.3. 비디오 업로드 완료 콜백 API ⚠️ **HIGH PRIORITY**

**문제**: 현재 `/upload-url`로 Presigned URL을 받지만, 업로드 완료 후 상태를 `processing` → `completed`로 변경하는 API가 없습니다.

**필요 API**:
```
POST /v1/videos/{video_id}/complete
```

**요청 바디**:
```json
{
  "width": 1080,
  "height": 1920,
  "actual_duration": 15.5
}
```

**구현 방안**:
- 업로드 완료 후 프론트엔드에서 호출
- 상태를 `completed`로 변경
- 실제 비디오 메타데이터 업데이트 (width, height, duration)

---

### 1.4. 크레딧 충전/구매 API ⚠️ **MEDIUM PRIORITY**

**문제**: 크레딧 소비는 구현되어 있지만, 충전 방법이 없습니다.

**필요 API**:
```
POST /v1/credits/purchase
GET /v1/credits/history
GET /v1/credits/balance
```

**구현 방안**:
- 결제 연동 (Stripe, Toss Payments 등)
- 크레딧 패키지 (100 크레딧 = $9.99 등)
- 크레딧 사용 내역 조회
- 현재 잔액 조회

---

## 2. 사용자 경험 개선 API

### 2.1. 피드 개인화 API

**현재 상태**: `/v1/videos/` 피드는 단순히 최신순 정렬입니다.

**개선 방안**:
```
GET /v1/videos/feed?algorithm=personalized
GET /v1/videos/feed?algorithm=trending
GET /v1/videos/feed?algorithm=following
```

**알고리즘 옵션**:
- `latest` (기본값): 최신순
- `trending`: 조회수, 좋아요 수 기반
- `personalized`: 사용자 관심사 기반 (팔로우, 좋아요 이력)
- `following`: 팔로우한 사용자의 영상만

---

### 2.2. 영상 신고 API

**필요 API**:
```
POST /v1/videos/{video_id}/report
GET /v1/reports/ (관리자 전용)
```

**신고 유형**:
- 부적절한 콘텐츠
- 스팸
- 저작권 침해
- 폭력적 콘텐츠
- 기타

---

### 2.3. 사용자 차단 API

**필요 API**:
```
POST /v1/blocks/users/{user_id}
DELETE /v1/blocks/users/{user_id}
GET /v1/blocks/
```

**기능**:
- 차단한 사용자의 영상이 피드에 표시되지 않음
- 차단한 사용자가 내 프로필/영상에 접근 불가
- 차단 목록 조회

---

### 2.4. 영상 저장 (북마크) API

**필요 API**:
```
POST /v1/bookmarks/videos/{video_id}
DELETE /v1/bookmarks/videos/{video_id}
GET /v1/bookmarks/
GET /v1/bookmarks/videos/{video_id}/check
```

**기능**:
- 나중에 볼 영상 저장
- 좋아요와 별개로 관리
- 프로필 페이지에 "저장한 영상" 탭 추가 가능

---

### 2.5. 영상 공유 API

**필요 API**:
```
POST /v1/videos/{video_id}/share
GET /v1/videos/{video_id}/share-count
```

**기능**:
- 공유 횟수 추적
- 공유 링크 생성 (딥링크)
- 공유 통계 (어디서 공유되었는지)

---

## 3. 비디오 편집 및 생성 개선

### 3.1. AI 작업 취소 API

**문제**: AI 작업이 시작되면 취소할 방법이 없습니다.

**필요 API**:
```
DELETE /v1/ai/jobs/{job_id}
```

**구현 방안**:
- 진행 중인 작업만 취소 가능
- Replicate API의 취소 기능 사용
- 크레딧은 환불 (아직 차감 전이므로)

---

### 3.2. 배치 프레임 캡처 API

**현재**: 한 번에 하나의 프레임만 캡처 가능

**개선 API**:
```
POST /v1/ai/capture-frames
```

**요청 바디**:
```json
{
  "video_id": "uuid",
  "timestamps": [1.0, 5.0, 10.0, 15.0]
}
```

**응답**:
```json
{
  "frames": [
    {"timestamp": 1.0, "image_url": "..."},
    {"timestamp": 5.0, "image_url": "..."}
  ]
}
```

---

### 3.3. 영상 편집 프리셋 API

**필요 API**:
```
GET /v1/presets/glitch
GET /v1/presets/music
```

**기능**:
- 인기 있는 글리치 스타일 목록
- 추천 음악 장르/스타일
- 프론트엔드에서 선택지 제공

---

### 3.4. 임시 저장 (Draft) API

**필요 API**:
```
POST /v1/videos/draft
GET /v1/videos/drafts
DELETE /v1/videos/drafts/{draft_id}
```

**기능**:
- AI 작업 중간 결과 임시 저장
- 나중에 이어서 편집
- 자동 저장 기능

---

## 4. 성능 및 최적화

### 4.1. 배치 좋아요 상태 확인 API

**현재**: `/v1/likes/videos/{video_id}/check`는 한 번에 하나씩만 확인 가능

**개선 API**:
```
POST /v1/likes/check-batch
```

**요청 바디**:
```json
{
  "video_ids": ["uuid1", "uuid2", "uuid3", ...]
}
```

**응답**:
```json
{
  "liked_videos": {
    "uuid1": true,
    "uuid2": false,
    "uuid3": true
  }
}
```

**영향**: 피드에서 20개 영상의 좋아요 상태를 확인할 때 1번의 요청으로 가능

---

### 4.2. 배치 팔로우 상태 확인 API

**현재**: `/v1/follows/users/{user_id}/check`는 한 번에 하나씩만 확인 가능

**개선 API**:
```
POST /v1/follows/check-batch
```

**요청 바디**:
```json
{
  "user_ids": ["uuid1", "uuid2", "uuid3", ...]
}
```

---

### 4.3. 피드 프리페치 API

**필요 API**:
```
GET /v1/videos/prefetch?cursor={cursor}&count=5
```

**기능**:
- 다음 페이지 미리 로드
- 무한 스크롤 성능 개선
- 낮은 우선순위로 백그라운드 로드

---

## 5. 구독 및 등급 시스템 (선택적)

### 5.1. 구독 플랜 API

**필요 API**:
```
GET /v1/subscriptions/plans
POST /v1/subscriptions/subscribe
GET /v1/subscriptions/me
DELETE /v1/subscriptions/cancel
```

**플랜 예시**:
- **Free**: 100 크레딧/월
- **Basic**: $9.99/월, 500 크레딧/월
- **Pro**: $29.99/월, 2000 크레딧/월, 우선 처리
- **Enterprise**: 맞춤형

---

### 5.2. 사용자 등급 시스템

**User 모델에 추가 필요**:
```python
subscription_tier = Column(String(20), default="free")  # free, basic, pro, enterprise
subscription_expires_at = Column(DateTime(timezone=True), nullable=True)
```

**권한 차별화**:
- Free: 기본 기능, 광고 표시
- Basic: 광고 제거, 크레딧 할인
- Pro: 우선 AI 처리, 고급 편집 기능
- Enterprise: API 접근, 무제한 크레딧

---

## 6. 관리자 기능

### 6.1. 관리자 대시보드 API

**필요 API**:
```
GET /v1/admin/stats
GET /v1/admin/users
GET /v1/admin/videos
GET /v1/admin/reports
PATCH /v1/admin/users/{user_id}/ban
PATCH /v1/admin/videos/{video_id}/remove
```

**통계**:
- 총 사용자 수
- 총 영상 수
- 일일 활성 사용자 (DAU)
- 크레딧 사용량
- AI 작업 성공률

---

## 7. 알림 개선

### 7.1. 실시간 알림 (WebSocket)

**필요 API**:
```
WS /v1/notifications/ws
```

**기능**:
- 실시간 알림 푸시
- 새 좋아요, 댓글, 팔로우 즉시 알림
- 프론트엔드에서 WebSocket 연결 유지

---

### 7.2. 알림 설정 API

**필요 API**:
```
GET /v1/notifications/settings
PATCH /v1/notifications/settings
```

**설정 옵션**:
- 좋아요 알림 on/off
- 댓글 알림 on/off
- 팔로우 알림 on/off
- 글리치 알림 on/off
- 이메일 알림 on/off

---

## 8. 검색 개선

### 8.1. 자동완성 API

**필요 API**:
```
GET /v1/search/autocomplete?q={query}
```

**응답**:
```json
{
  "suggestions": [
    {"type": "user", "text": "@username", "id": "uuid"},
    {"type": "hashtag", "text": "#trending", "count": 1234},
    {"type": "keyword", "text": "dance video"}
  ]
}
```

---

### 8.2. 검색 히스토리 API

**필요 API**:
```
GET /v1/search/history
POST /v1/search/history
DELETE /v1/search/history/{history_id}
DELETE /v1/search/history/clear
```

**기능**:
- 최근 검색어 저장
- 검색어 자동완성에 활용
- 개인화된 검색 결과

---

## 9. 분석 및 통계

### 9.1. 사용자 통계 API

**필요 API**:
```
GET /v1/users/me/stats
```

**응답**:
```json
{
  "total_videos": 42,
  "total_views": 12345,
  "total_likes": 678,
  "total_comments": 234,
  "total_followers": 56,
  "total_glitches_created": 23,
  "total_glitches_received": 89,
  "credits_used": 500,
  "credits_remaining": 100
}
```

---

### 9.2. 영상 통계 API

**필요 API**:
```
GET /v1/videos/{video_id}/stats
```

**응답**:
```json
{
  "views_by_day": [
    {"date": "2025-10-29", "views": 123},
    {"date": "2025-10-28", "views": 456}
  ],
  "likes_by_day": [...],
  "demographics": {
    "age_groups": {"18-24": 45, "25-34": 35, "35+": 20},
    "countries": {"US": 50, "KR": 30, "JP": 20}
  },
  "traffic_sources": {
    "feed": 60,
    "search": 20,
    "profile": 15,
    "external": 5
  }
}
```

---

## 우선순위 요약

### 🔴 즉시 구현 필요 (크리티컬)
1. ✅ **조회수 증가 API** - 트렌딩 알고리즘의 핵심
2. ✅ **사용자 프로필 수정 API** - 기본 기능
3. ✅ **비디오 업로드 완료 API** - 업로드 워크플로우 완성
4. ✅ **크레딧 충전 API** - 수익 모델

### 🟡 중요 (1-2주 내)
5. 피드 개인화 API
6. 배치 상태 확인 API (좋아요, 팔로우)
7. 영상 신고/차단 API
8. 북마크 API

### 🟢 선택적 (추후 개발)
9. 구독 시스템
10. 관리자 대시보드
11. 실시간 알림 (WebSocket)
12. 통계 및 분석 API

---

## 결론

현재 LOKIZ 백엔드는 **핵심 소셜 기능은 완성**되었지만, **사용자 경험과 수익화를 위한 API가 부족**합니다.

특히 **조회수 증가, 프로필 수정, 업로드 완료, 크레딧 충전** 4개 API는 프로덕션 배포 전에 반드시 구현되어야 합니다.

나머지 API들은 서비스 성장에 따라 단계적으로 추가할 수 있습니다.

