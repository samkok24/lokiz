import { X } from "lucide-react";
import { useEffect } from "react";
import VideoGrid from "./VideoGrid";

interface GlitchModalProps {
  isOpen: boolean;
  onClose: () => void;
  videoId: string;
  originalUser: string;
}

// Mock data
const mockGlitchVideos = [
  {
    id: "g1",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Glitch+1",
    view_count: 13700,
    user: { username: "glitcher1", profile_image: "https://via.placeholder.com/24" },
  },
  {
    id: "g2",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Glitch+2",
    view_count: 5456,
    user: { username: "glitcher2", profile_image: "https://via.placeholder.com/24" },
  },
  {
    id: "g3",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Glitch+3",
    view_count: 1111,
    user: { username: "glitcher3", profile_image: "https://via.placeholder.com/24" },
  },
  {
    id: "g4",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Glitch+4",
    view_count: 1826,
    user: { username: "glitcher4", profile_image: "https://via.placeholder.com/24" },
  },
  {
    id: "g5",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Glitch+5",
    view_count: 4354,
    user: { username: "glitcher5", profile_image: "https://via.placeholder.com/24" },
  },
  {
    id: "g6",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Glitch+6",
    view_count: 2340,
    user: { username: "glitcher6", profile_image: "https://via.placeholder.com/24" },
  },
];

export default function GlitchModal({
  isOpen,
  onClose,
  videoId,
  originalUser,
}: GlitchModalProps) {
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
            <h2 className="text-xl font-bold">원음 - {originalUser}</h2>
            <p className="text-sm text-muted-foreground">
              {formatCount(mockGlitchVideos.length)} 동영상
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
          <VideoGrid videos={mockGlitchVideos} onVideoClick={handleVideoClick} />
        </div>
      </div>
    </div>
  );
}

