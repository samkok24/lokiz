import { X, Heart, MessageCircle, Bookmark, Share2 } from "lucide-react";
import { useState, useRef, useEffect } from "react";

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

// Mock comments
const mockComments = [
  {
    id: "1",
    user: { username: "김치사발면마요", profile_image: "https://via.placeholder.com/40" },
    text: "레즈 마이온즈를",
    time: "5시간 전",
    likes: 1,
  },
  {
    id: "2",
    user: { username: "연제윤", profile_image: "https://via.placeholder.com/40" },
    text: "크리에이터 켓츠를 그래이!",
    time: "5시간 전",
    likes: 0,
    replies: [
      {
        id: "2-1",
        user: { username: "연제윤", profile_image: "https://via.placeholder.com/40" },
        text: "크리에이터 ❤️😭",
        time: "5시간 전",
        likes: 0,
      },
    ],
  },
  {
    id: "3",
    user: { username: "플가이", profile_image: "https://via.placeholder.com/40" },
    text: "이쁘다",
    time: "3시간 전",
    likes: 1,
  },
];

export default function VideoDetailModal({ isOpen, onClose, video }: VideoDetailModalProps) {
  const [isPlaying, setIsPlaying] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const [isLiked, setIsLiked] = useState(video.is_liked);
  const [comment, setComment] = useState("");
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (isOpen && videoRef.current) {
      videoRef.current.play();
    }
  }, [isOpen]);

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

  return (
    <div className="fixed inset-0 z-50 bg-black/95">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-6 py-4">
        <button
          onClick={onClose}
          className="p-2 hover:bg-white/10 rounded-full transition-colors"
        >
          <X className="w-6 h-6 text-white" />
        </button>
        <div className="flex-1 max-w-md mx-auto">
          <input
            type="text"
            placeholder="관련 콘텐츠를 찾아보세요"
            className="w-full px-4 py-2 bg-[#2a2a2a] text-white rounded-full focus:outline-none focus:ring-2 focus:ring-[#C9F227]"
          />
        </div>
        <button className="p-2 hover:bg-white/10 rounded-full transition-colors">
          <span className="text-white text-2xl">⋯</span>
        </button>
      </div>

      {/* Content */}
      <div className="flex items-center justify-center h-full pt-20 pb-6">
        <div className="flex gap-6 max-w-7xl w-full px-6">
          {/* Left: Video */}
          <div className="flex-shrink-0" style={{ width: "56.25%", maxWidth: "600px" }}>
            <div className="relative bg-black rounded-lg overflow-hidden" style={{ aspectRatio: "9/16" }}>
              <video
                ref={videoRef}
                src={video.url}
                className="w-full h-full object-contain"
                loop
                onClick={handlePlayPause}
              />
              
              {/* Video controls */}
              <button
                onClick={handleMute}
                className="absolute bottom-4 right-4 p-2 bg-black/50 rounded-full hover:bg-black/70 transition-colors"
              >
                <span className="text-white text-xl">{isMuted ? "🔇" : "🔊"}</span>
              </button>
            </div>
          </div>

          {/* Right: Info & Comments */}
          <div className="flex-1 flex flex-col max-w-md">
            {/* User info */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <img
                  src={video.user.profile_image}
                  alt={video.user.username}
                  className="w-10 h-10 rounded-full"
                />
                <div>
                  <div className="text-white font-semibold">{video.user.username}</div>
                  <div className="text-gray-400 text-sm">전재윤 · 8시간 전</div>
                </div>
              </div>
              <button className="px-6 py-2 bg-[#FE2C55] text-white font-semibold rounded hover:bg-[#FE2C55]/90 transition-colors">
                팔로우
              </button>
            </div>

            {/* Caption */}
            <div className="text-white mb-4">
              <p>{video.caption}</p>
              <p className="text-gray-400 text-sm mt-2">
                🎵 오리지널 사운드 - 선재윤
              </p>
            </div>

            {/* Stats */}
            <div className="flex items-center gap-6 mb-6 pb-6 border-b border-gray-800">
              <button
                onClick={() => setIsLiked(!isLiked)}
                className="flex items-center gap-2 text-white hover:text-[#C9F227] transition-colors"
              >
                <Heart className={`w-6 h-6 ${isLiked ? "fill-[#FE2C55] text-[#FE2C55]" : ""}`} />
                <span>{formatNumber(video.like_count + (isLiked ? 1 : 0))}</span>
              </button>
              <button className="flex items-center gap-2 text-white hover:text-[#C9F227] transition-colors">
                <MessageCircle className="w-6 h-6" />
                <span>{video.comment_count}</span>
              </button>
              <button className="flex items-center gap-2 text-white hover:text-[#C9F227] transition-colors">
                <Bookmark className="w-6 h-6" />
                <span>352</span>
              </button>
            </div>

            {/* Comments */}
            <div className="flex-1 overflow-y-auto mb-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white font-semibold">댓글 ({video.comment_count})</h3>
                <button className="text-gray-400 text-sm">크리에이터 동영상</button>
              </div>

              <div className="space-y-4">
                {mockComments.map((comment) => (
                  <div key={comment.id}>
                    <div className="flex gap-3">
                      <img
                        src={comment.user.profile_image}
                        alt={comment.user.username}
                        className="w-10 h-10 rounded-full flex-shrink-0"
                      />
                      <div className="flex-1">
                        <div className="text-white">
                          <span className="font-semibold">{comment.user.username}</span>
                          <span className="ml-2">{comment.text}</span>
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-gray-400 text-sm">
                          <span>{comment.time}</span>
                          <button className="hover:text-white">답글</button>
                        </div>
                      </div>
                      <button className="flex flex-col items-center gap-1 text-gray-400 hover:text-white">
                        <Heart className="w-4 h-4" />
                        {comment.likes > 0 && <span className="text-xs">{comment.likes}</span>}
                      </button>
                    </div>

                    {/* Replies */}
                    {comment.replies?.map((reply) => (
                      <div key={reply.id} className="flex gap-3 ml-12 mt-3">
                        <img
                          src={reply.user.profile_image}
                          alt={reply.user.username}
                          className="w-8 h-8 rounded-full flex-shrink-0"
                        />
                        <div className="flex-1">
                          <div className="text-white">
                            <span className="font-semibold">{reply.user.username}</span>
                            <span className="ml-2">{reply.text}</span>
                          </div>
                          <div className="flex items-center gap-4 mt-1 text-gray-400 text-sm">
                            <span>{reply.time}</span>
                            <button className="hover:text-white">답글</button>
                          </div>
                        </div>
                        <button className="flex flex-col items-center gap-1 text-gray-400 hover:text-white">
                          <Heart className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>

            {/* Comment input */}
            <div className="flex items-center gap-3 pt-4 border-t border-gray-800">
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
      </div>
    </div>
  );
}

