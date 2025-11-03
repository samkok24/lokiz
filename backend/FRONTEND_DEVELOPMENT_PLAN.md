# LOKIZ 프론트엔드 개발 계획

**작성일:** 2025-10-30  
**목표:** LOKIZ MVP 프론트엔드 완성 (틱톡 스타일)  
**플랫폼:** 웹앱 (데스크톱 + 모바일 반응형)

---

## 📋 Executive Summary

**개발 기간:** 약 4-6주  
**우선순위:** MVP 핵심 기능 (백엔드 82개 API 연동)  
**디자인:** 틱톡 UI/UX 동일하게 구현

---

## 🛠️ 기술 스택 추천

### 프레임워크: **Next.js 14 (App Router)**

**선택 이유:**
1. **SSR/SSG 지원** - SEO 최적화 (검색 노출 중요)
2. **Image Optimization** - 썸네일 자동 최적화
3. **API Routes** - 프록시/미들웨어 구현 용이
4. **File-based Routing** - 직관적인 라우팅
5. **React Server Components** - 성능 최적화
6. **틱톡도 Next.js 사용** - 검증된 선택

### 언어: **TypeScript**

**선택 이유:**
1. **타입 안전성** - API 응답 타입 정의
2. **자동완성** - 개발 생산성 향상
3. **리팩토링 용이** - 대규모 코드베이스 관리
4. **백엔드 스키마 공유** - Pydantic → TypeScript 변환

### 상태 관리: **Zustand + React Query**

**Zustand (글로벌 상태):**
- 사용자 인증 상태
- 테마 설정
- 재생 중인 영상 정보

**React Query (서버 상태):**
- API 데이터 캐싱
- 무한 스크롤
- 낙관적 업데이트 (좋아요, 팔로우)

**선택 이유:**
- Redux보다 간단하고 가벼움
- React Query는 서버 상태 관리에 최적화
- 틱톡 수준의 성능 구현 가능

### UI 라이브러리: **Tailwind CSS + Headless UI**

**Tailwind CSS:**
- 빠른 개발 속도
- 일관된 디자인 시스템
- 틱톡 스타일 재현 용이
- 반응형 디자인 간편

**Headless UI:**
- 접근성 (a11y) 기본 제공
- 모달, 드롭다운 등 컴포넌트
- Tailwind와 완벽 호환

### 비디오 플레이어: **Video.js + HLS.js**

**선택 이유:**
- 틱톡 스타일 세로 스크롤 피드 구현
- 자동 재생/일시정지
- 음소거/음소거 해제
- 진행 바, 볼륨 컨트롤
- HLS 스트리밍 지원

### 애니메이션: **Framer Motion**

**선택 이유:**
- 부드러운 페이지 전환
- 스크롤 애니메이션
- 제스처 인식 (스와이프)
- 틱톡 수준의 인터랙션

### 아이콘: **Lucide React**

**선택 이유:**
- 틱톡과 유사한 아이콘 스타일
- 트리 쉐이킹 지원
- TypeScript 지원

### 폼 관리: **React Hook Form + Zod**

**선택 이유:**
- 성능 최적화 (불필요한 리렌더 방지)
- Zod로 유효성 검증
- TypeScript 타입 자동 생성

---

## 📁 프로젝트 구조

```
lokiz-frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # 인증 그룹
│   │   ├── login/
│   │   └── register/
│   ├── (main)/                   # 메인 레이아웃 그룹
│   │   ├── layout.tsx            # 네비게이션 포함
│   │   ├── page.tsx              # For You 피드
│   │   ├── following/            # Following 피드
│   │   ├── explore/              # 탐색 (해시태그, 트렌딩)
│   │   ├── notifications/        # 알림
│   │   └── profile/
│   │       └── [username]/       # 사용자 프로필
│   ├── video/
│   │   └── [id]/                 # 영상 상세 (공유 링크)
│   ├── hashtag/
│   │   └── [name]/               # 해시태그 페이지
│   ├── search/                   # 검색 결과
│   ├── studio/                   # 스튜디오 (영상 편집)
│   │   ├── upload/
│   │   ├── glitch/
│   │   └── create/
│   ├── settings/                 # 설정
│   ├── api/                      # API Routes (프록시)
│   ├── layout.tsx                # 루트 레이아웃
│   └── globals.css               # Tailwind CSS
│
├── components/                   # 재사용 컴포넌트
│   ├── feed/
│   │   ├── VideoFeed.tsx         # 세로 스크롤 피드
│   │   ├── VideoCard.tsx         # 영상 카드
│   │   └── VideoPlayer.tsx       # 비디오 플레이어
│   ├── ui/                       # UI 컴포넌트
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   └── Avatar.tsx
│   ├── layout/
│   │   ├── Header.tsx            # 상단 헤더
│   │   ├── Sidebar.tsx           # 사이드바 (데스크톱)
│   │   └── BottomNav.tsx         # 하단 네비게이션 (모바일)
│   ├── social/
│   │   ├── LikeButton.tsx
│   │   ├── CommentSection.tsx
│   │   ├── FollowButton.tsx
│   │   └── ShareButton.tsx
│   └── studio/
│       ├── Timeline.tsx
│       ├── FrameSelector.tsx
│       └── GlitchPreview.tsx
│
├── lib/                          # 유틸리티
│   ├── api/                      # API 클라이언트
│   │   ├── client.ts             # Axios 인스턴스
│   │   ├── auth.ts               # 인증 API
│   │   ├── videos.ts             # 비디오 API
│   │   ├── social.ts             # 소셜 API
│   │   ├── ai.ts                 # AI API
│   │   └── feed.ts               # 피드 API
│   ├── hooks/                    # Custom Hooks
│   │   ├── useAuth.ts
│   │   ├── useInfiniteScroll.ts
│   │   ├── useVideoPlayer.ts
│   │   └── useOptimisticUpdate.ts
│   ├── store/                    # Zustand Store
│   │   ├── authStore.ts
│   │   ├── playerStore.ts
│   │   └── themeStore.ts
│   ├── utils/
│   │   ├── format.ts             # 날짜, 숫자 포맷
│   │   ├── validation.ts         # 유효성 검증
│   │   └── constants.ts          # 상수
│   └── types/                    # TypeScript 타입
│       ├── api.ts                # API 응답 타입
│       ├── models.ts             # 데이터 모델
│       └── components.ts         # 컴포넌트 Props
│
├── public/                       # 정적 파일
│   ├── icons/
│   ├── images/
│   └── sounds/                   # 효과음
│
├── styles/                       # 스타일
│   └── video-player.css          # Video.js 커스텀 스타일
│
├── .env.local                    # 환경 변수
├── next.config.js                # Next.js 설정
├── tailwind.config.js            # Tailwind 설정
├── tsconfig.json                 # TypeScript 설정
└── package.json
```

---

## 🎯 MVP 기능 목록 (백엔드 82개 API 기반)

### Phase 1: 기본 인프라 (1주)

#### 1.1. 프로젝트 셋업
- [x] Next.js 14 프로젝트 생성
- [x] TypeScript 설정
- [x] Tailwind CSS 설정
- [x] ESLint, Prettier 설정
- [x] 환경 변수 설정

#### 1.2. API 클라이언트
- [x] Axios 인스턴스 생성
- [x] 인터셉터 (토큰, 에러 처리)
- [x] API 함수 작성 (82개 엔드포인트)
- [x] TypeScript 타입 정의

#### 1.3. 인증 시스템
- [x] 회원가입 페이지
- [x] 로그인 페이지
- [x] JWT 토큰 관리
- [x] Protected Routes
- [x] 비로그인 접근 정책

#### 1.4. 레이아웃
- [x] 헤더 (로고, 검색, 알림, 프로필)
- [x] 사이드바 (데스크톱)
- [x] 하단 네비게이션 (모바일)
- [x] 반응형 디자인

---

### Phase 2: 피드 시스템 (1.5주)

#### 2.1. For You 피드
- [x] 세로 스크롤 피드 구현
- [x] 비디오 플레이어 (자동 재생)
- [x] 무한 스크롤
- [x] 스와이프 제스처
- [x] 우측 액션 버튼 (좋아요, 댓글, 공유, 글리치)

#### 2.2. Following 피드
- [x] 팔로우한 사용자 영상
- [x] 탭 전환 (For You / Following)
- [x] 빈 피드 처리

#### 2.3. 비디오 플레이어
- [x] Video.js 통합
- [x] 자동 재생/일시정지
- [x] 음소거/음소거 해제
- [x] 진행 바
- [x] 볼륨 컨트롤
- [x] 전체화면

#### 2.4. 소셜 인터랙션
- [x] 좋아요 버튼 (낙관적 업데이트)
- [x] 댓글 버튼 (모달)
- [x] 공유 버튼 (링크 복사)
- [x] 글리치 버튼 (글리치 모달)
- [x] 카운트 표시 (10.1K 형식)

---

### Phase 3: 사용자 프로필 (1주)

#### 3.1. 프로필 페이지
- [x] 사용자 정보 (아바타, 이름, bio)
- [x] 팔로워/팔로잉 수
- [x] 팔로우 버튼
- [x] 탭 (영상, 좋아요한 영상)
- [x] 그리드 뷰 (썸네일)

#### 3.2. 프로필 편집
- [x] 프로필 사진 업로드
- [x] 이름, bio 수정
- [x] 폼 유효성 검증

#### 3.3. 팔로우 시스템
- [x] 팔로우/언팔로우 버튼
- [x] 팔로워 목록 모달
- [x] 팔로잉 목록 모달
- [x] 낙관적 업데이트

---

### Phase 4: 댓글 시스템 (0.5주)

#### 4.1. 댓글 모달
- [x] 댓글 목록 (무한 스크롤)
- [x] 댓글 작성
- [x] 댓글 수정/삭제
- [x] 댓글 좋아요
- [x] 답글 (대댓글)

#### 4.2. 댓글 UI
- [x] 사용자 아바타
- [x] 시간 표시 (1분 전, 1시간 전)
- [x] 좋아요 수
- [x] 더보기 메뉴 (수정, 삭제, 신고)

---

### Phase 5: 검색 및 탐색 (0.5주)

#### 5.1. 검색
- [x] 검색 바 (헤더)
- [x] 자동완성 (사용자, 해시태그)
- [x] 검색 결과 페이지 (사용자, 영상, 해시태그 탭)
- [x] 최근 검색어

#### 5.2. 해시태그
- [x] 해시태그 페이지 (그리드 뷰)
- [x] 트렌딩 해시태그
- [x] 해시태그 통계 (영상 수, 조회수)

#### 5.3. 탐색 페이지
- [x] 트렌딩 영상
- [x] 카테고리별 영상
- [x] 추천 크리에이터

---

### Phase 6: 글리치 시스템 (1주)

#### 6.1. 글리치 모달
- [x] 글리치 목록 (그리드 뷰)
- [x] 틱톡 "원음" 스타일
- [x] 썸네일, 사용자 정보, 통계
- [x] 무한 스크롤

#### 6.2. 글리치 생성
- [x] 글리치 버튼 클릭
- [x] 영상 선택 (템플릿)
- [x] 이미지 업로드
- [x] 구간 선택 (start_time, end_time)
- [x] 프롬프트 입력
- [x] 생성 진행 상태

#### 6.3. 글리치 트리
- [x] 원본 영상 표시
- [x] 글리치 체인 시각화
- [x] 글리치 카운트

---

### Phase 7: 스튜디오 (AI 기능) (1.5주)

#### 7.1. 업로드
- [x] 드래그 앤 드롭
- [x] 파일 선택
- [x] 업로드 진행 상태
- [x] 썸네일 생성
- [x] 캡션, 해시태그 입력

#### 7.2. Sticker to Reality
- [x] 이미지 업로드
- [x] 영상 선택 (내 영상 또는 템플릿)
- [x] 구간 선택 (타임라인)
- [x] 프롬프트 입력
- [x] 생성 진행 상태
- [x] 크레딧 차감 표시

#### 7.3. 글리치 스튜디오
- [x] 모션 적용 (Animate)
- [x] 주체 교체 (Replace)
- [x] 프레임 캡처
- [x] 프리뷰

#### 7.4. 음악 생성
- [x] 프롬프트 입력
- [x] 장르 선택
- [x] 생성 진행 상태
- [x] 미리듣기

#### 7.5. 타임라인
- [x] 프레임 미리보기
- [x] 구간 선택 (드래그)
- [x] 재생/일시정지
- [x] 확대/축소

---

### Phase 8: 알림 시스템 (0.5주)

#### 8.1. 알림 목록
- [x] 알림 아이콘 (헤더)
- [x] 읽지 않은 알림 배지
- [x] 알림 드롭다운
- [x] 알림 타입별 아이콘
- [x] 알림 클릭 시 해당 페이지 이동

#### 8.2. 알림 타입
- [x] 좋아요 알림
- [x] 댓글 알림
- [x] 팔로우 알림
- [x] 글리치 알림
- [x] 시스템 알림

---

### Phase 9: 신고/차단 시스템 (0.5주)

#### 9.1. 차단
- [x] 사용자 차단 버튼
- [x] 차단 확인 모달
- [x] 차단 목록 페이지
- [x] 차단 해제

#### 9.2. 신고
- [x] 신고 버튼 (더보기 메뉴)
- [x] 신고 사유 선택
- [x] 신고 완료 메시지
- [x] 내 신고 목록

---

### Phase 10: 크레딧 시스템 (0.5주)

#### 10.1. 크레딧 표시
- [x] 헤더에 크레딧 잔액
- [x] 크레딧 아이콘 + 숫자
- [x] 일일 무료 크레딧 배지

#### 10.2. 크레딧 관리
- [x] 일일 무료 크레딧 받기 버튼
- [x] 크레딧 히스토리
- [x] 크레딧 부족 시 알림
- [x] 크레딧 패키지 (추후)

---

### Phase 11: 설정 및 기타 (0.5주)

#### 11.1. 설정 페이지
- [x] 계정 설정
- [x] 프라이버시 설정
- [x] 알림 설정
- [x] 테마 설정 (다크 모드)
- [x] 언어 설정

#### 11.2. 공유 기능
- [x] 링크 복사
- [x] SNS 공유 (Twitter, Facebook, KakaoTalk)
- [x] QR 코드 생성

#### 11.3. 에러 처리
- [x] 404 페이지
- [x] 500 페이지
- [x] 에러 바운더리
- [x] 토스트 알림

---

## 🎨 디자인 시스템 (틱톡 스타일)

### 색상 팔레트

```css
/* Primary */
--primary: #FE2C55;          /* 틱톡 레드 (좋아요, 액션 버튼) */
--primary-hover: #E01E46;

/* Secondary */
--secondary: #25F4EE;        /* 틱톡 시안 (강조, 링크) */

/* Background */
--bg-primary: #000000;       /* 검정 (피드 배경) */
--bg-secondary: #121212;     /* 다크 그레이 (카드, 모달) */
--bg-tertiary: #1F1F1F;      /* 밝은 다크 그레이 (호버) */

/* Text */
--text-primary: #FFFFFF;     /* 흰색 (주요 텍스트) */
--text-secondary: #A0A0A0;   /* 그레이 (부가 정보) */
--text-tertiary: #707070;    /* 다크 그레이 (비활성) */

/* Border */
--border: #2F2F2F;           /* 경계선 */

/* Success */
--success: #00D95F;          /* 초록 (성공 메시지) */

/* Error */
--error: #FF3B30;            /* 빨강 (에러 메시지) */

/* Warning */
--warning: #FFD60A;          /* 노랑 (경고 메시지) */
```

### 타이포그래피

```css
/* Font Family */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px - 작은 라벨 */
--text-sm: 0.875rem;   /* 14px - 부가 정보 */
--text-base: 1rem;     /* 16px - 본문 */
--text-lg: 1.125rem;   /* 18px - 제목 */
--text-xl: 1.25rem;    /* 20px - 큰 제목 */
--text-2xl: 1.5rem;    /* 24px - 페이지 제목 */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### 간격 (Spacing)

```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
```

### 둥근 모서리 (Border Radius)

```css
--radius-sm: 0.25rem;   /* 4px - 버튼, 입력 */
--radius-md: 0.5rem;    /* 8px - 카드 */
--radius-lg: 0.75rem;   /* 12px - 모달 */
--radius-xl: 1rem;      /* 16px - 큰 카드 */
--radius-full: 9999px;  /* 완전한 원 - 아바타 */
```

### 그림자 (Shadow)

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.5);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.5);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.5);
```

---

## 📱 반응형 디자인

### 브레이크포인트

```css
/* Mobile First */
--mobile: 0px;        /* 0-639px */
--tablet: 640px;      /* 640-1023px */
--desktop: 1024px;    /* 1024-1279px */
--wide: 1280px;       /* 1280px+ */
```

### 레이아웃

**모바일 (< 640px):**
- 전체 화면 피드
- 하단 네비게이션 (5개 아이콘)
- 햄버거 메뉴

**태블릿 (640px - 1023px):**
- 중앙 피드 (최대 600px)
- 좌측 사이드바 (축소)
- 하단 네비게이션

**데스크톱 (1024px+):**
- 좌측 사이드바 (확장)
- 중앙 피드 (최대 600px)
- 우측 추천 영역 (선택적)

---

## 🎬 비디오 플레이어 기능

### 틱톡 스타일 구현

**자동 재생:**
- 화면에 보이는 영상 자동 재생
- 스크롤 시 이전 영상 일시정지

**제스처:**
- 더블 탭: 좋아요
- 스와이프 업/다운: 다음/이전 영상
- 탭: 일시정지/재생
- 롱 프레스: 빠르게 감기

**UI:**
- 진행 바 (하단)
- 음소거 버튼 (우측 하단)
- 전체화면 버튼 (우측 하단)
- 우측 액션 버튼 (좋아요, 댓글, 공유, 글리치)

**성능:**
- Lazy Loading
- 비디오 프리로딩 (다음 2개)
- 메모리 관리 (화면 밖 영상 언로드)

---

## 🚀 성능 최적화

### 1. 이미지 최적화
- Next.js Image 컴포넌트 사용
- WebP 포맷 자동 변환
- Lazy Loading
- 블러 플레이스홀더

### 2. 코드 스플리팅
- 라우트 기반 자동 스플리팅
- 동적 import (모달, 무거운 컴포넌트)

### 3. 캐싱
- React Query 캐싱 (5분)
- API 응답 캐싱
- 이미지 브라우저 캐싱

### 4. 무한 스크롤 최적화
- Intersection Observer
- 가상 스크롤 (react-window)
- 페이지네이션 (커서 기반)

### 5. 번들 사이즈 최적화
- Tree Shaking
- 불필요한 라이브러리 제거
- 아이콘 개별 import

---

## 🔒 보안

### 1. XSS 방지
- DOMPurify로 HTML 새니타이징
- React의 기본 XSS 방어

### 2. CSRF 방지
- SameSite 쿠키
- CSRF 토큰 (API Routes)

### 3. 인증
- JWT 토큰 (HttpOnly 쿠키)
- Refresh Token
- 토큰 만료 처리

### 4. 환경 변수
- .env.local 사용
- 민감 정보 서버 사이드만

---

## 📊 개발 일정

### Week 1: 기본 인프라
- Day 1-2: 프로젝트 셋업, API 클라이언트
- Day 3-4: 인증 시스템
- Day 5-7: 레이아웃, 네비게이션

### Week 2: 피드 시스템
- Day 1-3: For You / Following 피드
- Day 4-5: 비디오 플레이어
- Day 6-7: 소셜 인터랙션 (좋아요, 댓글 버튼)

### Week 3: 프로필 및 댓글
- Day 1-3: 사용자 프로필
- Day 4-5: 댓글 시스템
- Day 6-7: 검색 및 탐색

### Week 4: 글리치 시스템
- Day 1-3: 글리치 모달, 글리치 트리
- Day 4-7: 글리치 생성 플로우

### Week 5: 스튜디오 (AI 기능)
- Day 1-2: 업로드
- Day 3-4: Sticker to Reality
- Day 5-6: 글리치 스튜디오
- Day 7: 음악 생성

### Week 6: 마무리
- Day 1-2: 알림, 신고/차단
- Day 3-4: 크레딧 시스템
- Day 5-6: 설정, 에러 처리
- Day 7: 테스트, 버그 수정

---

## 🧪 테스트

### 단위 테스트
- Jest + React Testing Library
- 컴포넌트 테스트
- 유틸 함수 테스트

### E2E 테스트
- Playwright
- 핵심 사용자 플로우
- 회원가입 → 로그인 → 피드 → 좋아요 → 댓글

### 성능 테스트
- Lighthouse
- Core Web Vitals
- 번들 사이즈 분석

---

## 📦 배포

### Vercel (권장)
- Next.js 최적화
- 자동 배포 (Git Push)
- Edge Functions
- 무료 SSL

### 환경 변수
```
NEXT_PUBLIC_API_URL=https://api.lokiz.app
NEXT_PUBLIC_S3_BUCKET=lokiz-videos
```

---

## 🎯 성공 지표

### 성능
- Lighthouse 점수 > 90
- First Contentful Paint < 1.5s
- Time to Interactive < 3s

### 사용자 경험
- 피드 로딩 < 1s
- 비디오 재생 지연 < 500ms
- 인터랙션 응답 < 100ms

---

## 📚 참고 자료

### 디자인
- 틱톡 웹 (tiktok.com)
- 틱톡 모바일 앱

### 기술 문서
- Next.js 14 Docs
- React Query Docs
- Tailwind CSS Docs
- Video.js Docs

---

**문서 버전:** 1.0  
**마지막 업데이트:** 2025-10-30  
**다음 단계:** 프로젝트 셋업 시작

