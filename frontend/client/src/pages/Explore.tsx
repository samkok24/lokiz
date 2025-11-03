import { useState, useEffect, useRef } from "react";
import { Heart, ChevronLeft, ChevronRight } from "lucide-react";
import VideoDetailModal from "@/components/VideoDetailModal";
import { mockVideos } from "@shared/mockData";
import type { Video } from "@shared/types";

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

// Mock data - using mockVideos from shared/mockData.ts
const generateMockVideos = (count: number, startIndex: number): Video[] => {
  // Repeat mockVideos to generate more videos
  const result: Video[] = [];
  for (let i = 0; i < count; i++) {
    const sourceVideo = mockVideos[i % mockVideos.length];
    result.push({
      ...sourceVideo,
      id: `${startIndex + i + 1}`,
    });
  }
  return result;
};

export default function Explore() {
  const [activeCategory, setActiveCategory] = useState("모두");
  const [videos, setVideos] = useState(generateMockVideos(20, 0));
  const [selectedVideo, setSelectedVideo] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const observerRef = useRef<HTMLDivElement>(null);
  const categoryScrollRef = useRef<HTMLDivElement>(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);

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
  }, [isLoading]);

  // Check scroll position for arrows
  const checkScrollPosition = () => {
    if (categoryScrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = categoryScrollRef.current;
      setShowLeftArrow(scrollLeft > 0);
      setShowRightArrow(scrollLeft < scrollWidth - clientWidth - 10);
    }
  };

  useEffect(() => {
    checkScrollPosition();
    const scrollContainer = categoryScrollRef.current;
    if (scrollContainer) {
      scrollContainer.addEventListener('scroll', checkScrollPosition);
      return () => scrollContainer.removeEventListener('scroll', checkScrollPosition);
    }
  }, []);

  const scrollCategories = (direction: 'left' | 'right') => {
    if (categoryScrollRef.current) {
      const scrollAmount = 300;
      categoryScrollRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      });
    }
  };

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
      <div className="sticky top-16 z-10 bg-background border-b border-border">
        <div className="container mx-auto px-2 md:px-6">
          <div className="relative flex items-center py-2 md:py-4">
            {/* Left Arrow */}
            {showLeftArrow && (
              <button
                onClick={() => scrollCategories('left')}
                className="absolute left-0 z-20 w-8 h-8 flex items-center justify-center bg-background/80 hover:bg-background rounded-full shadow-lg transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
            )}

            {/* Categories */}
            <div 
              ref={categoryScrollRef}
              className="flex items-center gap-4 overflow-x-auto scrollbar-hide scroll-smooth"
              style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
            >
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setActiveCategory(category)}
                  className={`px-3 md:px-4 py-1.5 md:py-2 rounded-full whitespace-nowrap text-xs md:text-sm font-medium transition-colors ${
                    activeCategory === category
                      ? "bg-white text-black"
                      : "bg-[#2a2a2a] text-white hover:bg-[#3a3a3a]"
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>

            {/* Right Arrow */}
            {showRightArrow && (
              <button
                onClick={() => scrollCategories('right')}
                className="absolute right-0 z-20 w-8 h-8 flex items-center justify-center bg-background/80 hover:bg-background rounded-full shadow-lg transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Video Grid */}
      <div className="container mx-auto px-2 md:px-6 pt-4 md:pt-6">
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-1">
          {videos.map((video) => (
            <div
              key={video.id}
              onClick={() => setSelectedVideo(video.id)}
              className="group cursor-pointer"
            >
              {/* Thumbnail */}
              <div className="relative aspect-[3/4] bg-muted rounded-lg overflow-hidden mb-1 md:mb-2">
                <img
                  src={video.thumbnailUrl}
                  alt={`Video ${video.id}`}
                  className="w-full h-full object-cover"
                />
                
                {/* Hover Overlay */}
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />

                {/* Like Count */}
                <div className="absolute bottom-1 md:bottom-2 left-1 md:left-2 flex items-center gap-0.5 md:gap-1 text-white text-xs md:text-sm font-semibold">
                  <Heart className="w-3 h-3 md:w-4 md:h-4 fill-white" />
                  <span>{formatCount(video.likes)}</span>
                </div>
              </div>

              {/* User Info */}
              <div className="flex items-center gap-1.5 md:gap-2">
                <img
                  src={video.user.avatar}
                  alt={video.user.username}
                  className="w-5 h-5 md:w-6 md:h-6 rounded-full"
                />
                <span className="text-xs md:text-sm text-gray-400 truncate">
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
            url: videos.find(v => v.id === selectedVideo)?.videoUrl || "",
            user: {
              id: videos.find(v => v.id === selectedVideo)?.user.id || "",
              username: videos.find(v => v.id === selectedVideo)?.user.username || "",
              profile_image: videos.find(v => v.id === selectedVideo)?.user.avatar || "",
            },
            caption: videos.find(v => v.id === selectedVideo)?.caption || "",
            view_count: videos.find(v => v.id === selectedVideo)?.views || 0,
            like_count: videos.find(v => v.id === selectedVideo)?.likes || 0,
            comment_count: videos.find(v => v.id === selectedVideo)?.comments || 0,
            is_liked: videos.find(v => v.id === selectedVideo)?.isLiked || false,
          }}
        />
      )}
    </div>
  );
}

