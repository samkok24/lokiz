import { X } from "lucide-react";
import { useEffect } from "react";
import VideoGrid from "./VideoGrid";

interface HashtagModalProps {
  isOpen: boolean;
  onClose: () => void;
  hashtag: string;
}

// Mock data
const mockHashtagVideos = [
  {
    id: "h1",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Hashtag+1",
    view_count: 23400,
    user: { username: "user1", profile_image: "https://via.placeholder.com/24" },
  },
  {
    id: "h2",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Hashtag+2",
    view_count: 12300,
    user: { username: "user2", profile_image: "https://via.placeholder.com/24" },
  },
  {
    id: "h3",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Hashtag+3",
    view_count: 8900,
    user: { username: "user3", profile_image: "https://via.placeholder.com/24" },
  },
  {
    id: "h4",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Hashtag+4",
    view_count: 5600,
    user: { username: "user4", profile_image: "https://via.placeholder.com/24" },
  },
  {
    id: "h5",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Hashtag+5",
    view_count: 3400,
    user: { username: "user5", profile_image: "https://via.placeholder.com/24" },
  },
  {
    id: "h6",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Hashtag+6",
    view_count: 2100,
    user: { username: "user6", profile_image: "https://via.placeholder.com/24" },
  },
];

export default function HashtagModal({
  isOpen,
  onClose,
  hashtag,
}: HashtagModalProps) {
  // Close on ESC key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      document.addEventListener("keydown", handleEsc);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleEsc);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleVideoClick = (videoId: string) => {
    console.log("Open video:", videoId);
    // TODO: Navigate to video or open in feed
  };

  const formatCount = (count: number) => {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K`;
    }
    return count.toString();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/80"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-5xl h-[90vh] bg-background rounded-lg overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div>
            <h2 className="text-xl font-bold">#{hashtag}</h2>
            <p className="text-sm text-muted-foreground">
              {formatCount(mockHashtagVideos.length * 1000)} 게시물
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-10 h-10 rounded-full hover:bg-muted flex items-center justify-center transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <VideoGrid videos={mockHashtagVideos} onVideoClick={handleVideoClick} />
        </div>
      </div>
    </div>
  );
}

