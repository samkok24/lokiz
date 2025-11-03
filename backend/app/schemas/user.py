from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    """Request to update user profile"""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    display_name: Optional[str]
    bio: Optional[str]
    profile_image_url: Optional[str]
    credits: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserBasicInfo(BaseModel):
    """Basic user info for embedding in other responses"""
    id: UUID
    username: str
    display_name: Optional[str]
    profile_image_url: Optional[str]

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """User profile with statistics"""
    id: UUID
    username: str
    display_name: Optional[str]
    bio: Optional[str]
    profile_image_url: Optional[str]
    follower_count: int = 0
    following_count: int = 0
    video_count: int = 0
    total_likes: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
