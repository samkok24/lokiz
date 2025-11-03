import { useState, useRef, useEffect } from "react";
import { Heart, MessageCircle, Zap, Share2, Play, Volume2, VolumeX } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";
import type { Video } from "@shared/types";

interface VideoPlayerProps {
  video: Video;
  isActive: boolean;
  onLike: () => void;
  onComment: () => void;
  onGlitch: () => void;
  onShare: () => void;
}

export default function VideoPlayer({
  video,
  isActive,
  onLike,
  onComment,
  onGlitch,
  onShare,
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const [progress, setProgress] = useState(0);
  const [, setLocation] = useLocation();

  // Auto play/pause based on isActive
  useEffect(() => {
    if (!videoRef.current) return;

    if (isActive) {
      videoRef.current.play().catch(() => {
        // Autoplay failed, user interaction required
      });
      setIsPlaying(true);
    } else {
      videoRef.current.pause();
      setIsPlaying(false);
    }
  }, [isActive]);

  // Update progress
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      const progress = (video.currentTime / video.duration) * 100;
      setProgress(progress);
    };

    video.addEventListener("timeupdate", handleTimeUpdate);
    return () => video.removeEventListener("timeupdate", handleTimeUpdate);
  }, []);

  const togglePlay = () => {
    if (!videoRef.current) return;

    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const formatCount = (count: number) => {
    if (count >= 1000000) {
      return `${(count / 1000000).toFixed(1)}M`;
    }
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K`;
    }
    return count.toString();
  };

  return (
    <div className="relative w-full h-screen flex items-center justify-center bg-black">
      {/* Center: Video Container */}
      <div className="relative w-full md:w-[56.25%] max-w-full md:max-w-[600px]">
        <div className="relative bg-black rounded-lg overflow-hidden" style={{ aspectRatio: "9/16" }}>
          {/* Video */}
          <video
            ref={videoRef}
            src={video.videoUrl}
            poster={video.thumbnailUrl}
            className="w-full h-full object-contain cursor-pointer"
            loop
            playsInline
            muted={isMuted}
            onClick={togglePlay}
          />

          {/* Play Icon Overlay */}
          {!isPlaying && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="w-20 h-20 rounded-full bg-black/50 flex items-center justify-center">
                <Play className="w-10 h-10 text-white fill-white ml-1" />
              </div>
            </div>
          )}

          {/* Progress Bar */}
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-white/20">
            <div
              className="h-full bg-primary transition-all duration-100"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Bottom Info (Overlay) */}
          <div className="absolute left-4 bottom-4 right-4 text-white">
            <div className="mb-2">
              <span
                onClick={() => setLocation(`/profile/${video.user.id}`)}
                className="font-semibold cursor-pointer hover:underline"
              >
                {video.user.username}
              </span>
            </div>
            <p className="text-sm line-clamp-2">{video.caption}</p>
          </div>
        </div>
      </div>

      {/* Right Side Actions (Outside Video) */}
      <div className="absolute right-4 md:right-8 bottom-28 md:bottom-24 flex flex-col items-center gap-4 md:gap-6">
        {/* Profile */}
        <div className="relative">
          <img
            src={video.user.avatar || "https://via.placeholder.com/48"}
            alt={video.user.username}
            onClick={() => setLocation(`/profile/${video.user.id}`)}
            className="w-10 h-10 md:w-12 md:h-12 rounded-full border-2 border-white cursor-pointer"
          />
          <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-5 h-5 md:w-6 md:h-6 rounded-full bg-primary flex items-center justify-center cursor-pointer">
            <span className="text-black text-lg font-bold">+</span>
          </div>
        </div>

        {/* Like */}
        <button
          onClick={onLike}
          className="flex flex-col items-center gap-1 text-white hover:scale-110 transition-transform"
        >
          <Heart
            className={`w-7 h-7 md:w-8 md:h-8 ${video.isLiked ? "fill-primary text-primary" : ""}`}
          />
          <span className="text-xs font-semibold">{formatCount(video.likes)}</span>
        </button>

        {/* Comment */}
        <button
          onClick={onComment}
          className="flex flex-col items-center gap-1 text-white hover:scale-110 transition-transform"
        >
          <MessageCircle className="w-7 h-7 md:w-8 md:h-8" />
          <span className="text-xs font-semibold">{formatCount(video.comments)}</span>
        </button>

        {/* Glitch */}
        <button
          onClick={onGlitch}
          className="flex flex-col items-center gap-1 text-white hover:scale-110 transition-transform"
        >
          <Zap className="w-7 h-7 md:w-8 md:h-8" />
          <span className="text-xs font-semibold">{formatCount(video.bookmarks || 0)}</span>
        </button>

        {/* Share */}
        <button
          onClick={onShare}
          className="flex flex-col items-center gap-1 text-white hover:scale-110 transition-transform"
        >
          <Share2 className="w-7 h-7 md:w-8 md:h-8" />
          <span className="text-xs font-semibold">공유</span>
        </button>
      </div>

      {/* Mute Button */}
      <button
        onClick={toggleMute}
        className="absolute top-4 right-4 w-10 h-10 rounded-full bg-black/50 flex items-center justify-center text-white hover:bg-black/70 transition-colors"
      >
        {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
      </button>
    </div>
  );
}

