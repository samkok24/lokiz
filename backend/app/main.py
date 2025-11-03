from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, video, ai, glitch, studio, image, like, comment, follow, user, notification, search, hashtag, credit, share, bookmark, moderation, feed
from app.core.config import settings

app = FastAPI(
    title="LOKIZ API",
    description="AI-powered social video glitch platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/v1")
app.include_router(video.router, prefix="/v1")
app.include_router(ai.router, prefix="/v1")
app.include_router(glitch.router, prefix="/v1")
app.include_router(studio.router, prefix="/v1")
app.include_router(image.router, prefix="/v1")
app.include_router(like.router, prefix="/v1")
app.include_router(comment.router, prefix="/v1")
app.include_router(follow.router, prefix="/v1")
app.include_router(user.router, prefix="/v1")
app.include_router(notification.router, prefix="/v1")
app.include_router(search.router, prefix="/v1")
app.include_router(hashtag.router, prefix="/v1")
app.include_router(credit.router, prefix="/v1")
app.include_router(share.router, prefix="/v1")
app.include_router(bookmark.router, prefix="/v1")
app.include_router(moderation.router, prefix="/v1")
app.include_router(feed.router, prefix="/v1")


@app.get("/")
def root():
    return {
        "message": "Welcome to LOKIZ API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
