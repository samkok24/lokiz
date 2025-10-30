# REMIX → GLITCH 용어 통일 완료

**작업일:** 2025년 10월 30일  
**목적:** 기획서에 맞게 "리믹스" 용어를 "글리치"로 통일

---

## ✅ 작업 완료 항목

### 1. 데이터베이스 변경

#### 컬럼 이름 변경 (데이터 보존)
```sql
ALTER TABLE videos 
RENAME COLUMN remix_count TO glitch_count;
```

**마이그레이션:**
- `450377ba8eb0_rename_remix_count_to_glitch_count.py`
- 기존 데이터 보존 (단순 컬럼 이름 변경)
- Downgrade 지원

---

### 2. 코드 변경 (6개 파일)

#### A. `app/models/video.py`
```python
# Before
remix_count = Column(Integer, default=0, nullable=False)
original_video = relationship("Video", remote_side=[id], backref="remixes")

# After
glitch_count = Column(Integer, default=0, nullable=False)
original_video = relationship("Video", remote_side=[id], backref="glitches")
```

#### B. `app/schemas/video.py`
```python
# Before
remix_count: int
glitch_count: int = 0

# After
glitch_count: int  # 통일
```

#### C. `app/routers/video.py`
```python
# Before
"remix_count": video.remix_count,

# After
"glitch_count": video.glitch_count,
```

#### D. `app/routers/ai.py` (2곳)
```python
# Before
# Increment remix_count on template video
template_video.remix_count += 1

# After
# Increment glitch_count on template video
template_video.glitch_count += 1
```

#### E. `app/routers/glitch.py`
```python
# Before
Shows the glitch chain - who remixed this video

# After
Shows the glitch chain - who glitched this video
```

#### F. `app/main.py`
```python
# Before
description="AI-powered social video remix platform"

# After
description="AI-powered social video glitch platform"
```

---

## 🎯 용어 정의 (최종 확정)

### 기획서 기준

**글리치 (Glitch) = 리믹스 (Remix)**

- **정의**: 다른 사람의 영상을 템플릿으로 사용하여 내 이미지로 새로운 영상을 생성하는 기능
- **기술**: WAN 2.2 기반 (Animate / Replace)
- **크레딧**: 30 크레딧
- **결과**: 원본 영상과 글리치 관계 기록

### 데이터베이스 구조

```
videos 테이블:
- glitch_count: 이 영상을 템플릿으로 사용한 글리치 개수
- original_video_id: 이 영상이 글리치인 경우, 원본 영상 ID

video_glitches 테이블:
- original_video_id: 원본 영상 ID
- glitch_video_id: 글리치 영상 ID
- glitch_type: 'animate' or 'replace'
```

---

## 🧪 검증 결과

### 1. 서버 시작 확인 ✅
```
Status: healthy
API 개수: 64
설명: AI-powered social video glitch platform
```

### 2. 코드에서 "remix" 용어 검색 ✅
```bash
$ grep -rn "remix" app/ --include="*.py"
(결과 없음)
```

**모든 "remix" 용어가 "glitch"로 변경되었습니다!**

---

## 📊 변경 영향 범위

### API 응답 변경

**Before:**
```json
{
  "id": "...",
  "remix_count": 5,
  "glitch_count": 0
}
```

**After:**
```json
{
  "id": "...",
  "glitch_count": 5
}
```

### 프론트엔드 영향

**변경 필요한 부분:**
1. API 응답에서 `remix_count` → `glitch_count`
2. UI 텍스트: "리믹스" → "글리치"
3. 버튼 라벨: "Remix" → "Glitch"

---

## 🎨 UI 용어 가이드

### 한국어
- ✅ 글리치
- ✅ 글리치하기
- ✅ 글리치 횟수
- ✅ 이 영상을 글리치했습니다

### 영어
- ✅ Glitch
- ✅ Glitch this video
- ✅ Glitch count
- ✅ Glitched from @username

---

## 📈 최종 상태

**총 64개 API 엔드포인트**

### 글리치 관련 API

1. ✅ `POST /v1/ai/glitch/animate` - 글리치 생성 (Animate)
2. ✅ `POST /v1/ai/glitch/replace` - 글리치 생성 (Replace)
3. ✅ `GET /v1/glitch/videos/{video_id}/glitches` - 글리치 목록
4. ✅ `GET /v1/glitch/videos/{video_id}/source` - 원본 영상 조회
5. ✅ `POST /v1/videos/batch-metadata` - 메타데이터 (glitch_count 포함)

### 데이터 흐름

```
1. 사용자가 영상 A를 보고 "글리치" 버튼 클릭
2. 스튜디오로 이동, 영상 A가 템플릿으로 로드
3. 내 이미지 업로드
4. AI 글리치 생성 (Animate or Replace)
5. 새 영상 B 생성
6. video_glitches 테이블에 관계 기록:
   - original_video_id: A
   - glitch_video_id: B
   - glitch_type: 'animate'
7. 영상 A의 glitch_count += 1
8. 영상 A 소유자에게 알림
```

---

## ✅ 기획서 요구사항 충족

**기획서 명시:**
> **B. 글리치 (Glitch) - WAN 2.2 기반 리믹스**
> - 피드에서 다른 사람의 영상을 템플릿으로 사용하여 내 이미지로 새로운 영상을 생성하는 고급 리믹스 기능

**구현 상태:** ✅ 완료

**특징:**
- ✅ 용어 통일 (리믹스 → 글리치)
- ✅ 데이터베이스 컬럼 이름 변경
- ✅ 모든 코드에서 용어 통일
- ✅ API 응답 일관성 확보
- ✅ 기존 데이터 보존

---

## 🚀 다음 단계

### 남은 MVP 기능

1. ⚠️ **AI 자동 통합 (Sticker to Reality)** - 미구현
   - 기획서의 핵심 차별화 기능
   - 40-50 크레딧

2. ⚠️ **글리치 추적 시스템 API** - 부분 구현
   - 글리치 체인 조회 ✅
   - 프로필 페이지 통합 필요

3. ✅ **크레딧 일일 무료 지급** - 완료

---

**작업자:** Manus AI  
**완료일:** 2025년 10월 30일  
**검증:** 통과 ✅

