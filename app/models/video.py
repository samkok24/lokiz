from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.session import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    caption = Column(Text)
    video_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=False)
    duration_seconds = Column(Integer, nullable=False)

    # Status and visibility
    status = Column(String(20), nullable=False, default="completed", index=True)
    is_public = Column(Boolean, nullable=False, default=True, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Optional metadata
    title = Column(String(200), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    s3_key = Column(String(500), nullable=True)

    # Counters
    view_count = Column(Integer, default=0, nullable=False)
    like_count = Column(Integer, default=0, nullable=False)
    comment_count = Column(Integer, default=0, nullable=False)
    glitch_count = Column(Integer, default=0, nullable=False)
    share_count = Column(Integer, default=0, nullable=False)
    original_video_id = Column(
        UUID(
            as_uuid=True),
        ForeignKey(
            "videos.id",
            ondelete="SET NULL"),
        nullable=True,
        index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="videos")
    original_video = relationship("Video", remote_side=[id], backref="glitches")
    hashtags = relationship("Hashtag", secondary="video_hashtags", back_populates="videos")
