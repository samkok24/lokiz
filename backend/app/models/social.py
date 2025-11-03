from sqlalchemy import Column, DateTime, ForeignKey, Text, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.session import Base


class Like(Base):
    __tablename__ = "likes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint('user_id', 'video_id', name='unique_user_video_like'),)

    # Relationships
    user = relationship("User", backref="likes")
    video = relationship("Video", backref="likes")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    like_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="comments")
    video = relationship("Video", backref="comments")


class Follow(Base):
    __tablename__ = "follows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    following_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint('follower_id', 'following_id', name='unique_follower_following'),)

    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], backref="following")
    following = relationship("User", foreign_keys=[following_id], backref="followers")


class VideoGlitch(Base):
    __tablename__ = "video_glitches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_video_id = Column(
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    glitch_video_id = Column(
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    glitch_type = Column(Text, nullable=False)  # 'animate' or 'replace'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint('glitch_video_id', name='unique_glitch_video'),)

    # Relationships
    original_video = relationship("Video", foreign_keys=[original_video_id], backref="glitches_created")
    glitch_video = relationship("Video", foreign_keys=[glitch_video_id], backref="glitch_source")


class CommentLike(Base):
    __tablename__ = "comment_likes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_like'),)

    # Relationships
    user = relationship("User", backref="comment_likes")
    comment = relationship("Comment", backref="comment_likes")


class VideoShare(Base):
    __tablename__ = "video_shares"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    share_platform = Column(Text, nullable=True)  # 'twitter', 'facebook', 'copy_link', etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="video_shares")
    video = relationship("Video", backref="video_shares")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (UniqueConstraint('user_id', 'video_id', name='unique_user_video_bookmark'),)

    # Relationships
    user = relationship("User", backref="bookmarks")
    video = relationship("Video", backref="bookmarks")


class Block(Base):
    """User blocking system"""
    __tablename__ = "blocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    blocker_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    blocked_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint('blocker_id', 'blocked_id', name='unique_blocker_blocked'),)

    # Relationships
    blocker = relationship("User", foreign_keys=[blocker_id], backref="blocking")
    blocked = relationship("User", foreign_keys=[blocked_id], backref="blocked_by")


class Report(Base):
    """Content reporting system"""
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Reported content (one of these will be set)
    reported_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    reported_video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=True, index=True)
    reported_comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Report details
    report_type = Column(Text, nullable=False)  # 'spam', 'harassment', 'inappropriate', 'copyright', 'other'
    reason = Column(Text, nullable=True)  # Optional detailed reason
    status = Column(Text, default="pending", nullable=False)  # 'pending', 'reviewed', 'resolved', 'dismissed'
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id], backref="reports_made")
    reported_user = relationship("User", foreign_keys=[reported_user_id], backref="reports_received")
    reported_video = relationship("Video", foreign_keys=[reported_video_id], backref="reports")
    reported_comment = relationship("Comment", foreign_keys=[reported_comment_id], backref="reports")
