# LOKIZ 코드 검수 체크리스트

모든 개발 단계마다 다음 항목들을 반드시 확인합니다.

---

## ✅ 1. 네이밍 규칙

### Python 표준 준수
- [ ] **변수명**: `snake_case` (예: `user_id`, `video_url`)
- [ ] **함수명**: `snake_case` (예: `get_user`, `create_video`)
- [ ] **클래스명**: `PascalCase` (예: `User`, `VideoService`)
- [ ] **상수명**: `UPPER_SNAKE_CASE` (예: `MAX_FILE_SIZE`, `DEFAULT_CREDITS`)
- [ ] **Private 변수/함수**: `_leading_underscore` (예: `_internal_method`)

### 데이터베이스
- [ ] **테이블명**: 복수형 `snake_case` (예: `users`, `videos`, `ai_jobs`)
- [ ] **컬럼명**: 단수형 `snake_case` (예: `user_id`, `created_at`)
- [ ] **외래키**: `{table}_id` 형식 (예: `user_id`, `video_id`)

### API
- [ ] **엔드포인트**: kebab-case 또는 snake_case (예: `/api/v1/auth/register`)
- [ ] **JSON 키**: `snake_case` (예: `access_token`, `user_id`)

### 일관성
- [ ] 같은 개념은 같은 이름 사용 (예: `user_id`를 `userId`, `uid` 등으로 혼용 금지)
- [ ] 약어 사용 최소화, 사용 시 일관성 유지

---

## ✅ 2. 코드 품질

### Lint 검사
- [ ] **flake8**: `flake8 app/ --max-line-length=120 --count`
- [ ] **결과**: 0개 오류
- [ ] **경고 처리**: 모든 경고 확인 및 수정

### 타입 힌팅
- [ ] 모든 함수 파라미터에 타입 명시
- [ ] 모든 함수 반환 타입 명시
- [ ] Optional, Union 등 적절히 사용

```python
# ✅ 좋은 예
def get_user(user_id: UUID, db: Session) -> User:
    return db.query(User).filter(User.id == user_id).first()

# ❌ 나쁜 예
def get_user(user_id, db):
    return db.query(User).filter(User.id == user_id).first()
```

### Import 정리
- [ ] 사용하지 않는 import 제거
- [ ] Import 순서: 표준 라이브러리 → 서드파티 → 로컬
- [ ] 각 그룹 사이 빈 줄

```python
# ✅ 좋은 예
from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.config import settings
```

### 들여쓰기 및 포맷팅
- [ ] 들여쓰기: 4칸 (Python 표준)
- [ ] 최대 라인 길이: 120자
- [ ] 함수/클래스 사이: 2줄 빈 줄
- [ ] 파일 끝: 빈 줄 1개

---

## ✅ 3. 데이터베이스

### 모델 정의
- [ ] 모든 테이블에 `id` (Primary Key)
- [ ] 타임스탬프: `created_at`, `updated_at` (필요시)
- [ ] Soft delete: `is_active` 또는 `deleted_at` (필요시)

### 외래키
- [ ] 올바른 테이블/컬럼 참조
- [ ] `ondelete` 옵션 명시 (CASCADE, SET NULL 등)
- [ ] 인덱스 설정 (`index=True`)

```python
# ✅ 좋은 예
user_id = Column(
    UUID(as_uuid=True),
    ForeignKey("users.id", ondelete="CASCADE"),
    nullable=False,
    index=True
)
```

### 인덱스
- [ ] 자주 조회하는 컬럼에 인덱스
- [ ] 외래키에 인덱스
- [ ] 복합 인덱스 고려 (필요시)

### 제약조건
- [ ] `nullable` 명시 (기본값: True)
- [ ] `unique` 설정 (이메일, 유저명 등)
- [ ] `default` 값 설정 (필요시)

---

## ✅ 4. API

### RESTful 규칙
- [ ] GET: 조회
- [ ] POST: 생성
- [ ] PUT/PATCH: 수정
- [ ] DELETE: 삭제

### 엔드포인트 구조
- [ ] 버전 포함: `/v1/...`
- [ ] 리소스 명확: `/users`, `/videos`
- [ ] 계층 구조: `/videos/{id}/comments`

### 응답 형식
- [ ] 일관된 JSON 구조
- [ ] HTTP 상태 코드 적절히 사용
  - 200: 성공
  - 201: 생성 성공
  - 400: 잘못된 요청
  - 401: 인증 실패
  - 403: 권한 없음
  - 404: 리소스 없음
  - 500: 서버 오류

### 에러 처리
- [ ] 모든 예외 처리
- [ ] 명확한 에러 메시지
- [ ] 적절한 HTTP 상태 코드

```python
# ✅ 좋은 예
if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )
```

---

## ✅ 5. 보안

### 인증/인가
- [ ] 비밀번호 해싱 (bcrypt)
- [ ] JWT 토큰 사용
- [ ] 민감한 엔드포인트 인증 필요

### 데이터 검증
- [ ] Pydantic 스키마 사용
- [ ] 입력 데이터 검증
- [ ] SQL Injection 방지 (ORM 사용)

### 환경 변수
- [ ] 민감한 정보 `.env`에 저장
- [ ] `.env.example` 제공
- [ ] `.env`는 `.gitignore`에 포함

---

## ✅ 6. 테스트

### API 테스트
- [ ] 모든 엔드포인트 테스트
- [ ] 성공 케이스
- [ ] 실패 케이스 (에러 처리)

### 데이터베이스 테스트
- [ ] 마이그레이션 정상 작동
- [ ] 외래키 제약조건 확인
- [ ] 데이터 무결성 확인

---

## ✅ 7. 문서화

### 코드 주석
- [ ] 복잡한 로직에 주석
- [ ] Docstring (함수 설명)
- [ ] TODO, FIXME 표시 (필요시)

### API 문서
- [ ] FastAPI Swagger 자동 생성
- [ ] 엔드포인트 설명
- [ ] 요청/응답 예시

---

## 검수 프로세스

### 1단계: 자동 검사
```bash
# Lint 검사
flake8 app/ --max-line-length=120 --count

# 타입 체크 (선택)
mypy app/ --config-file mypy.ini

# 자동 포맷팅
autopep8 --in-place --aggressive --max-line-length=120 --recursive app/
```

### 2단계: 수동 검토
- 네이밍 규칙 확인
- 외래키 참조 확인
- 에러 처리 확인
- 보안 이슈 확인

### 3단계: 테스트
- API 엔드포인트 테스트
- 데이터베이스 작업 테스트
- 엣지 케이스 테스트

### 4단계: 문서 업데이트
- DEVELOPMENT_STATUS.md 업데이트
- API 문서 확인
- README 업데이트 (필요시)

---

## 체크리스트 사용법

각 개발 단계 완료 후:
1. 이 체크리스트 복사
2. 해당하는 항목 체크
3. 모든 항목 통과 시 다음 단계 진행
4. 문제 발견 시 즉시 수정

---

**마지막 업데이트**: 2025년 10월 29일

