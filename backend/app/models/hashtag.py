from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.db.session import Base


class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    use_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    videos = relationship("Video", secondary="video_hashtags", back_populates="hashtags")


# Association table for many-to-many relationship
video_hashtags = Table(
    'video_hashtags',
    Base.metadata,
    Column('video_id', UUID(as_uuid=True), ForeignKey('videos.id'), primary_key=True),
    Column('hashtag_id', UUID(as_uuid=True), ForeignKey('hashtags.id'), primary_key=True)
)
