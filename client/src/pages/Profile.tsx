import { useState } from "react";
import { Share2, MoreHorizontal, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

// Mock data
const mockUser = {
  id: "1",
  username: "lynarex",
  displayName: "lynarex 짜모",
  profileImage: "https://via.placeholder.com/150",
  bio: "Tfssrw",
  following: 169,
  followers: 12300,
  likes: 125500,
};

const mockVideos = Array.from({ length: 12 }, (_, i) => ({
  id: `${i + 1}`,
  thumbnail: `https://via.placeholder.com/300x400?text=Video+${i + 1}`,
  views: Math.floor(Math.random() * 50000) + 1000,
}));

export default function Profile() {
  const [isFollowing, setIsFollowing] = useState(false);
  const [activeTab, setActiveTab] = useState("videos");

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
    <div className="min-h-screen">
      {/* Profile Header */}
      <div className="border-b border-border">
        <div className="container mx-auto px-6 py-8">
          <div className="flex items-start gap-8">
            {/* Profile Image */}
            <div className="flex-shrink-0">
              <img
                src={mockUser.profileImage}
                alt={mockUser.displayName}
                className="w-32 h-32 rounded-full object-cover"
              />
            </div>

            {/* Profile Info */}
            <div className="flex-1">
              <h1 className="text-3xl font-bold mb-1">{mockUser.displayName}</h1>
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
                <div>
                  <span className="font-semibold">{formatNumber(mockUser.following)}</span>
                  <span className="text-muted-foreground ml-1">팔로잉</span>
                </div>
                <div>
                  <span className="font-semibold">{formatNumber(mockUser.followers)}</span>
                  <span className="text-muted-foreground ml-1">팔로워</span>
                </div>
                <div>
                  <span className="font-semibold">{formatNumber(mockUser.likes)}</span>
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
          <TabsList className="w-full justify-start border-b border-border rounded-none h-auto p-0 bg-transparent">
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

          <TabsContent value="videos" className="mt-0">
            <VideoGrid videos={mockVideos} />
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
    </div>
  );
}

interface VideoGridProps {
  videos: Array<{
    id: string;
    thumbnail: string;
    views: number;
  }>;
}

function VideoGrid({ videos }: VideoGridProps) {
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
    <div className="grid grid-cols-3 gap-1 py-4">
      {videos.map((video) => (
        <div
          key={video.id}
          className="relative aspect-[3/4] bg-muted rounded overflow-hidden cursor-pointer group"
        >
          <img
            src={video.thumbnail}
            alt={`Video ${video.id}`}
            className="w-full h-full object-cover"
          />
          
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

