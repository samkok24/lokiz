import { Play } from "lucide-react";
import type { Video } from "@shared/types";

interface VideoGridProps {
  videos: Video[];
  onVideoClick: (videoId: string) => void;
}

export default function VideoGrid({ videos, onVideoClick }: VideoGridProps) {
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
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-1">
      {videos.map((video) => (
        <div
          key={video.id}
          className="relative aspect-[3/4] bg-muted cursor-pointer group overflow-hidden rounded-lg"
          onClick={() => onVideoClick(video.id)}
        >
          {/* Thumbnail */}
          <img
            src={video.thumbnailUrl}
            alt="Video thumbnail"
            className="w-full h-full object-cover"
          />

          {/* Hover Overlay */}
          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />

          {/* View Count */}
          <div className="absolute bottom-1 md:bottom-2 left-1 md:left-2 flex items-center gap-0.5 md:gap-1 text-white text-xs md:text-sm font-semibold">
            <Play className="w-3 h-3 md:w-4 md:h-4 fill-white" />
            <span>{formatCount(video.views)}</span>
          </div>

          {/* User Info (on hover) */}
          <div className="absolute top-1 md:top-2 left-1 md:left-2 flex items-center gap-1 md:gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <img
              src={video.user.avatar || "https://via.placeholder.com/24"}
              alt={video.user.username}
              className="w-5 h-5 md:w-6 md:h-6 rounded-full border border-white"
            />
            <span className="text-white text-[10px] md:text-xs font-semibold">
              @{video.user.username}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

