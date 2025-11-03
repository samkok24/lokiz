// API Response Types based on LOKIZ Backend

// ============================================================================
// Common Types
// ============================================================================

export interface PaginationParams {
  limit?: number;
  cursor?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  has_more: boolean;
  next_cursor?: string;
}

// ============================================================================
// User Types
// ============================================================================

export interface UserBasicInfo {
  id: string;
  username: string;
  profile_image?: string;
}

export interface UserProfile extends UserBasicInfo {
  bio?: string;
  follower_count: number;
  following_count: number;
  video_count: number;
  like_count: number;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

// ============================================================================
// Video Types
// ============================================================================

export interface VideoResponse {
  id: string;
  user: UserBasicInfo;
  video_url: string;
  thumbnail_url?: string;
  duration_seconds: number;
  caption?: string;
  view_count: number;
  like_count: number;
  comment_count: number;
  glitch_count: number;
  original_video_id?: string;
  created_at: string;
}

export interface UploadUrlResponse {
  upload_url: string;
  video_id: string;
  video_url: string;
}

export interface CompleteUploadRequest {
  caption?: string;
  is_public?: boolean;
}

// ============================================================================
// AI Types
// ============================================================================

export interface AIJobResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result_url?: string;
  error?: string;
  created_at: string;
  updated_at: string;
}

export interface CaptureFrameRequest {
  video_id: string;
  timestamp: number;
}

export interface I2VRequest {
  image_url: string;
  prompt?: string;
  motion_strength?: number;
}

export interface GlitchAnimateRequest {
  video_id: string;
  start_time: number;
  end_time: number;
  motion_type: 'zoom' | 'rotate' | 'shake' | 'wave';
  intensity?: number;
}

export interface GlitchReplaceRequest {
  video_id: string;
  start_time: number;
  end_time: number;
  replacement_image_url: string;
  prompt?: string;
}

export interface StickerToRealityRequest {
  video_id: string;
  user_image_url: string;
  start_time: number;
  end_time: number;
  prompt?: string;
  is_glitch: boolean;
}

export interface MusicGenerationRequest {
  prompt: string;
  duration?: number;
  genre?: string;
}

// ============================================================================
// Social Types
// ============================================================================

export interface CommentResponse {
  id: string;
  user: UserBasicInfo;
  video_id: string;
  content: string;
  like_count: number;
  created_at: string;
  updated_at: string;
}

export interface CreateCommentRequest {
  content: string;
}

export interface FollowStats {
  follower_count: number;
  following_count: number;
}

// ============================================================================
// Feed Types
// ============================================================================

export interface FeedResponse {
  videos: VideoResponse[];
  total: number;
  page_size: number;
  has_more: boolean;
  next_cursor?: string;
  feed_type: 'for_you' | 'following';
}

// ============================================================================
// Glitch Types
// ============================================================================

export interface GlitchChainResponse {
  glitches: VideoResponse[];
  total: number;
}

export interface SourceVideoResponse {
  source_video: VideoResponse;
}

// ============================================================================
// Notification Types
// ============================================================================

export interface NotificationResponse {
  id: string;
  type: 'like' | 'comment' | 'follow' | 'glitch' | 'system';
  actor?: UserBasicInfo;
  video?: VideoResponse;
  comment?: CommentResponse;
  message?: string;
  is_read: boolean;
  created_at: string;
}

export interface UnreadCountResponse {
  unread_count: number;
}

// ============================================================================
// Search Types
// ============================================================================

export interface SearchUsersResponse {
  users: UserProfile[];
  total: number;
}

export interface SearchVideosResponse {
  videos: VideoResponse[];
  total: number;
}

export interface SearchAllResponse {
  users: UserProfile[];
  videos: VideoResponse[];
  hashtags: string[];
}

// ============================================================================
// Hashtag Types
// ============================================================================

export interface HashtagResponse {
  name: string;
  video_count: number;
  view_count: number;
}

export interface TrendingHashtagsResponse {
  hashtags: HashtagResponse[];
}

export interface HashtagVideosResponse {
  videos: VideoResponse[];
  total: number;
}

// ============================================================================
// Moderation Types
// ============================================================================

export interface BlockRequest {
  blocked_user_id: string;
}

export interface BlockedUserResponse {
  id: string;
  blocked_user: UserBasicInfo;
  created_at: string;
}

export interface BlockListResponse {
  blocks: BlockedUserResponse[];
  total: number;
}

export interface IsBlockedResponse {
  is_blocked: boolean;
}

export interface ReportRequest {
  reported_user_id?: string;
  reported_video_id?: string;
  reported_comment_id?: string;
  report_type: 'spam' | 'harassment' | 'inappropriate' | 'copyright' | 'other';
  reason?: string;
}

export interface ReportResponse {
  id: string;
  report_type: string;
  reason?: string;
  status: 'pending' | 'reviewed' | 'resolved' | 'dismissed';
  created_at: string;
}

export interface ReportListResponse {
  reports: ReportResponse[];
  total: number;
}

// ============================================================================
// Credit Types
// ============================================================================

export interface CreditBalanceResponse {
  balance: number;
  daily_free_credits: number;
  daily_free_credits_claimed_at?: string;
}

export interface ClaimDailyCreditsResponse {
  balance: number;
  claimed_amount: number;
}

export interface CreditHistoryItem {
  id: string;
  amount: number;
  type: 'earn' | 'spend';
  description: string;
  created_at: string;
}

export interface CreditHistoryResponse {
  history: CreditHistoryItem[];
  total: number;
}

// ============================================================================
// Studio Types
// ============================================================================

export interface TimelineResponse {
  video_id: string;
  duration_seconds: number;
  frame_count: number;
  fps: number;
}

export interface FramePreviewResponse {
  frames: string[];  // Array of frame URLs
}

export interface SelectRangeRequest {
  start_time: number;
  end_time: number;
}

// ============================================================================
// Error Types
// ============================================================================

export interface APIError {
  detail: string;
  status_code: number;
}

