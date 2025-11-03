/**
 * Shared mock data for LOKIZ
 * Single Source of Truth for all mock data
 */

import type { User, Video, Comment, Conversation, Notification, GlitchEffect } from './types';

// Mock Users
export const mockUsers: User[] = [
  {
    id: "user1",
    username: "user1",
    nickname: "사용자1",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=user1",
    bio: "AI 글리치 아티스트 🎨",
    followersCount: 12300,
    followingCount: 169,
    likesCount: 456000,
  },
  {
    id: "user2",
    username: "user2",
    nickname: "사용자2",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=user2",
    bio: "Creative video maker ✨",
    followersCount: 45600,
    followingCount: 234,
    likesCount: 789000,
  },
  {
    id: "user3",
    username: "user3",
    nickname: "사용자3",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=user3",
    bio: "Glitch enthusiast 🌈",
    followersCount: 78900,
    followingCount: 345,
    likesCount: 1234000,
  },
];

// Mock Videos
export const mockVideos: Video[] = [
  {
    id: "1",
    userId: "user1",
    user: mockUsers[0],
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    thumbnailUrl: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&h=600&fit=crop",
    caption: "Amazing video! #lokiz #glitch #ai",
    hashtags: ["lokiz", "glitch", "ai"],
    musicName: "오리지널 사운드 - user1",
    likes: 12300,
    comments: 456,
    bookmarks: 89,
    shares: 234,
    views: 123000,
    createdAt: "2024-01-15T10:30:00Z",
    isLiked: false,
    isBookmarked: false,
  },
  {
    id: "2",
    userId: "user2",
    user: mockUsers[1],
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    thumbnailUrl: "https://images.unsplash.com/photo-1618556450994-a6a128ef0d9d?w=400&h=600&fit=crop",
    caption: "Check this out! #trending",
    hashtags: ["trending"],
    musicName: "오리지널 사운드 - user2",
    likes: 45600,
    comments: 789,
    bookmarks: 123,
    shares: 567,
    views: 456000,
    createdAt: "2024-01-14T15:20:00Z",
    isLiked: true,
    isBookmarked: false,
    recentlyWatched: true,
  },
  {
    id: "3",
    userId: "user3",
    user: mockUsers[2],
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    thumbnailUrl: "https://images.unsplash.com/photo-1618005198919-d3d4b5a92ead?w=400&h=600&fit=crop",
    caption: "Epic moment! #viral",
    hashtags: ["viral"],
    musicName: "오리지널 사운드 - user3",
    likes: 78900,
    comments: 1234,
    bookmarks: 456,
    shares: 890,
    views: 789000,
    createdAt: "2024-01-13T09:45:00Z",
    isLiked: false,
    isBookmarked: true,
  },
];

// Mock Comments
export const mockComments: Comment[] = [
  {
    id: "c1",
    videoId: "1",
    userId: "user2",
    user: mockUsers[1],
    content: "정말 멋진 영상이에요! 👍",
    likes: 45,
    createdAt: "2024-01-15T11:00:00Z",
    isLiked: false,
  },
  {
    id: "c2",
    videoId: "1",
    userId: "user3",
    user: mockUsers[2],
    content: "어떤 효과를 사용하셨나요?",
    likes: 23,
    createdAt: "2024-01-15T11:30:00Z",
    isLiked: true,
  },
];

// Mock Conversations
export const mockConversations: Conversation[] = [
  {
    id: "conv1",
    user: mockUsers[0],
    lastMessage: "안녕하세요!",
    lastMessageTime: "13:32",
    unreadCount: 2,
  },
  {
    id: "conv2",
    user: mockUsers[1],
    lastMessage: "좋은 영상 감사합니다",
    lastMessageTime: "13:31",
    unreadCount: 0,
  },
];

// Mock Notifications
export const mockNotifications: Notification[] = [
  {
    id: "n1",
    type: "like",
    user: mockUsers[1],
    video: mockVideos[0],
    message: "님이 회원님의 동영상을 좋아합니다",
    createdAt: "5분 전",
    isRead: false,
  },
  {
    id: "n2",
    type: "comment",
    user: mockUsers[2],
    video: mockVideos[0],
    message: "님이 댓글을 남겼습니다: \"정말 멋져요!\"",
    createdAt: "10분 전",
    isRead: false,
  },
  {
    id: "n3",
    type: "follow",
    user: mockUsers[0],
    message: "님이 회원님을 팔로우하기 시작했습니다",
    createdAt: "1시간 전",
    isRead: true,
  },
  {
    id: "n4",
    type: "message",
    user: mockUsers[1],
    message: "님이 메시지를 보냈습니다",
    createdAt: "2시간 전",
    isRead: true,
  },
  {
    id: "n5",
    type: "system",
    message: "새로운 AI 글리치 효과가 추가되었습니다!",
    createdAt: "1일 전",
    isRead: true,
  },
];

// Mock Glitch Effects
export const mockGlitchEffects: GlitchEffect[] = [
  {
    id: "effect1",
    name: "VHS",
    thumbnail: "https://via.placeholder.com/100?text=VHS",
    description: "레트로 VHS 효과",
  },
  {
    id: "effect2",
    name: "Pixel",
    thumbnail: "https://via.placeholder.com/100?text=Pixel",
    description: "픽셀 아트 효과",
  },
  {
    id: "effect3",
    name: "Glitch",
    thumbnail: "https://via.placeholder.com/100?text=Glitch",
    description: "디지털 글리치 효과",
  },
  {
    id: "effect4",
    name: "Chromatic",
    thumbnail: "https://via.placeholder.com/100?text=Chromatic",
    description: "색수차 효과",
  },
];

// Helper functions
export function getUserById(id: string): User | undefined {
  return mockUsers.find(user => user.id === id);
}

export function getVideoById(id: string): Video | undefined {
  return mockVideos.find(video => video.id === id);
}

export function getCommentsByVideoId(videoId: string): Comment[] {
  return mockComments.filter(comment => comment.videoId === videoId);
}

