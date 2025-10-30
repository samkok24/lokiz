import { useState, useRef, useEffect } from "react";
import VideoPlayer from "@/components/VideoPlayer";
import GlitchModal from "@/components/GlitchModal";
import HashtagModal from "@/components/HashtagModal";
import CommentPanel from "@/components/CommentPanel";
import ShareModal from "@/components/ShareModal";

// Mock data
const mockVideos = [
  {
    id: "1",
    url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Video+1",
    user: {
      id: "user1",
      username: "user1",
      profile_image: "https://via.placeholder.com/40",
    },
    caption: "Amazing video! #lokiz #glitch #ai",
    view_count: 123000,
    like_count: 12300,
    comment_count: 456,
    glitch_count: 89,
    share_count: 234,
    is_liked: false,
  },
  {
    id: "2",
    url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Video+2",
    user: {
      id: "user2",
      username: "user2",
      profile_image: "https://via.placeholder.com/40",
    },
    caption: "Check this out! #trending",
    view_count: 456000,
    like_count: 45600,
    comment_count: 789,
    glitch_count: 123,
    share_count: 567,
    is_liked: true,
  },
  {
    id: "3",
    url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    thumbnail_url: "https://via.placeholder.com/400x600?text=Video+3",
    user: {
      id: "user3",
      username: "user3",
      profile_image: "https://via.placeholder.com/40",
    },
    caption: "Epic moment! #viral",
    view_count: 789000,
    like_count: 78900,
    comment_count: 1234,
    glitch_count: 456,
    share_count: 890,
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
  const [commentPanel, setCommentPanel] = useState<{ isOpen: boolean; videoId: string }>({ isOpen: false, videoId: "" });
  const [shareModal, setShareModal] = useState<{ isOpen: boolean; videoId: string }>({ isOpen: false, videoId: "" });

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
        const videoHeight = container.clientHeight;
        const newIndex = Math.round(scrollTop / videoHeight);
        
        if (newIndex !== currentIndex && newIndex >= 0 && newIndex < videos.length) {
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
  }, [currentIndex, videos.length]);

  const handleLike = (videoId: string) => {
    console.log("Like video:", videoId);
    // TODO: Call API
  };

  const handleComment = (videoId: string) => {
    setCommentPanel({ isOpen: true, videoId });
  };

  const handleGlitch = (videoId: string) => {
    const video = videos.find(v => v.id === videoId);
    if (video) {
      setGlitchModal({ isOpen: true, videoId, user: video.user.username });
    }
  };

  const handleShare = (videoId: string) => {
    setShareModal({ isOpen: true, videoId });
  };

  return (
    <div className="flex items-center justify-center h-screen bg-black">
      <div
        ref={containerRef}
        className="relative h-screen overflow-y-scroll snap-y snap-mandatory"
        style={{ width: '56.25%', minWidth: '320px', maxWidth: '600px' }}
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
      </div>

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
      <CommentPanel
        isOpen={commentPanel.isOpen}
        onClose={() => setCommentPanel({ isOpen: false, videoId: "" })}
        videoId={commentPanel.videoId}
        commentCount={videos.find(v => v.id === commentPanel.videoId)?.comment_count || 0}
      />
      <ShareModal
        isOpen={shareModal.isOpen}
        onClose={() => setShareModal({ isOpen: false, videoId: "" })}
        videoId={shareModal.videoId}
      />
    </div>
  );
}

