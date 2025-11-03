from sqlalchemy.orm import Session
from uuid import UUID

from app.models.notification import Notification


def create_notification(
    db: Session,
    user_id: UUID,
    notification_type: str,
    actor_id: UUID,
    target_id: UUID = None
):
    """
    Create a notification

    Args:
        db: Database session
        user_id: User who receives the notification
        notification_type: Type of notification (like, comment, follow, glitch)
        actor_id: User who triggered the notification
        target_id: Target object ID (video_id, comment_id, etc.)
    """
    # Don't create notification if actor is the same as user
    if user_id == actor_id:
        return None

    notification = Notification(
        user_id=user_id,
        type=notification_type,
        actor_id=actor_id,
        target_id=target_id
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification
