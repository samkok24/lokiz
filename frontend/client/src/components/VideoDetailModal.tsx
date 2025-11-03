import { X, Heart, MessageCircle, Bookmark, ChevronUp, ChevronDown, Copy } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { mockComments } from "@shared/mockData";

interface VideoDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  video: {
    id: string;
    url: string;
    user: {
      id: string;
      username: string;
      profile_image: string;
    };
    caption: string;
    view_count: number;
    like_count: number;
    comment_count: number;
    is_liked: boolean;
  };
}

// Mock comments imported from shared/mockData.ts

export default function VideoDetailModal({ isOpen, onClose, video }: VideoDetailModalProps) {
  const [isPlaying, setIsPlaying] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const [isLiked, setIsLiked] = useState(video.is_liked);
  const [comment, setComment] = useState("");
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [activeTab, setActiveTab] = useState<"comments" | "creator">("comments");
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (isOpen && videoRef.current) {
      videoRef.current.play();
    }
  }, [isOpen]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => setCurrentTime(video.currentTime);
    const handleLoadedMetadata = () => setDuration(video.duration);

    video.addEventListener("timeupdate", handleTimeUpdate);
    video.addEventListener("loadedmetadata", handleLoadedMetadata);

    return () => {
      video.removeEventListener("timeupdate", handleTimeUpdate);
      video.removeEventListener("loadedmetadata", handleLoadedMetadata);
    };
  }, []);

  if (!isOpen) return null;

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="fixed inset-0 z-50 bg-black flex">
      {/* Close button */}
      <button
        onClick={onClose}
        className="absolute top-6 left-6 z-20 p-2 hover:bg-white/10 rounded-full transition-colors"
      >
        <X className="w-6 h-6 text-white" />
      </button>

      {/* Left: Video Section */}
      <div className="flex-1 relative flex items-center justify-center">
        {/* Search bar overlay */}
        <div className="absolute top-6 left-1/2 -translate-x-1/2 z-10 w-full max-w-md px-4">
          <div className="relative">
            <input
              type="text"
              placeholder="관련 콘텐츠를 찾아보세요"
              className="w-full px-4 py-2 bg-white/10 backdrop-blur-sm text-white rounded-full border border-white/20 focus:outline-none focus:ring-2 focus:ring-white/30 placeholder:text-white/60"
            />
            <button className="absolute right-3 top-1/2 -translate-y-1/2 text-white/60">
              🔍
            </button>
          </div>
        </div>

        {/* More button */}
        <button className="absolute top-6 right-6 z-10 p-2 hover:bg-white/10 rounded-full transition-colors">
          <span className="text-white text-2xl">⋯</span>
        </button>

        {/* Video */}
        <div className="relative" style={{ width: "56.25%", maxWidth: "600px" }}>
          <div className="relative bg-black rounded-lg overflow-hidden" style={{ aspectRatio: "9/16" }}>
            <video
              ref={videoRef}
              src={video.url}
              className="w-full h-full object-contain"
              loop
              onClick={handlePlayPause}
            />

            {/* Progress bar */}
            <div className="absolute bottom-0 left-0 right-0 px-4 pb-4">
              <div className="relative h-1 bg-white/30 rounded-full overflow-hidden">
                <div
                  className="absolute top-0 left-0 h-full bg-white transition-all duration-100"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <div className="flex justify-end mt-1">
                <span className="text-white text-xs">
                  {formatTime(currentTime)}/{formatTime(duration)}
                </span>
              </div>
            </div>
          </div>

          {/* Navigation buttons */}
          <button className="absolute top-1/2 -translate-y-1/2 -left-16 p-3 bg-white/10 hover:bg-white/20 rounded-full transition-colors">
            <ChevronUp className="w-6 h-6 text-white" />
          </button>
          <button className="absolute top-1/2 -translate-y-1/2 -right-16 p-3 bg-white/10 hover:bg-white/20 rounded-full transition-colors">
            <ChevronDown className="w-6 h-6 text-white" />
          </button>
        </div>

        {/* Mute button */}
        <button
          onClick={handleMute}
          className="absolute bottom-6 left-6 p-3 bg-white/10 hover:bg-white/20 rounded-full transition-colors"
        >
          <span className="text-white text-xl">{isMuted ? "🔇" : "🔊"}</span>
        </button>
      </div>

      {/* Right: Info Panel */}
      <div className="w-[400px] bg-black flex flex-col">
        {/* User info */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <img
              src={video.user.profile_image}
              alt={video.user.username}
              className="w-10 h-10 rounded-full"
            />
            <div>
              <div className="text-white font-semibold">{video.user.username}</div>
              <div className="text-gray-400 text-sm">전재윤 · 10-18</div>
            </div>
          </div>
          <button className="px-6 py-2 bg-[#FE2C55] text-white font-semibold rounded hover:bg-[#FE2C55]/90 transition-colors">
            팔로우
          </button>
        </div>

        {/* Caption */}
        <div className="p-4 border-b border-gray-800">
          <p className="text-white mb-2">{video.caption}</p>
          <p className="text-gray-400 text-sm">🎵 오리지널 사운드 - 연재윤</p>
        </div>

        {/* Stats & Actions */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsLiked(!isLiked)}
              className="flex items-center gap-2 text-white hover:text-[#C9F227] transition-colors"
            >
              <Heart className={`w-6 h-6 ${isLiked ? "fill-[#FE2C55] text-[#FE2C55]" : ""}`} />
              <span className="text-sm">{formatNumber(video.like_count + (isLiked ? 1 : 0))}</span>
            </button>
            <button className="flex items-center gap-2 text-white hover:text-[#C9F227] transition-colors">
              <MessageCircle className="w-6 h-6" />
              <span className="text-sm">{video.comment_count}</span>
            </button>
            <button className="flex items-center gap-2 text-white hover:text-[#C9F227] transition-colors">
              <Bookmark className="w-6 h-6" />
              <span className="text-sm">5126</span>
            </button>
          </div>
          <div className="flex items-center gap-2">
            {["💰", "📋", "❤️", "🔗", "👍", "📘", "📤"].map((icon, i) => (
              <button
                key={i}
                className="w-8 h-8 flex items-center justify-center hover:bg-white/10 rounded-full transition-colors"
              >
                <span className="text-lg">{icon}</span>
              </button>
            ))}
          </div>
        </div>

        {/* URL copy */}
        <div className="px-4 py-3 border-b border-gray-800">
          <div className="flex items-center gap-2 bg-[#1a1a1a] rounded px-3 py-2">
            <input
              type="text"
              value={`https://www.tiktok.com/@${video.user.username}/video/${video.id}`}
              readOnly
              className="flex-1 bg-transparent text-gray-400 text-sm focus:outline-none"
            />
            <button className="text-white hover:text-[#C9F227] transition-colors">
              링크 복사
            </button>
          </div>
        </div>

        {/* Comments tabs */}
        <div className="flex items-center border-b border-gray-800">
          <button
            onClick={() => setActiveTab("comments")}
            className={`flex-1 px-4 py-3 text-sm font-semibold ${
              activeTab === "comments"
                ? "text-white border-b-2 border-white"
                : "text-gray-400"
            }`}
          >
            댓글 ({video.comment_count})
          </button>
          <button
            onClick={() => setActiveTab("creator")}
            className={`flex-1 px-4 py-3 text-sm font-semibold ${
              activeTab === "creator"
                ? "text-white border-b-2 border-white"
                : "text-gray-400"
            }`}
          >
            크리에이터 동영상
          </button>
        </div>

        {/* Comments list */}
        <div className="flex-1 overflow-y-auto px-4 py-4">
          <div className="space-y-4">
            {mockComments.map((comment) => (
              <div key={comment.id} className="flex gap-3">
                <img
                  src={comment.user.avatar}
                  alt={comment.user.username}
                  className="w-10 h-10 rounded-full flex-shrink-0"
                />
                <div className="flex-1">
                  <div className="text-white">
                    <span className="font-semibold">{comment.user.username}</span>
                  </div>
                  <div className="text-white mt-1">{comment.content}</div>
                  <div className="flex items-center gap-4 mt-2 text-gray-400 text-sm">
                    <span>{new Date(comment.createdAt).toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric' })}</span>
                    <button className="hover:text-white">답글</button>
                  </div>
                </div>
                <button className="flex flex-col items-center gap-1 text-gray-400 hover:text-white">
                  <Heart className="w-4 h-4" />
                  {comment.likes > 0 && <span className="text-xs">{comment.likes}</span>}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Comment input */}
        <div className="flex items-center gap-3 px-4 py-3 border-t border-gray-800">
          <button className="p-2 hover:bg-white/10 rounded-full transition-colors">
            <span className="text-xl">📋</span>
          </button>
          <button
            onClick={handleMute}
            className="p-2 hover:bg-white/10 rounded-full transition-colors"
          >
            <span className="text-xl">{isMuted ? "🔇" : "🔊"}</span>
          </button>
          <input
            type="text"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="댓글을 달 위치가 해주세요..."
            className="flex-1 px-4 py-2 bg-transparent text-white focus:outline-none placeholder:text-gray-500"
          />
          <button className="text-gray-400 hover:text-white">😊</button>
          <button className="text-gray-400 hover:text-white">😀</button>
          <button
            disabled={!comment.trim()}
            className="text-[#C9F227] font-semibold disabled:text-gray-600 disabled:cursor-not-allowed"
          >
            게시
          </button>
        </div>
      </div>
    </div>
  );
}

