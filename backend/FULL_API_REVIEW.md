# LOKIZ 전체 API 검수 보고서

**작성일**: 2025년 10월 29일  
**검수 범위**: 전체 29개 API 엔드포인트

---

## 📊 API 현황

### 총 29개 API

1. **Auth (3개)**: 인증 관련
2. **Videos (4개)**: 비디오 업로드 및 관리
3. **AI (6개)**: AI 작업 (I2V, 글리치, 음악)
4. **Glitch (2개)**: 글리치 체인
5. **Studio (3개)**: 스튜디오 편집
6. **Images (1개)**: 이미지 업로드
7. **Likes (2개)**: 좋아요
8. **Comments (2개)**: 댓글
9. **Follows (4개)**: 팔로우
10. **Root (2개)**: 헬스체크

---

## 🔍 검수 결과

### 🔴 Critical 문제 (3개)

#### 1. 댓글 API 메서드 중복
**문제**:
```
GET /v1/comments/videos/{video_id}  # 댓글 목록 조회
POST /v1/comments/videos/{video_id} # 댓글 작성
```

같은 경로에 GET, POST가 있는데, **PATCH, DELETE는 다른 경로**:
```
PATCH /v1/comments/{comment_id}
DELETE /v1/comments/{comment_id}
```

**영향**: 프론트엔드에서 혼란 가능

**해결 방안**: 현재 설계 유지 (RESTful 패턴에 부합)

---

#### 2. 사용자 프로필 API 누락
**문제**: 다른 사용자의 프로필을 조회하는 API가 없음

**현재**:
- `GET /v1/auth/me` - 내 정보만 조회 가능

**필요**:
- `GET /v1/users/{user_id}` - 다른 사용자 프로필 조회
- 팔로워/팔로잉 수
- 비디오 수
- 좋아요 받은 수

**영향**: 🔴 **High** - 사용자 프로필 페이지 구현 불가

---

#### 3. 비디오 응답에 사용자 정보 누락
**문제**: VideoResponse에 user 정보가 없음

**현재**:
```json
{
  "id": "uuid",
  "user_id": "uuid",  // ID만 있음
  "video_url": "...",
  "caption": "..."
}
```

**필요**:
```json
{
  "id": "uuid",
  "user": {  // 사용자 정보 포함
    "id": "uuid",
    "username": "john_doe",
    "display_name": "John Doe",
    "profile_image_url": "..."
  },
  "video_url": "...",
  "caption": "..."
}
```

**영향**: 🔴 **High** - 피드에서 사용자 이름 표시 불가

---

### 🟡 Major 문제 (5개)

#### 4. 댓글/팔로우 응답에 사용자 정보 누락
**문제**: CommentResponse, FollowResponse에도 user 정보 없음

**현재 CommentResponse**:
```json
{
  "id": "uuid",
  "user_id": "uuid",  // ID만
  "content": "..."
}
```

**필요**:
```json
{
  "id": "uuid",
  "user": {
    "id": "uuid",
    "username": "...",
    "display_name": "...",
    "profile_image_url": "..."
  },
  "content": "..."
}
```

**영향**: 🟡 **Medium** - 댓글 작성자 이름 표시 불가

---

#### 5. 비디오 상태 (status) 필터링 누락
**문제**: 내 영상 목록 API에서 status 필터가 없음

**현재**:
```python
GET /v1/videos/me  # 모든 상태 (processing, completed, failed)
```

**필요**:
```python
GET /v1/videos/me?status=completed  # 완료된 것만
GET /v1/videos/me?status=processing  # 처리 중만
```

**영향**: 🟡 **Medium** - 처리 중인 영상과 완료된 영상 구분 불가

---

#### 6. 페이지네이션 불일치
**문제**: API마다 페이지네이션 방식이 다름

**피드 API**:
```python
GET /v1/videos/?cursor=...  # Cursor-based
```

**댓글 API**:
```python
GET /v1/comments/videos/{video_id}?page=1  # Offset-based
```

**영향**: 🟡 **Medium** - 프론트엔드 구현 복잡도 증가

**해결 방안**: 
- 피드: Cursor-based (무한 스크롤)
- 댓글/팔로우: Offset-based (페이지 번호)
- 현재 설계 유지 (용도에 따라 다름)

---

#### 7. 글리치 목록 API 정렬 옵션 없음
**문제**: 글리치 목록을 정렬할 수 없음

**현재**:
```python
GET /v1/glitch/videos/{video_id}/glitches  # 생성일순만
```

**필요**:
```python
GET /v1/glitch/videos/{video_id}/glitches?sort=popular  # 인기순
GET /v1/glitch/videos/{video_id}/glitches?sort=latest   # 최신순
```

**영향**: 🟡 **Medium** - TikTok 음악 페이지처럼 인기순 정렬 불가

---

#### 8. 비디오 삭제 시 연관 데이터 처리
**문제**: 비디오 삭제 시 글리치 체인이 깨짐

**시나리오**:
```
영상 A (원본)
  ↓
영상 B (A를 글리치)
  ↓
영상 C (B를 글리치)
```

**A를 삭제하면?**
- B의 `original_video_id`가 NULL이 됨 (ON DELETE SET NULL)
- 하지만 VideoGlitch는 `ON DELETE CASCADE`

**영향**: 🟡 **Medium** - 데이터 일관성 문제

**해결 방안**: 
- 옵션 A: 글리치가 있는 영상은 삭제 불가
- 옵션 B: 영상 삭제 시 "비공개" 처리
- 옵션 C: 현재대로 CASCADE (글리치 관계도 삭제)

---

### 🟢 Minor 문제 (4개)

#### 9. 좋아요/팔로우 토글 API 없음
**문제**: 좋아요/팔로우를 토글하려면 2번 호출 필요

**현재**:
```javascript
// 좋아요 토글
const { liked } = await checkIfLiked(video_id);
if (liked) {
  await unlikeVideo(video_id);  // DELETE
} else {
  await likeVideo(video_id);    // POST
}
```

**개선안**:
```python
POST /v1/likes/videos/{video_id}/toggle  # 한 번에 토글
```

**영향**: 🟢 **Low** - 편의성 문제, 기능은 작동함

---

#### 10. 에러 메시지 일관성 부족
**문제**: 에러 응답 형식이 일관되지 않음

**예시**:
```json
// 어떤 API
{"detail": "Video not found"}

// 다른 API
{"detail": {"message": "비디오를 찾을 수 없습니다", "code": "VIDEO_NOT_FOUND"}}
```

**영향**: 🟢 **Low** - 프론트엔드 에러 처리 복잡도 증가

---

#### 11. Rate Limiting 없음
**문제**: API 호출 횟수 제한이 없음

**영향**: 🟢 **Low** - 개발 환경에서는 문제없음, 프로덕션에서 필요

---

#### 12. CORS 설정 확인 필요
**문제**: CORS 설정이 모든 origin 허용 중

**현재**:
```python
allow_origins=["*"]
```

**영향**: 🟢 **Low** - 개발 환경에서는 문제없음, 프로덕션에서 제한 필요

---

## 📋 검수 요약

### 문제점 통계
- 🔴 Critical: 3개
- 🟡 Major: 5개
- 🟢 Minor: 4개
- **총 12개 문제**

### 우선순위별 수정 계획

#### 즉시 수정 필요 (Critical)
1. ✅ 사용자 프로필 API 추가
2. ✅ VideoResponse에 user 정보 추가
3. ✅ CommentResponse, FollowResponse에 user 정보 추가

#### 중요 (Major)
4. ⚠️ 비디오 상태 필터링 추가
5. ⚠️ 글리치 목록 정렬 옵션 추가
6. ⚠️ 비디오 삭제 정책 결정

#### 개선 (Minor)
7. 🔵 좋아요/팔로우 토글 API (선택)
8. 🔵 에러 메시지 표준화 (선택)
9. 🔵 Rate Limiting (프로덕션)
10. 🔵 CORS 설정 (프로덕션)

---

## 🎯 상세 수정 계획

### 1. 사용자 프로필 API 추가

#### 새로운 API
```python
GET /v1/users/{user_id}
```

#### 응답
```json
{
  "id": "uuid",
  "username": "john_doe",
  "display_name": "John Doe",
  "bio": "...",
  "profile_image_url": "...",
  "follower_count": 1000,
  "following_count": 500,
  "video_count": 50,
  "total_likes": 10000,
  "created_at": "..."
}
```

---

### 2. VideoResponse 스키마 확장

#### 현재
```python
class VideoResponse(BaseModel):
    id: UUID
    user_id: UUID
    video_url: str
    ...
```

#### 수정 후
```python
class UserBasicInfo(BaseModel):
    id: UUID
    username: str
    display_name: str
    profile_image_url: Optional[str]

class VideoResponse(BaseModel):
    id: UUID
    user: UserBasicInfo  # user_id 대신
    video_url: str
    ...
```

---

### 3. CommentResponse, FollowResponse 확장

#### CommentResponse
```python
class CommentResponse(BaseModel):
    id: UUID
    user: UserBasicInfo  # 추가
    video_id: UUID
    content: str
    created_at: datetime
```

#### FollowResponse
```python
class FollowResponse(BaseModel):
    id: UUID
    follower: UserBasicInfo  # 추가
    following: UserBasicInfo  # 추가
    created_at: datetime
```

---

### 4. 비디오 상태 필터링

#### API 수정
```python
@router.get("/me")
async def get_my_videos(
    status: Optional[str] = Query(None, regex="^(processing|completed|failed)$"),
    ...
):
    query = db.query(Video).filter(Video.user_id == current_user.id)
    
    if status:
        query = query.filter(Video.status == status)
    
    videos = query.order_by(Video.created_at.desc()).all()
    ...
```

---

### 5. 글리치 목록 정렬

#### API 수정
```python
@router.get("/videos/{video_id}/glitches")
async def get_video_glitches(
    video_id: UUID,
    sort: str = Query("latest", regex="^(latest|popular)$"),
    ...
):
    query = db.query(Video).join(VideoGlitch).filter(
        VideoGlitch.original_video_id == video_id
    )
    
    if sort == "latest":
        query = query.order_by(VideoGlitch.created_at.desc())
    elif sort == "popular":
        query = query.order_by(Video.like_count.desc())
    
    videos = query.all()
    ...
```

---

### 6. 비디오 삭제 정책

#### 제안: 옵션 B (비공개 처리)

**이유**:
- 글리치 체인 유지
- 사용자가 실수로 삭제해도 복구 가능
- TikTok도 비슷한 방식 사용

**구현**:
```python
@router.delete("/{video_id}")
async def delete_video(...):
    # 실제 삭제 대신 비공개 처리
    video.status = "deleted"
    video.is_public = False
    db.commit()
```

---

## ✅ 검수 체크리스트

### API 설계
- ✅ RESTful 원칙 준수
- ⚠️ 응답 스키마 일관성 (user 정보 누락)
- ✅ HTTP 메서드 적절성
- ✅ 상태 코드 적절성

### 데이터 무결성
- ✅ 외래 키 제약조건
- ✅ UniqueConstraint
- ⚠️ CASCADE 정책 검토 필요

### 보안
- ✅ JWT 인증
- ✅ 권한 검증 (본인만 수정/삭제)
- ⚠️ CORS 설정 (프로덕션)
- ⚠️ Rate Limiting (프로덕션)

### 성능
- ✅ 페이지네이션
- ⚠️ N+1 쿼리 (user 정보 조회 시)
- ✅ 인덱스 설정

### 유저 경험
- ⚠️ 사용자 프로필 API 누락
- ⚠️ 비디오 상태 필터링 누락
- ⚠️ 글리치 정렬 옵션 누락
- ✅ 에러 메시지 명확성

---

## 🚀 다음 단계

### 즉시 수정 (Critical 3개)
1. 사용자 스키마 작성
2. 사용자 프로필 API 추가
3. VideoResponse, CommentResponse, FollowResponse에 user 정보 추가

### 이후 수정 (Major 3개)
4. 비디오 상태 필터링
5. 글리치 정렬 옵션
6. 비디오 삭제 정책 구현

**예상 소요 시간**: 1-2시간

수정을 시작하시겠습니까?

