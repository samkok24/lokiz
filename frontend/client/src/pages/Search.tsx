import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { mockVideos, mockUsers } from "../../../shared/mockData";
import type { Video, User } from "../../../shared/types";
import VideoGrid from "@/components/VideoGrid";
import { Search as SearchIcon } from "lucide-react";

export default function Search() {
  const [location] = useLocation();
  const [activeTab, setActiveTab] = useState<"videos" | "users" | "hashtags">("videos");
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredVideos, setFilteredVideos] = useState<Video[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<User[]>([]);
  const [filteredHashtags, setFilteredHashtags] = useState<string[]>([]);

  // URL에서 검색어 추출
  useEffect(() => {
    const params = new URLSearchParams(location.split("?")[1]);
    const q = params.get("q") || "";
    setSearchQuery(q);
  }, [location]);

  // 검색 실행
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredVideos([]);
      setFilteredUsers([]);
      setFilteredHashtags([]);
      return;
    }

    const query = searchQuery.toLowerCase();

    // 비디오 검색 (캡션, 해시태그)
    const videos = mockVideos.filter(
      (video) =>
        video.caption.toLowerCase().includes(query) ||
        video.hashtags?.some((tag) => tag.toLowerCase().includes(query))
    );
    setFilteredVideos(videos);

    // 사용자 검색 (닉네임, 유저명)
    const users = mockUsers.filter(
      (user) =>
        user.nickname.toLowerCase().includes(query) ||
        user.username.toLowerCase().includes(query)
    );
    setFilteredUsers(users);

    // 해시태그 검색
    const allHashtags = mockVideos.flatMap((video) => video.hashtags || []);
    const uniqueHashtags = Array.from(new Set(allHashtags));
    const hashtags = uniqueHashtags.filter((tag) =>
      tag?.toLowerCase().includes(query)
    ).filter((tag): tag is string => tag !== undefined);
    setFilteredHashtags(hashtags);
  }, [searchQuery]);

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="container mx-auto px-4 py-8">
        {/* 검색 결과 헤더 */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-2">
            "{searchQuery}" 검색 결과
          </h1>
          <p className="text-gray-400">
            {filteredVideos.length + filteredUsers.length + filteredHashtags.length}개의 결과
          </p>
        </div>

        {/* 탭 */}
        <div className="flex gap-8 mb-8 border-b border-gray-800">
          <button
            onClick={() => setActiveTab("videos")}
            className={`pb-4 px-2 font-semibold transition-colors ${
              activeTab === "videos"
                ? "text-white border-b-2 border-[#D0FF00]"
                : "text-gray-400 hover:text-white"
            }`}
          >
            동영상 ({filteredVideos.length})
          </button>
          <button
            onClick={() => setActiveTab("users")}
            className={`pb-4 px-2 font-semibold transition-colors ${
              activeTab === "users"
                ? "text-white border-b-2 border-[#D0FF00]"
                : "text-gray-400 hover:text-white"
            }`}
          >
            사용자 ({filteredUsers.length})
          </button>
          <button
            onClick={() => setActiveTab("hashtags")}
            className={`pb-4 px-2 font-semibold transition-colors ${
              activeTab === "hashtags"
                ? "text-white border-b-2 border-[#D0FF00]"
                : "text-gray-400 hover:text-white"
            }`}
          >
            해시태그 ({filteredHashtags.length})
          </button>
        </div>

        {/* 검색 결과 */}
        {searchQuery.trim() === "" ? (
          <div className="flex flex-col items-center justify-center py-20 text-gray-400">
            <SearchIcon className="w-16 h-16 mb-4" />
            <p className="text-lg">검색어를 입력하세요</p>
          </div>
        ) : (
          <>
            {/* 동영상 탭 */}
            {activeTab === "videos" && (
              <>
                {filteredVideos.length > 0 ? (
                  <VideoGrid 
                    videos={filteredVideos} 
                    onVideoClick={(videoId) => console.log('Video clicked:', videoId)}
                  />
                ) : (
                  <div className="flex flex-col items-center justify-center py-20 text-gray-400">
                    <SearchIcon className="w-16 h-16 mb-4" />
                    <p className="text-lg">검색 결과가 없습니다</p>
                  </div>
                )}
              </>
            )}

            {/* 사용자 탭 */}
            {activeTab === "users" && (
              <>
                {filteredUsers.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredUsers.map((user) => (
                      <a
                        key={user.id}
                        href={`/profile/${user.id}`}
                        className="flex items-center gap-4 p-4 bg-gray-900 rounded-lg hover:bg-gray-800 transition-colors"
                      >
                        <img
                          src={user.avatar}
                          alt={user.nickname}
                          className="w-16 h-16 rounded-full object-cover"
                        />
                        <div className="flex-1">
                          <h3 className="font-semibold">{user.nickname}</h3>
                          <p className="text-sm text-gray-400">@{user.username}</p>
                          <p className="text-sm text-gray-500 mt-1">
                            팔로워 {(user.followersCount || 0).toLocaleString()}
                          </p>
                        </div>
                      </a>
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-20 text-gray-400">
                    <SearchIcon className="w-16 h-16 mb-4" />
                    <p className="text-lg">검색 결과가 없습니다</p>
                  </div>
                )}
              </>
            )}

            {/* 해시태그 탭 */}
            {activeTab === "hashtags" && (
              <>
                {filteredHashtags.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredHashtags.map((hashtag) => {
                      const videoCount = mockVideos.filter((v: Video) =>
                        v.hashtags?.includes(hashtag)
                      ).length;
                      const totalViews = mockVideos
                        .filter((v: Video) => v.hashtags?.includes(hashtag))
                        .reduce((sum: number, v: Video) => sum + v.views, 0);

                      return (
                        <a
                          key={hashtag}
                          href={`/hashtag/${encodeURIComponent(hashtag)}`}
                          className="p-6 bg-gray-900 rounded-lg hover:bg-gray-800 transition-colors"
                        >
                          <h3 className="text-xl font-bold mb-2">#{hashtag}</h3>
                          <p className="text-sm text-gray-400">
                            {videoCount}개 동영상
                          </p>
                          <p className="text-sm text-gray-500">
                            조회수 {totalViews.toLocaleString()}
                          </p>
                        </a>
                      );
                    })}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-20 text-gray-400">
                    <SearchIcon className="w-16 h-16 mb-4" />
                    <p className="text-lg">검색 결과가 없습니다</p>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}

