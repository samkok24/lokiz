import re
from sqlalchemy.orm import Session
from app.models.hashtag import Hashtag


def extract_hashtags(text: str) -> list[str]:
    """
    Extract hashtags from text
    Returns list of hashtag names (without #)
    """
    if not text:
        return []

    # Find all hashtags (# followed by alphanumeric characters and underscores)
    hashtags = re.findall(r'#(\w+)', text)

    # Remove duplicates and convert to lowercase
    unique_hashtags = list(set([tag.lower() for tag in hashtags]))

    return unique_hashtags


def get_or_create_hashtags(db: Session, hashtag_names: list[str]) -> list[Hashtag]:
    """
    Get existing hashtags or create new ones
    """
    hashtags = []

    for name in hashtag_names:
        # Try to find existing hashtag
        hashtag = db.query(Hashtag).filter(Hashtag.name == name).first()

        if not hashtag:
            # Create new hashtag
            hashtag = Hashtag(name=name)
            db.add(hashtag)
            db.flush()

        hashtags.append(hashtag)

    return hashtags


def update_video_hashtags(db: Session, video, caption: str):
    """
    Update hashtags for a video based on caption
    """
    # Extract hashtags from caption
    hashtag_names = extract_hashtags(caption)

    # Get or create hashtags
    new_hashtags = get_or_create_hashtags(db, hashtag_names)

    # Get current hashtags
    current_hashtags = video.hashtags

    # Find hashtags to remove (old hashtags not in new caption)
    hashtags_to_remove = [h for h in current_hashtags if h not in new_hashtags]

    # Find hashtags to add (new hashtags not in current)
    hashtags_to_add = [h for h in new_hashtags if h not in current_hashtags]

    # Update use_count for removed hashtags
    for hashtag in hashtags_to_remove:
        if hashtag.use_count > 0:
            hashtag.use_count -= 1

    # Update use_count for added hashtags
    for hashtag in hashtags_to_add:
        hashtag.use_count += 1

    # Update video hashtags
    video.hashtags = new_hashtags

    db.commit()
