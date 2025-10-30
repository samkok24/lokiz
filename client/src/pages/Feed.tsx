import { useState, useRef, useEffect } from "react";
import VideoPlayer from "@/components/VideoPlayer";
import GlitchModal from "@/components/GlitchModal";
import HashtagModal from "@/components/HashtagModal";

// Mock data
const mockVideos = [
  {
    id: "1",
    url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Video+1",
    user: {
      id: "1",
      username: "user1",
      profile_image: "https://via.placeholder.com/48",
    },
    caption: "Amazing video! #lokiz #glitch #ai",
    view_count: 125000,
    like_count: 12300,
    comment_count: 456,
    glitch_count: 89,
    is_liked: false,
  },
  {
    id: "2",
    url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Video+2",
    user: {
      id: "2",
      username: "user2",
      profile_image: "https://via.placeholder.com/48",
    },
    caption: "Check this out! 🔥",
    view_count: 89000,
    like_count: 8900,
    comment_count: 234,
    glitch_count: 45,
    is_liked: true,
  },
  {
    id: "3",
    url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Video+3",
    user: {
      id: "3",
      username: "user3",
      profile_image: "https://via.placeholder.com/48",
    },
    caption: "This is incredible! #trending",
    view_count: 234000,
    like_count: 23400,
    comment_count: 789,
    glitch_count: 123,
    is_liked: false,
  },
];

export default function Feed() {
  const [videos] = useState(mockVideos);
  const [currentIndex, setCurrentIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isScrolling, setIsScrolling] = useState(false);
  const [glitchModal, setGlitchModal] = useState<{ isOpen: boolean; videoId: string; user: string }>({ isOpen: false, videoId: "", user: "" });
  const [hashtagModal, setHashtagModal] = useState<{ isOpen: boolean; hashtag: string }>({ isOpen: false, hashtag: "" });

  // Handle scroll
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let scrollTimeout: NodeJS.Timeout;

    const handleScroll = () => {
      setIsScrolling(true);
      clearTimeout(scrollTimeout);

      scrollTimeout = setTimeout(() => {
        setIsScrolling(false);
        
        // Snap to nearest video
        const scrollTop = container.scrollTop;
        const videoHeight = window.innerHeight;
        const newIndex = Math.round(scrollTop / videoHeight);
        
        if (newIndex !== currentIndex) {
          setCurrentIndex(newIndex);
          container.scrollTo({
            top: newIndex * videoHeight,
            behavior: "smooth",
          });
        }
      }, 150);
    };

    container.addEventListener("scroll", handleScroll);
    return () => {
      container.removeEventListener("scroll", handleScroll);
      clearTimeout(scrollTimeout);
    };
  }, [currentIndex]);

  const handleLike = (videoId: string) => {
    console.log("Like video:", videoId);
    // TODO: API call
  };

  const handleComment = (videoId: string) => {
    console.log("Comment on video:", videoId);
    // TODO: Open comment modal
  };

  const handleGlitch = (videoId: string) => {
    const video = videos.find(v => v.id === videoId);
    if (video) {
      setGlitchModal({ isOpen: true, videoId, user: video.user.username });
    }
  };

  const handleShare = (videoId: string) => {
    console.log("Share video:", videoId);
    // TODO: Open share modal
  };

  return (
    <div
      ref={containerRef}
      className="h-screen overflow-y-scroll snap-y snap-mandatory scroll-smooth"
      style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
    >
      <style>{`
        div::-webkit-scrollbar {
          display: none;
        }
      `}</style>
      
      {videos.map((video, index) => (
        <div key={video.id} className="h-screen snap-start">
          <VideoPlayer
            video={video}
            isActive={index === currentIndex && !isScrolling}
            onLike={() => handleLike(video.id)}
            onComment={() => handleComment(video.id)}
            onGlitch={() => handleGlitch(video.id)}
            onShare={() => handleShare(video.id)}
          />
        </div>
      ))}

      {/* Modals */}
      <GlitchModal
        isOpen={glitchModal.isOpen}
        onClose={() => setGlitchModal({ isOpen: false, videoId: "", user: "" })}
        videoId={glitchModal.videoId}
        originalUser={glitchModal.user}
      />
      <HashtagModal
        isOpen={hashtagModal.isOpen}
        onClose={() => setHashtagModal({ isOpen: false, hashtag: "" })}
        hashtag={hashtagModal.hashtag}
      />
    </div>
  );
}
