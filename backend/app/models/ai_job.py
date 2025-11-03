from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.session import Base


class JobType(str, enum.Enum):
    I2V = "i2v"
    VTV = "vtv"
    COMPOSITING = "compositing"
    MUSIC = "music"


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AIJob(Base):
    __tablename__ = "ai_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_type = Column(SQLEnum(JobType), nullable=False, index=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)
    input_data = Column(JSONB, nullable=False)  # 입력 파라미터 (URL, 프롬프트 등)
    output_url = Column(String(500))  # 결과 비디오/오디오 URL
    credits_used = Column(Integer, nullable=False)
    error_message = Column(Text)
    replicate_id = Column(String(255))  # Replicate API의 prediction ID
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", backref="ai_jobs")
