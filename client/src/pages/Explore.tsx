import { useState, useEffect, useRef } from "react";
import { Heart } from "lucide-react";
import VideoDetailModal from "@/components/VideoDetailModal";

const categories = [
  "모두",
  "노래 맞춤",
  "코미디",
  "스포츠",
  "애니메이션 및 만화",
  "관계",
  "쇼",
  "힙합크",
  "일상 생활",
  "뷰티 케어",
  "게임",
  "사회",
  "의상",
  "자동차",
];

// Mock data
const generateMockVideos = (count: number, startIndex: number) => {
  return Array.from({ length: count }, (_, i) => ({
    id: `${startIndex + i + 1}`,
    thumbnailUrl: `https://via.placeholder.com/300x400?text=Video+${startIndex + i + 1}`,
    likeCount: Math.floor(Math.random() * 1000000) + 1000,
    user: {
      id: `user${startIndex + i + 1}`,
      username: `user${startIndex + i + 1}`,
      profileImage: "https://via.placeholder.com/40",
    },
    url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    caption: `Amazing video! #lokiz #glitch #ai`,
    viewCount: Math.floor(Math.random() * 1000000) + 1000,
    commentCount: Math.floor(Math.random() * 10000) + 100,
    glitchCount: Math.floor(Math.random() * 1000) + 10,
    shareCount: Math.floor(Math.random() * 10000) + 100,
    isLiked: false,
  }));
};

export default function Explore() {
  const [activeCategory, setActiveCategory] = useState("모두");
  const [videos, setVideos] = useState(generateMockVideos(20, 0));
  const [selectedVideo, setSelectedVideo] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const observerRef = useRef<HTMLDivElement>(null);

  // Infinite scroll
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !isLoading) {
          loadMoreVideos();
        }
      },
      { threshold: 0.1 }
    );

    if (observerRef.current) {
      observer.observe(observerRef.current);
    }

    return () => {
      if (observerRef.current) {
        observer.unobserve(observerRef.current);
      }
    };
  }, [isLoading, videos.length]);

  const loadMoreVideos = () => {
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      const newVideos = generateMockVideos(20, videos.length);
      setVideos((prev) => [...prev, ...newVideos]);
      setIsLoading(false);
    }, 1000);
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
    <div className="min-h-screen pb-8">
      {/* Category Tabs */}
      <div className="sticky top-0 z-10 bg-background border-b border-border">
        <div className="container mx-auto px-6">
          <div className="flex items-center gap-4 overflow-x-auto py-4 scrollbar-hide">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setActiveCategory(category)}
                className={`px-4 py-2 rounded-full whitespace-nowrap text-sm font-medium transition-colors ${
                  activeCategory === category
                    ? "bg-white text-black"
                    : "bg-[#2a2a2a] text-white hover:bg-[#3a3a3a]"
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Video Grid */}
      <div className="container mx-auto px-6 pt-6">
        <div className="grid grid-cols-4 lg:grid-cols-5 gap-4">
          {videos.map((video) => (
            <div
              key={video.id}
              onClick={() => setSelectedVideo(video.id)}
              className="group cursor-pointer"
            >
              {/* Thumbnail */}
              <div className="relative aspect-[3/4] bg-muted rounded-lg overflow-hidden mb-2">
                <img
                  src={video.thumbnailUrl}
                  alt={`Video ${video.id}`}
                  className="w-full h-full object-cover"
                />
                
                {/* Hover Overlay */}
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />

                {/* Like Count */}
                <div className="absolute bottom-2 left-2 flex items-center gap-1 text-white text-sm font-semibold">
                  <Heart className="w-4 h-4 fill-white" />
                  <span>{formatCount(video.likeCount)}</span>
                </div>
              </div>

              {/* User Info */}
              <div className="flex items-center gap-2">
                <img
                  src={video.user.profileImage}
                  alt={video.user.username}
                  className="w-6 h-6 rounded-full"
                />
                <span className="text-sm text-gray-400 truncate">
                  {video.user.username}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-center items-center py-8">
            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {/* Infinite Scroll Trigger */}
        <div ref={observerRef} className="h-10" />
      </div>

      {/* Video Detail Modal */}
      {selectedVideo && (
        <VideoDetailModal
          isOpen={!!selectedVideo}
          onClose={() => setSelectedVideo(null)}
          video={{
            id: videos.find(v => v.id === selectedVideo)?.id || "",
            url: videos.find(v => v.id === selectedVideo)?.url || "",
            user: {
              id: videos.find(v => v.id === selectedVideo)?.user.id || "",
              username: videos.find(v => v.id === selectedVideo)?.user.username || "",
              profile_image: videos.find(v => v.id === selectedVideo)?.user.profileImage || "",
            },
            caption: videos.find(v => v.id === selectedVideo)?.caption || "",
            view_count: videos.find(v => v.id === selectedVideo)?.viewCount || 0,
            like_count: videos.find(v => v.id === selectedVideo)?.likeCount || 0,
            comment_count: videos.find(v => v.id === selectedVideo)?.commentCount || 0,
            is_liked: videos.find(v => v.id === selectedVideo)?.isLiked || false,
          }}
        />
      )}
    </div>
  );
}

