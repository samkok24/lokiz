# LOKIZ Phase 3 완료 요약

**완료 날짜**: 2025년 10월 29일

---

## 📋 Phase 3 목표

AI 작업 API 구현 - I2V 기반 비디오 생성 및 글리치 기능

---

## ✅ 완료된 작업

### 1. 기획서 수정
- **파일**: `/home/ubuntu/lokiz_planning_document.md`
- **변경사항**:
  - VTV (Video-to-Video) → I2V (Image-to-Video) 기반으로 전환
  - 스튜디오 워크플로우 명확화: 영상 업로드 → 프레임 캡처 → 템플릿 프롬프트 + I2V
  - 글리치 기능 추가 (WAN 2.2 Animate/Replace 모델)
  - 크레딧 시스템 업데이트

### 2. Replicate 서비스 구현
- **파일**: `/home/ubuntu/lokiz-backend/app/services/replicate_service.py`
- **구현 메서드**:
  - `generate_i2v_template()`: 모션/스타일 템플릿 생성 (veo-3-fast)
  - `generate_glitch_animate()`: 글리치 모션 적용 (WAN 2.2 Animate)
  - `generate_glitch_replace()`: 글리치 주체 교체 (WAN 2.2 Replace)
  - `generate_music()`: 음악 생성 (suno-ai/bark)

### 3. 프레임 캡처 유틸리티
- **파일**: `/home/ubuntu/lokiz-backend/app/utils/video_utils.py`
- **구현 함수**:
  - `extract_frame_from_video()`: ffmpeg 기반 프레임 추출
  - `get_video_duration()`: 비디오 길이 확인

### 4. AI 작업 스키마 업데이트
- **파일**: `/home/ubuntu/lokiz-backend/app/schemas/ai_job.py`
- **새로운 스키마**:
  - `FrameCaptureRequest`: 프레임 캡처 요청
  - `FrameCaptureResponse`: 프레임 캡처 응답
  - `I2VTemplateRequest`: I2V 템플릿 생성 요청
  - `GlitchAnimateRequest`: 글리치 모션 적용 요청
  - `GlitchReplaceRequest`: 글리치 주체 교체 요청

### 5. AI 라우터 구현
- **파일**: `/home/ubuntu/lokiz-backend/app/routers/ai.py`
- **구현 엔드포인트**:
  - `POST /v1/ai/capture-frame`: 프레임 캡처
  - `POST /v1/ai/template`: 모션/스타일 템플릿 (20 크레딧)
  - `POST /v1/ai/glitch/animate`: 글리치 모션 적용 (30 크레딧)
  - `POST /v1/ai/glitch/replace`: 글리치 주체 교체 (30 크레딧)
  - `POST /v1/ai/music`: 음악 생성 (5 크레딧)
  - `GET /v1/ai/jobs/{job_id}`: AI 작업 상태 조회

### 6. Mock S3 서비스 확장
- **파일**: `/home/ubuntu/lokiz-backend/app/services/mock_s3_service.py`
- **추가 메서드**:
  - `download_file()`: S3에서 파일 다운로드 (Mock)
  - `upload_file()`: S3로 파일 업로드 (Mock)

### 7. 코드 품질 검수
- **Lint 검사**: flake8 통과 (0개 오류)
- **네이밍 규칙**: snake_case (변수/함수), PascalCase (클래스)
- **타입 힌팅**: 모든 함수에 타입 힌트 적용
- **문서화**: 모든 함수에 docstring 작성

---

## 🎯 핵심 기능

### A. 모션/스타일 템플릿 (I2V 기반)
**작동 방식**:
1. 메인 영상 업로드 후 프리뷰 재생
2. 원하는 장면에서 프레임 캡처 (이미지 추출)
3. 템플릿 선택 (AI 허그, 댄스 모션 등)
4. 캡처 이미지 + 템플릿 프롬프트 → I2V 모델 → 새로운 영상 생성

**크레딧**: 20 크레딧  
**생성 길이**: 5-10초  
**모델**: `google/veo-3-fast`

### B. 글리치 (Glitch) - WAN 2.2 기반 리믹스
**작동 방식**:
1. 피드에서 마음에 드는 영상의 '글리치' 버튼 클릭
2. 해당 영상이 스튜디오로 로드 (템플릿 영상으로 사용)
3. 내 이미지 업로드 OR 내 메인 영상에서 프레임 캡처
4. 모델 선택:
   - **WAN 2.2 Animate**: 템플릿 영상의 모션을 내 이미지에 적용
   - **WAN 2.2 Replace**: 템플릿 영상의 주체를 내 이미지로 교체
5. I2V 생성 → 새로운 영상 완성

**크레딧**: 30 크레딧  
**생성 길이**: 5-10초  
**모델**: `wan-video/wan-2.2-animate-animation`, `wan-video/wan-2.2-animate-replace`

### C. AI 음악 생성
**작동 방식**:
- 텍스트 프롬프트 입력 (예: "신나는 일렉트로닉 비트")
- AI가 영상에 어울리는 배경 음악 생성

**크레딧**: 5 크레딧  
**길이**: 60초  
**모델**: `suno-ai/bark`

---

## 📊 API 엔드포인트 목록

### 프레임 캡처
```
POST /v1/ai/capture-frame
```
**요청**:
```json
{
  "video_id": "uuid",
  "timestamp": 5.5
}
```
**응답**:
```json
{
  "image_url": "https://mock-s3.lokiz.dev/...",
  "timestamp": 5.5,
  "video_id": "uuid"
}
```

### 모션/스타일 템플릿
```
POST /v1/ai/template
```
**요청**:
```json
{
  "image_url": "https://...",
  "template": "ai_hug",
  "prompt": "Two people hugging with AI effect",
  "duration": 5
}
```
**크레딧**: 20

### 글리치 모션 적용
```
POST /v1/ai/glitch/animate
```
**요청**:
```json
{
  "template_video_id": "uuid",
  "user_image_url": "https://...",
  "prompt": "Apply dance motion"
}
```
**크레딧**: 30

### 글리치 주체 교체
```
POST /v1/ai/glitch/replace
```
**요청**:
```json
{
  "template_video_id": "uuid",
  "user_image_url": "https://...",
  "prompt": "Replace subject"
}
```
**크레딧**: 30

### 음악 생성
```
POST /v1/ai/music
```
**요청**:
```json
{
  "prompt": "Upbeat electronic beat",
  "duration": 60
}
```
**크레딧**: 5

### AI 작업 상태 조회
```
GET /v1/ai/jobs/{job_id}
```
**응답**:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "job_type": "i2v_template",
  "status": "completed",
  "input_data": {...},
  "output_data": {
    "video_url": "https://...",
    "model": "google/veo-3-fast"
  },
  "credits_used": 20,
  "created_at": "2025-10-29T...",
  "completed_at": "2025-10-29T..."
}
```

---

## 🔧 기술 스택

### AI 모델 (Replicate)
- **I2V**: `google/veo-3-fast` (15 크레딧)
- **WAN 2.2 Animate**: `wan-video/wan-2.2-animate-animation` (30 크레딧)
- **WAN 2.2 Replace**: `wan-video/wan-2.2-animate-replace` (30 크레딧)
- **음악 생성**: `suno-ai/bark` (5 크레딧)

### 비디오 처리
- **ffmpeg**: 프레임 추출, 비디오 길이 확인
- **ffprobe**: 비디오 메타데이터 분석

### 파일 저장
- **Mock S3**: 개발 환경용 파일 저장소
- **실제 배포**: AWS S3 연동 필요

---

## ⚠️ 주의사항

### 개발 환경
- Mock S3 사용 중 (실제 파일 업로드/다운로드 미구현)
- 프레임 캡처 기능은 실제 비디오 파일이 필요
- Replicate API 호출은 실제 크레딧 소모

### 실제 배포 시 필요한 작업
1. AWS S3 연동
2. 실제 비디오 파일 업로드/다운로드 구현
3. Replicate API 키 보안 강화
4. 비동기 작업 처리 (Celery 또는 RQ)
5. Webhook 구현 (AI 작업 완료 알림)

---

## 📈 다음 단계 (Phase 4)

### 소셜 기능 API
1. 좋아요 API
2. 댓글 API
3. 팔로우 API
4. 리믹스 API
5. 피드 알고리즘

### 프론트엔드 개발
1. React + TypeScript 설정
2. 인증 UI
3. 비디오 업로드 UI
4. 프레임 캡처 UI
5. AI 편집 UI (템플릿, 글리치)
6. 피드 UI

---

## 🎉 Phase 3 완료!

모든 AI 작업 API가 성공적으로 구현되었습니다. 이제 소셜 기능 API를 개발하거나 프론트엔드 개발을 시작할 수 있습니다.

