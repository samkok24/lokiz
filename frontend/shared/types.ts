/**
 * Shared type definitions for LOKIZ
 * Single Source of Truth for all data types
 */

export interface User {
  id: string;
  username: string;
  nickname: string;
  avatar: string;
  bio?: string;
  followersCount?: number;
  followingCount?: number;
  likesCount?: number;
  isFollowing?: boolean;
}

export interface Video {
  id: string;
  userId: string;
  user: User;
  videoUrl: string;
  thumbnailUrl: string;
  caption: string;
  hashtags?: string[];
  musicName?: string;
  likes: number;
  comments: number;
  bookmarks?: number;
  shares?: number;
  views: number;
  createdAt: string;
  isLiked?: boolean;
  isBookmarked?: boolean;
  recentlyWatched?: boolean;
}

export interface Comment {
  id: string;
  videoId: string;
  userId: string;
  user: User;
  content: string;
  likes: number;
  createdAt: string;
  isLiked?: boolean;
}

export interface Message {
  id: string;
  senderId: string;
  receiverId: string;
  content: string;
  createdAt: string;
  isRead?: boolean;
}

export interface Conversation {
  id: string;
  user: User;
  lastMessage: string;
  lastMessageTime: string;
  unreadCount?: number;
}

export interface Notification {
  id: string;
  type: 'like' | 'comment' | 'follow' | 'message' | 'system';
  user?: User;
  video?: Video;
  message: string;
  createdAt: string;
  isRead: boolean;
}

export interface GlitchEffect {
  id: string;
  name: string;
  thumbnail: string;
  description?: string;
}

