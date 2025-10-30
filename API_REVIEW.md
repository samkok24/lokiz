# LOKIZ API 검수 보고서

**검수 날짜**: 2025년 10월 29일

---

## 🔍 검수 항목

1. ✅ API 통신 테스트
2. ⚠️ API 설계 미스
3. ⚠️ 데이터 일관성 문제
4. ⚠️ 유저 경험 타격 요소
5. ⚠️ 보안 및 권한 검증

---

## ⚠️ 발견된 문제점

### 🔴 심각 (Critical)

#### 1. 글리치 API에서 Video 생성 시 인증 누락
**파일**: `app/routers/ai.py`
**위치**: `generate_glitch_animate()`, `generate_glitch_replace()`

**문제**:
```python
new_video = Video(
    user_id=current_user.id,
    title=f"Glitch from {template_video.title or 'video'}",
    url=result['output_url'],
    s3_key=f"glitch/{ai_job.id}.mp4",
    duration=5,
    status="completed"
)
```

**이슈**: 
- 생성된 비디오가 바로 `completed` 상태로 설정됨
- 실제로는 Replicate API가 비동기로 처리되므로 즉시 완료되지 않음
- 사용자가 아직 생성되지 않은 비디오를 볼 수 있음

**해결 방안**:
- AI 작업 완료 후 Webhook으로 비디오 상태 업데이트
- 또는 폴링으로 AI 작업 상태 확인 후 비디오 생성

---

#### 2. 프레임 캡처 API에서 Mock S3 다운로드 실패
**파일**: `app/routers/ai.py`
**위치**: `capture_frame()`

**문제**:
```python
s3_service.download_file(video.s3_key, local_video_path)
```

**이슈**:
- Mock S3는 실제 파일을 저장하지 않음
- `download_file()`은 빈 파일만 생성
- ffmpeg가 빈 파일에서 프레임을 추출할 수 없음

**해결 방안**:
- 개발 환경에서는 샘플 비디오 파일 사용
- 또는 Mock S3에 실제 파일 저장 기능 추가

---

#### 3. 글리치 체인 조회 시 권한 검증 없음
**파일**: `app/routers/glitch.py`
**위치**: `get_video_glitches()`, `get_glitch_source()`

**문제**:
```python
async def get_video_glitches(
    video_id: UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)  # Optional!
):
```

**이슈**:
- `current_user`가 Optional이므로 인증 없이 접근 가능
- 비공개 비디오의 글리치 체인도 조회 가능

**해결 방안**:
- `Optional` 제거하고 필수 인증으로 변경
- 또는 공개 비디오만 조회 가능하도록 필터링

---

### 🟡 중요 (Major)

#### 4. AI 작업 완료 후 비디오 ID 반환 없음
**파일**: `app/routers/ai.py`
**위치**: 모든 AI 엔드포인트

**문제**:
```python
return ai_job  # AIJobResponse만 반환
```

**이슈**:
- 글리치 생성 후 새로 만들어진 비디오 ID를 알 수 없음
- 사용자가 생성된 비디오를 찾을 수 없음

**해결 방안**:
- AIJobResponse에 `video_id` 필드 추가
- 또는 output_data에 video_id 포함

---

#### 5. 스튜디오 API에서 다른 사용자 비디오 접근 가능
**파일**: `app/routers/studio.py`
**위치**: 모든 엔드포인트

**문제**:
```python
video = db.query(Video).filter(
    Video.id == video_id,
    Video.user_id == current_user.id  # 본인 비디오만
).first()
```

**이슈**:
- 스튜디오는 본인 비디오만 편집 가능
- 하지만 글리치 워크플로우에서는 다른 사람 비디오도 봐야 함
- 현재 설계로는 다른 사람 비디오의 타임라인을 볼 수 없음

**해결 방안**:
- 공개 비디오는 누구나 타임라인 조회 가능하도록 변경
- 프레임 캡처는 본인 비디오만 가능

---

#### 6. 비디오 목록 API에 페이지네이션 없음
**파일**: `app/routers/video.py`
**위치**: `get_videos()`

**문제**:
```python
@router.get("/", response_model=VideoListResponse)
async def get_videos(
    skip: int = 0,
    limit: int = 20,  # 하드코딩된 제한
    ...
```

**이슈**:
- 피드가 무한 스크롤이어야 하는데 최대 20개만 반환
- 다음 페이지 조회 방법 불명확

**해결 방안**:
- Cursor-based 페이지네이션 구현
- 또는 offset-based 페이지네이션 명확화

---

#### 7. 글리치 생성 시 크레딧 차감 타이밍 문제
**파일**: `app/routers/ai.py`

**문제**:
```python
# AI 작업 시작 전에 크레딧 차감
current_user.credits -= CREDITS_REQUIRED
db.commit()

# 이후 Replicate API 호출 실패 가능
result = replicate_service.generate_glitch_animate(...)
```

**이슈**:
- AI 작업 실패 시 크레딧이 복구되지 않음
- 사용자가 크레딧만 잃고 결과물을 받지 못함

**해결 방안**:
- AI 작업 성공 후 크레딧 차감
- 또는 실패 시 크레딧 환불 로직 추가

---

### 🟢 경미 (Minor)

#### 8. 템플릿 API에서 duration 파라미터 검증 없음
**파일**: `app/routers/ai.py`

**문제**:
```python
class I2VTemplateRequest(BaseModel):
    duration: int = 5  # 5-10초여야 하는데 검증 없음
```

**이슈**:
- 사용자가 100초를 입력해도 통과
- Replicate API에서 거부될 가능성

**해결 방안**:
- Pydantic validator 추가 (5 ≤ duration ≤ 10)

---

#### 9. 비디오 삭제 시 글리치 관계 처리 불명확
**파일**: `app/routers/video.py`

**문제**:
- 원본 비디오 삭제 시 글리치 비디오는 어떻게 되는가?
- 글리치 비디오 삭제 시 관계 레코드는?

**이슈**:
- CASCADE 설정으로 자동 삭제되지만 사용자에게 경고 없음
- "이 비디오를 삭제하면 42개의 글리치도 삭제됩니다" 같은 안내 필요

**해결 방안**:
- 삭제 전 글리치 개수 확인 및 경고 메시지

---

#### 10. 스튜디오 구간 선택 시 오류 메시지 불친절
**파일**: `app/routers/studio.py`

**문제**:
```python
if duration > 10:
    raise HTTPException(
        status_code=400,
        detail="Selected range exceeds 10 second limit for AI processing"
    )
```

**이슈**:
- 왜 10초인지, 어떻게 해야 하는지 불명확

**해결 방안**:
- 더 친절한 메시지: "AI 처리는 최대 10초까지 가능합니다. 현재 선택: {duration}초"

---

## 📋 유저 경험 시나리오 검증

### 시나리오 1: 글리치 생성 워크플로우

**단계**:
1. 피드에서 영상 발견 → ✅
2. 글리치 버튼 클릭 → ❌ **문제**: 버튼 클릭 시 어떤 API를 호출해야 하는지 불명확
3. 내 영상 선택 → ✅
4. 프레임 캡처 → ❌ **문제**: Mock S3로 인해 실패
5. 글리치 생성 → ⚠️ **문제**: 생성된 비디오 ID를 알 수 없음
6. 결과 확인 → ❌ **문제**: 어떻게 확인하는지 불명확

**해결 필요**:
- 글리치 버튼 클릭 시 템플릿 비디오 정보 저장 방법 명확화
- 프레임 캡처 Mock 수정
- 생성된 비디오 ID 반환

---

### 시나리오 2: 다른 사람 영상으로 글리치 만들기

**단계**:
1. 피드에서 @user123의 영상 발견
2. 글리치 버튼 클릭
3. 스튜디오 진입 → ❌ **문제**: @user123의 영상 타임라인을 볼 수 없음 (본인 비디오만 조회 가능)

**해결 필요**:
- 스튜디오 API에서 공개 비디오는 누구나 조회 가능하도록 변경

---

### 시나리오 3: 글리치 체인 확인

**단계**:
1. 내 영상이 인기를 얻음
2. 다른 사람들이 내 영상으로 글리치 생성
3. 글리치 목록 확인 → ✅
4. 글리치의 글리치 확인 → ⚠️ **문제**: 재귀적 조회 불가능

**해결 필요**:
- 글리치 체인 재귀 조회 API 추가

---

## 🔒 보안 검증

### 1. 인증 누락
- ❌ 글리치 조회 API: Optional 인증
- ✅ 나머지 API: 필수 인증

### 2. 권한 검증
- ✅ 비디오 CRUD: 본인만 가능
- ❌ 스튜디오 API: 다른 사람 비디오 접근 불가 (글리치 워크플로우 방해)
- ✅ AI 작업: 본인만 조회 가능

### 3. 크레딧 검증
- ✅ 모든 AI API에서 크레딧 확인
- ⚠️ 크레딧 차감 타이밍 문제 (실패 시 환불 없음)

---

## 📊 데이터 일관성 검증

### 1. 비디오 상태 관리
- ❌ **문제**: 글리치 생성 시 바로 `completed` 상태
- **해결**: `processing` → Webhook → `completed`

### 2. 글리치 관계 무결성
- ✅ CASCADE 설정으로 자동 삭제
- ⚠️ 사용자 경고 없음

### 3. AI 작업 상태
- ✅ `processing`, `completed`, `failed` 상태 관리
- ⚠️ 타임아웃 처리 없음

---

## 🎯 우선순위별 수정 필요 항목

### 🔴 즉시 수정 필요 (Critical)
1. Mock S3 프레임 캡처 실패 → 샘플 비디오 사용
2. 글리치 체인 조회 인증 누락 → 필수 인증으로 변경
3. AI 작업 완료 후 비디오 ID 반환 → output_data에 추가

### 🟡 조만간 수정 필요 (Major)
4. 스튜디오 API 권한 문제 → 공개 비디오 조회 허용
5. 크레딧 차감 타이밍 → 성공 후 차감 또는 환불 로직
6. 비디오 상태 관리 → 비동기 처리 구현

### 🟢 개선 권장 (Minor)
7. duration 파라미터 검증
8. 비디오 삭제 시 경고 메시지
9. 오류 메시지 개선
10. 페이지네이션 명확화

---

## ✅ 검수 통과 항목

1. ✅ API 엔드포인트 구조 일관성
2. ✅ 네이밍 규칙 준수
3. ✅ 기본 인증 시스템
4. ✅ 데이터베이스 스키마 설계
5. ✅ Lint 검사 통과

---

## 📝 다음 단계

1. Critical 이슈 수정
2. Major 이슈 수정
3. 통합 테스트 작성
4. API 문서 업데이트

