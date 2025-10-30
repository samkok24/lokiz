import { Play } from "lucide-react";

interface VideoGridProps {
  videos: {
    id: string;
    thumbnail_url: string;
    view_count: number;
    user: {
      username: string;
      profile_image: string | null;
    };
  }[];
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
    <div className="grid grid-cols-3 md:grid-cols-4 gap-1">
      {videos.map((video) => (
        <div
          key={video.id}
          className="relative aspect-[9/16] bg-muted cursor-pointer group overflow-hidden"
          onClick={() => onVideoClick(video.id)}
        >
          {/* Thumbnail */}
          <img
            src={video.thumbnail_url}
            alt="Video thumbnail"
            className="w-full h-full object-cover"
          />

          {/* Hover Overlay */}
          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />

          {/* View Count */}
          <div className="absolute bottom-2 left-2 flex items-center gap-1 text-white text-sm font-semibold">
            <Play className="w-4 h-4 fill-white" />
            <span>{formatCount(video.view_count)}</span>
          </div>

          {/* User Info (on hover) */}
          <div className="absolute top-2 left-2 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <img
              src={video.user.profile_image || "https://via.placeholder.com/24"}
              alt={video.user.username}
              className="w-6 h-6 rounded-full border border-white"
            />
            <span className="text-white text-xs font-semibold">
              @{video.user.username}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

