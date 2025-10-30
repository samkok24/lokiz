# LOKIZ 글리치 체인 시스템 설계

**작성일**: 2025년 10월 29일  
**참고**: TikTok 음악 시스템

---

## 🎵 TikTok 음악 시스템 분석

### TikTok의 음악 사용 방식

```
[음악 A] (원본)
  ↓
[영상 1] - 음악 A 사용
[영상 2] - 음악 A 사용
[영상 3] - 음악 A 사용
...
[영상 1000] - 음악 A 사용
```

### 핵심 특징

1. **하나의 음악을 여러 영상이 사용**
   - 음악은 "템플릿" 역할
   - 각 영상은 독립적

2. **음악 페이지**
   - "이 음악을 사용한 영상 1000개"
   - 인기순/최신순 정렬
   - 음악 정보 표시

3. **영상에서 음악 정보 표시**
   - 하단에 음악 제목/아티스트
   - 클릭하면 음악 페이지로 이동
   - "이 음악 사용하기" 버튼

4. **체인 구조**
   - 평면 구조 (트리가 아님)
   - 음악 → 영상들 (1:N 관계)
   - 영상끼리는 연결 없음

---

## 🎨 LOKIZ 글리치 체인 설계

### 기본 개념

**TikTok 음악 = LOKIZ 템플릿 영상**

```
[템플릿 영상 A] (원본)
  ↓
[글리치 영상 1] - 템플릿 A 사용
[글리치 영상 2] - 템플릿 A 사용
[글리치 영상 3] - 템플릿 A 사용
...
[글리치 영상 100] - 템플릿 A 사용
```

---

## 📊 데이터 구조

### 현재 DB 스키마 (이미 구현됨)

```sql
CREATE TABLE video_glitches (
    id UUID PRIMARY KEY,
    original_video_id UUID REFERENCES videos(id),  -- 템플릿 영상
    glitch_video_id UUID REFERENCES videos(id),    -- 글리치 영상
    glitch_type VARCHAR(50),                       -- 'animate' or 'replace'
    created_at TIMESTAMP
);
```

**관계**:
- `original_video_id`: 템플릿으로 사용된 영상
- `glitch_video_id`: 생성된 글리치 영상
- 1:N 관계 (하나의 템플릿 → 여러 글리치)

---

## 🔄 글리치 체인 규칙

### 규칙 1: 모든 영상은 템플릿이 될 수 있다

```
영상 A (일반 업로드)
  ↓ User 2가 글리치
글리치 영상 B
  ↓ User 3이 B를 템플릿으로 또 글리치
글리치 영상 C
  ↓ User 4가 C를 템플릿으로 또 글리치
글리치 영상 D
```

**결과**:
- A의 글리치: B
- B의 글리치: C
- C의 글리치: D

**체인 깊이**: 무제한 (TikTok처럼)

---

### 규칙 2: 평면 구조 (각 영상별로 독립)

**영상 A의 글리치 페이지**:
```
템플릿 영상: A
글리치 개수: 1개
- 글리치 영상 B (by User 2)
```

**영상 B의 글리치 페이지**:
```
템플릿 영상: B
글리치 개수: 1개
- 글리치 영상 C (by User 3)

원본 템플릿: A (by User 1)
```

**영상 C의 글리치 페이지**:
```
템플릿 영상: C
글리치 개수: 1개
- 글리치 영상 D (by User 4)

원본 템플릿: B (by User 2)
```

---

### 규칙 3: 루트 템플릿 추적 (선택적)

**옵션 A**: 직접 템플릿만 표시
```
글리치 영상 D
  ↓ 정보
템플릿: C
```

**옵션 B**: 전체 체인 표시
```
글리치 영상 D
  ↓ 정보
템플릿: C
  ← 템플릿: B
    ← 템플릿: A (원조)
```

**제안**: 옵션 A (TikTok 방식)
- 단순하고 명확
- 필요시 "원본 보기" 버튼으로 체인 탐색

---

## 🎯 피드 UI/UX

### 영상 카드 디자인

```
┌─────────────────────────┐
│                         │
│   [영상 재생 영역]        │
│                         │
├─────────────────────────┤
│ @username               │
│ 캡션 텍스트...           │
│                         │
│ 🎨 글리치 from @원본유저  │ ← 새로 추가
│    "원본 영상 제목"       │
│    👉 이 영상으로 글리치 42개 │
│                         │
│ ❤️ 1.2K  💬 45  ↗️ 12   │
└─────────────────────────┘
```

### 글리치 정보 표시 조건

1. **일반 업로드 영상**
   ```
   @username
   캡션 텍스트...
   
   👉 이 영상으로 글리치 5개
   ```

2. **글리치 영상**
   ```
   @username
   캡션 텍스트...
   
   🎨 글리치 from @원본유저
      "원본 영상 제목"
   
   👉 이 영상으로 글리치 2개
   ```

---

## 🔧 필요한 API 수정

### 1. 비디오 응답 스키마 확장

**현재**:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "video_url": "https://...",
  "caption": "캡션",
  "like_count": 100,
  "comment_count": 20,
  "remix_count": 5
}
```

**수정 후**:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "video_url": "https://...",
  "caption": "캡션",
  "like_count": 100,
  "comment_count": 20,
  
  // 글리치 정보 추가
  "glitch_info": {
    "is_glitch": true,
    "original_video": {
      "id": "uuid",
      "title": "원본 영상 제목",
      "user": {
        "id": "uuid",
        "username": "원본유저"
      }
    },
    "glitch_type": "animate"
  },
  
  // 이 영상을 템플릿으로 사용한 글리치 개수
  "glitch_count": 42
}
```

---

### 2. 피드 API 수정

**현재**:
```python
@router.get("/", response_model=VideoListResponse)
async def list_videos(...):
    videos = db.query(Video).filter(
        Video.status == "completed"
    ).order_by(
        Video.created_at.desc()
    ).all()
    
    return VideoListResponse(videos=videos, ...)
```

**수정 후**:
```python
@router.get("/", response_model=VideoListResponse)
async def list_videos(...):
    videos = db.query(Video).filter(
        Video.status == "completed"
    ).order_by(
        Video.created_at.desc()
    ).all()
    
    # 각 비디오에 글리치 정보 추가
    for video in videos:
        # 이 영상이 글리치인지 확인
        glitch_relation = db.query(VideoGlitch).filter(
            VideoGlitch.glitch_video_id == video.id
        ).first()
        
        if glitch_relation:
            # 원본 영상 정보 가져오기
            original_video = db.query(Video).filter(
                Video.id == glitch_relation.original_video_id
            ).first()
            
            video.glitch_info = {
                "is_glitch": True,
                "original_video": original_video,
                "glitch_type": glitch_relation.glitch_type
            }
        
        # 이 영상을 템플릿으로 사용한 글리치 개수
        video.glitch_count = db.query(VideoGlitch).filter(
            VideoGlitch.original_video_id == video.id
        ).count()
    
    return VideoListResponse(videos=videos, ...)
```

---

### 3. 템플릿 영상 페이지 API

**새로운 엔드포인트**:
```
GET /v1/videos/{video_id}/glitches?page=1&page_size=20
```

**응답**:
```json
{
  "template_video": {
    "id": "uuid",
    "title": "원본 영상",
    "user": {...},
    "video_url": "https://..."
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
  ],
  "has_more": true,
  "next_cursor": "..."
}
```

**이미 구현됨!** ✅
```
GET /v1/glitch/videos/{video_id}/glitches
```

---

## 🎬 사용자 시나리오

### 시나리오 1: 일반 영상 업로드 → 글리치 생성

```
User 1: 댄스 영상 A 업로드
  ↓
User 2: 피드에서 A 발견
  ↓ "글리치" 버튼 클릭
User 2: 스튜디오에서 글리치 B 생성
  ↓
피드에 B 표시:
  "🎨 글리치 from @User1"
  "댄스 영상 A"
```

---

### 시나리오 2: 글리치 영상을 템플릿으로 또 글리치

```
User 3: 피드에서 글리치 B 발견
  ↓ "글리치" 버튼 클릭
User 3: 스튜디오에서 글리치 C 생성
  ↓
피드에 C 표시:
  "🎨 글리치 from @User2"
  "글리치 영상 B"
  
영상 B 정보:
  "🎨 글리치 from @User1"
  "댄스 영상 A"
```

**User 3은 B를 템플릿으로 사용**
- A와 직접적인 관계 없음
- B의 원본이 A라는 정보는 B 페이지에서 확인 가능

---

### 시나리오 3: 인기 템플릿 영상

```
영상 A가 인기를 끌어서 100명이 글리치

피드에서 A 표시:
  @User1
  "댄스 영상 A"
  👉 이 영상으로 글리치 100개
  
클릭 시:
  [템플릿 영상 페이지]
  - 원본 영상 A 재생
  - 글리치 목록 (100개)
    - 인기순 정렬
    - 최신순 정렬
  - "이 영상으로 글리치 만들기" 버튼
```

---

## 📊 통계 및 랭킹

### 인기 템플릿 영상

**API**:
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
      "trend_score": 95.5
    }
  ]
}
```

---

### 글리치 마스터 (유저 랭킹)

**기준**:
1. 내 영상이 템플릿으로 사용된 횟수
2. 내가 만든 글리치 수
3. 내 글리치의 좋아요 수

---

## 🚀 구현 단계

### Phase 1: 기본 체인 (현재 완료)
- ✅ VideoGlitch 모델
- ✅ 글리치 생성 API
- ✅ 글리치 조회 API

### Phase 2: 피드 통합 (필요)
- ❌ VideoResponse에 glitch_info 추가
- ❌ VideoResponse에 glitch_count 추가
- ❌ 피드 API에서 글리치 정보 포함

### Phase 3: 템플릿 페이지 (일부 완료)
- ✅ 글리치 목록 API
- ❌ 정렬 옵션 (인기순/최신순)
- ❌ 템플릿 통계

### Phase 4: 고급 기능
- ❌ 인기 템플릿 랭킹
- ❌ 글리치 마스터 랭킹
- ❌ 글리치 체인 시각화

---

## 🎯 다음 작업

### 즉시 구현 필요

1. **VideoResponse 스키마 확장**
   - `glitch_info` 필드 추가
   - `glitch_count` 필드 추가

2. **피드 API 수정**
   - 글리치 정보 자동 포함
   - N+1 쿼리 최적화 (JOIN 사용)

3. **글리치 목록 API 개선**
   - 정렬 옵션 추가
   - 페이지네이션 개선

---

## 💡 추가 아이디어

### 1. 글리치 챌린지
```
"이 영상으로 글리치 만들기 챌린지!"
- 기간: 1주일
- 상금: 1000 크레딧
- 참여: 글리치 버튼 클릭
```

### 2. 글리치 컬렉션
```
"내가 좋아하는 글리치 모음"
- 북마크 기능
- 컬렉션 공유
```

### 3. 글리치 스타일 필터
```
템플릿 페이지에서:
- Animate만 보기
- Replace만 보기
- 인기순/최신순
```

---

## ✅ 결론

**글리치 체인 = TikTok 음악 시스템**

### 핵심 원칙
1. 모든 영상은 템플릿이 될 수 있다
2. 평면 구조 (각 영상별로 독립)
3. 직접 템플릿만 표시 (단순함)
4. 체인 깊이 무제한

### 구현 우선순위
1. 🔴 High: VideoResponse 스키마 확장
2. 🔴 High: 피드 API에 글리치 정보 포함
3. 🟡 Medium: 글리치 목록 정렬 옵션
4. 🟢 Low: 인기 템플릿 랭킹

**지금 바로 Phase 2 (피드 통합)를 구현할까요?**

