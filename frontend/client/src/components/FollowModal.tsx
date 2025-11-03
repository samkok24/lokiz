import { X, Users } from "lucide-react";
import { useState } from "react";
import { Button } from "./ui/button";
import { mockUsers } from "@shared/mockData";
import type { User as UserType } from "@shared/types";

interface User {
  id: string;
  username: string;
  nickname: string;
  avatar: string;
  isFollowing?: boolean;
  isFollower?: boolean;
}

interface FollowModalProps {
  isOpen: boolean;
  onClose: () => void;
  username: string;
  initialTab?: "following" | "followers" | "friends" | "suggested";
}

// Mock data - using first 3 users from shared mockData
const mockFollowing: User[] = mockUsers.slice(0, 3).map(u => ({ ...u, isFollowing: true, isFollower: false }));
const mockFollowers: User[] = mockUsers.slice(0, 2).map(u => ({ ...u, isFollowing: false, isFollower: true }));
const mockSuggested: User[] = mockUsers.slice(0, 3).map(u => ({ ...u, isFollowing: false, isFollower: false }));

export default function FollowModal({ isOpen, onClose, username, initialTab = "following" }: FollowModalProps) {
  const [activeTab, setActiveTab] = useState(initialTab);
  const [followingUsers, setFollowingUsers] = useState(mockFollowing);
  const [followerUsers, setFollowerUsers] = useState(mockFollowers);
  const [suggestedUsers, setSuggestedUsers] = useState(mockSuggested);

  if (!isOpen) return null;

  const friends = followingUsers.filter(user => 
    followerUsers.some(follower => follower.id === user.id)
  );

  const handleFollow = (userId: string, listType: "following" | "followers" | "suggested") => {
    if (listType === "following") {
      setFollowingUsers(prev => prev.filter(u => u.id !== userId));
    } else if (listType === "followers") {
      setFollowerUsers(prev => prev.map(u => 
        u.id === userId ? { ...u, isFollowing: !u.isFollowing } : u
      ));
    } else if (listType === "suggested") {
      setSuggestedUsers(prev => prev.map(u => 
        u.id === userId ? { ...u, isFollowing: !u.isFollowing } : u
      ));
    }
  };

  const renderUserList = (users: User[], listType: "following" | "followers" | "suggested") => {
    if (users.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center py-16 text-gray-400">
          <Users className="w-16 h-16 mb-4 text-gray-600" />
          <p className="text-sm">
            {activeTab === "friends" 
              ? "맞팔로우하는 팔로워가 있으면 여기에 표시됩니다"
              : "아직 아무도 없습니다"}
          </p>
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {users.map((user) => (
          <div key={user.id} className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img
                src={user.avatar}
                alt={user.nickname}
                className="w-12 h-12 rounded-full"
              />
              <div>
                <div className="font-semibold text-white">{user.nickname}</div>
                <div className="text-sm text-gray-400">{user.username}</div>
              </div>
            </div>

            <Button
              onClick={() => handleFollow(user.id, listType)}
              className={`px-6 py-2 rounded-md font-semibold text-sm ${
                listType === "following"
                  ? "bg-[#2a2a2a] text-white hover:bg-[#3a3a3a]"
                  : user.isFollowing
                  ? "bg-[#2a2a2a] text-white hover:bg-[#3a3a3a]"
                  : "bg-[#D0FF00] text-black hover:bg-[#b8e600]"
              }`}
            >
              {listType === "following" 
                ? "팔로잉" 
                : user.isFollowing 
                ? "팔로잉" 
                : listType === "followers" 
                ? "맞팔로우" 
                : "팔로우"}
            </Button>
          </div>
        ))}
      </div>
    );
  };

  const getCurrentUsers = () => {
    switch (activeTab) {
      case "following":
        return { users: followingUsers, type: "following" as const };
      case "followers":
        return { users: followerUsers, type: "followers" as const };
      case "friends":
        return { users: friends, type: "following" as const };
      case "suggested":
        return { users: suggestedUsers, type: "suggested" as const };
      default:
        return { users: [], type: "following" as const };
    }
  };

  const { users, type } = getCurrentUsers();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
      <div className="relative w-full max-w-md bg-[#1a1a1a] rounded-lg shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-xl font-semibold text-white">{username}</h2>
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border">
          <button
            onClick={() => setActiveTab("following")}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === "following"
                ? "text-white border-b-2 border-white"
                : "text-gray-400 hover:text-white"
            }`}
          >
            팔로잉 {followingUsers.length}
          </button>
          <button
            onClick={() => setActiveTab("followers")}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === "followers"
                ? "text-white border-b-2 border-white"
                : "text-gray-400 hover:text-white"
            }`}
          >
            팔로워 {followerUsers.length}
          </button>
          <button
            onClick={() => setActiveTab("friends")}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === "friends"
                ? "text-white border-b-2 border-white"
                : "text-gray-400 hover:text-white"
            }`}
          >
            친구 {friends.length}
          </button>
          <button
            onClick={() => setActiveTab("suggested")}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === "suggested"
                ? "text-white border-b-2 border-white"
                : "text-gray-400 hover:text-white"
            }`}
          >
            추천
          </button>
        </div>

        {/* User List */}
        <div className="p-4 max-h-96 overflow-y-auto">
          {renderUserList(users, type)}
        </div>
      </div>
    </div>
  );
}

