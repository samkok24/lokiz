import { useState } from "react";
import { Share2, MoreHorizontal, Play, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import VideoDetailModal from "@/components/VideoDetailModal";
import FollowModal from "@/components/FollowModal";
import { useLocation } from "wouter";
import { mockVideos, mockUsers } from "@shared/mockData";
import type { Video } from "@shared/types";

// Mock data
const mockUser = mockUsers[0];

export default function Profile() {
  const [isFollowing, setIsFollowing] = useState(false);
  const [activeTab, setActiveTab] = useState("videos");
  const [selectedVideo, setSelectedVideo] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<"latest" | "popular" | "oldest">("latest");
  const [followModalOpen, setFollowModalOpen] = useState(false);
  const [followModalTab, setFollowModalTab] = useState<"following" | "followers" | "friends" | "suggested">("following");
  const [, setLocation] = useLocation();

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
    <div className="min-h-screen relative">
      {/* Close button */}
      <button
        onClick={() => setLocation("/")}
        className="fixed top-6 right-6 z-10 p-2 hover:bg-white/10 rounded-full transition-colors"
      >
        <X className="w-6 h-6" />
      </button>

      {/* Profile Header */}
      <div className="border-b border-border">
        <div className="container mx-auto px-6 py-8">
          <div className="flex items-start gap-8">
            {/* Profile Image */}
            <div className="flex-shrink-0">
              <img
                src={mockUser.avatar}
                alt={mockUser.nickname}
                className="w-32 h-32 rounded-full object-cover"
              />
            </div>

            {/* Profile Info */}
            <div className="flex-1">
              <h1 className="text-3xl font-bold mb-1">{mockUser.nickname}</h1>
              <p className="text-muted-foreground mb-4">@{mockUser.username}</p>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 mb-6">
                <Button
                  variant={isFollowing ? "outline" : "default"}
                  onClick={() => setIsFollowing(!isFollowing)}
                  className="px-8"
                >
                  {isFollowing ? "팔로잉" : "팔로우"}
                </Button>
                <Button variant="outline" size="icon">
                  <Share2 className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="icon">
                  <MoreHorizontal className="w-4 h-4" />
                </Button>
              </div>

              {/* Stats */}
              <div className="flex items-center gap-6 mb-4">
                <button
                  onClick={() => {
                    setFollowModalTab("following");
                    setFollowModalOpen(true);
                  }}
                  className="hover:underline"
                >
                  <span className="font-semibold">{formatNumber(mockUser.followingCount || 0)}</span>
                  <span className="text-muted-foreground ml-1">팔로잉</span>
                </button>
                <button
                  onClick={() => {
                    setFollowModalTab("followers");
                    setFollowModalOpen(true);
                  }}
                  className="hover:underline"
                >
                  <span className="font-semibold">{formatNumber(mockUser.followersCount || 0)}</span>
                  <span className="text-muted-foreground ml-1">팔로워</span>
                </button>
                <div>
                  <span className="font-semibold">{formatNumber(mockUser.likesCount || 0)}</span>
                  <span className="text-muted-foreground ml-1">좋아요</span>
                </div>
              </div>

              {/* Bio */}
              <p className="text-sm">{mockUser.bio}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="container mx-auto px-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <div className="flex items-center justify-between border-b border-border">
            <TabsList className="justify-start rounded-none h-auto p-0 bg-transparent">
              <TabsTrigger
                value="videos"
                className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-6 py-4"
              >
                동영상
              </TabsTrigger>
              <TabsTrigger
                value="reposts"
                className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-6 py-4"
              >
                리포스트
              </TabsTrigger>
              <TabsTrigger
                value="likes"
                className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-6 py-4"
              >
                좋아요
              </TabsTrigger>
            </TabsList>
            
            {/* Filter buttons */}
            <div className="flex items-center gap-2 pb-4">
              <button
                onClick={() => setSortBy("latest")}
                className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                  sortBy === "latest"
                    ? "bg-[#2a2a2a] text-white"
                    : "bg-transparent text-gray-400 hover:text-white"
                }`}
              >
                최신
              </button>
              <button
                onClick={() => setSortBy("popular")}
                className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                  sortBy === "popular"
                    ? "bg-[#2a2a2a] text-white"
                    : "bg-transparent text-gray-400 hover:text-white"
                }`}
              >
                인기
              </button>
              <button
                onClick={() => setSortBy("oldest")}
                className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                  sortBy === "oldest"
                    ? "bg-[#2a2a2a] text-white"
                    : "bg-transparent text-gray-400 hover:text-white"
                }`}
              >
                오래된 순
              </button>
            </div>
          </div>

          <TabsContent value="videos" className="mt-0">
            <VideoGrid videos={mockVideos} onVideoClick={(videoId) => setSelectedVideo(videoId)} />
          </TabsContent>

          <TabsContent value="reposts" className="mt-0">
            <div className="py-12 text-center text-muted-foreground">
              리포스트한 영상이 없습니다.
            </div>
          </TabsContent>

          <TabsContent value="likes" className="mt-0">
            <div className="py-12 text-center text-muted-foreground">
              좋아요한 영상이 없습니다.
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Video Detail Modal */}
      {selectedVideo && (
        <VideoDetailModal
          isOpen={!!selectedVideo}
          onClose={() => setSelectedVideo(null)}
          video={{
            id: selectedVideo,
            url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            user: {
              id: mockUser.id,
              username: mockUser.username,
              profile_image: mockUser.avatar,
            },
            caption: "Amazing video! #lokiz #glitch #ai",
            view_count: 123000,
            like_count: 2661,
            comment_count: 20,
            is_liked: false,
          }}
        />
      )}

      {/* Follow Modal */}
      <FollowModal
        isOpen={followModalOpen}
        onClose={() => setFollowModalOpen(false)}
        username={mockUser.username}
        initialTab={followModalTab}
      />
    </div>
  );
}

interface VideoGridProps {
  videos: Video[];
  onVideoClick: (videoId: string) => void;
}

function VideoGrid({ videos, onVideoClick }: VideoGridProps) {
  const formatViews = (views: number) => {
    if (views >= 1000000) {
      return `${(views / 1000000).toFixed(1)}M`;
    }
    if (views >= 1000) {
      return `${(views / 1000).toFixed(1)}K`;
    }
    return views.toString();
  };

  return (
    <div className="grid grid-cols-6 gap-1 py-4">
      {videos.map((video) => (
        <div
          key={video.id}
          onClick={() => onVideoClick(video.id)}
          className="relative aspect-[3/4] bg-muted rounded overflow-hidden cursor-pointer group"
        >
          <img
            src={video.thumbnailUrl}
            alt={`Video ${video.id}`}
            className="w-full h-full object-cover"
          />
          
          {/* Recently Watched Overlay */}
          {video.recentlyWatched && (
            <div className="absolute inset-0 bg-black/70 flex items-center justify-center">
              <div className="text-white text-center">
                <Play className="w-8 h-8 mx-auto mb-2 fill-white" />
                <span className="text-sm font-semibold">방금 시청함</span>
              </div>
            </div>
          )}
          
          {/* Hover Overlay */}
          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />

          {/* View Count */}
          <div className="absolute bottom-2 left-2 flex items-center gap-1 text-white text-sm font-semibold">
            <Play className="w-4 h-4 fill-white" />
            <span>{formatViews(video.views)}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

