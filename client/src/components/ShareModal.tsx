import { useState } from "react";
import { X, Search } from "lucide-react";

interface ShareModalProps {
  isOpen: boolean;
  onClose: () => void;
  videoId: string;
}

// Mock following users
const mockFollowingUsers = [
  { id: "me", username: "dsge foc", profile_image: "https://via.placeholder.com/60", isMe: true },
  { id: "user1", username: "세스킹", profile_image: "https://via.placeholder.com/60", isMe: false },
  { id: "user2", username: "Hikilkarma", profile_image: "https://via.placeholder.com/60", isMe: false },
  { id: "user3", username: "사용혁", profile_image: "https://via.placeholder.com/60", isMe: false },
  { id: "user4", username: "윤여민", profile_image: "https://via.placeholder.com/60", isMe: false },
];

const socialShareOptions = [
  { id: "repost", name: "리포스트", icon: "📱", color: "bg-yellow-500" },
  { id: "copy", name: "Copy", icon: "🔗", color: "bg-blue-500" },
  { id: "whatsapp", name: "WhatsApp", icon: "💬", color: "bg-green-500" },
  { id: "embed", name: "동영상 퍼가기", icon: "📋", color: "bg-cyan-500" },
  { id: "facebook", name: "Facebook", icon: "👍", color: "bg-blue-600" },
];

export default function ShareModal({ isOpen, onClose, videoId }: ShareModalProps) {
  const [selectedUser, setSelectedUser] = useState<string | null>(null);
  const [message, setMessage] = useState("");

  if (!isOpen) return null;

  const handleUserClick = (userId: string) => {
    if (userId === "me") return; // 나 자신은 클릭 불가
    setSelectedUser(userId);
  };

  const handleSend = () => {
    console.log("Send to:", selectedUser, "Message:", message);
    // TODO: Call API
    setSelectedUser(null);
    setMessage("");
    onClose();
  };

  const handleSocialShare = (socialId: string) => {
    console.log("Share to:", socialId);
    // TODO: Implement social share
    if (socialId === "copy") {
      navigator.clipboard.writeText(`https://lokiz.com/video/${videoId}`);
      // TODO: Show toast
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/70"
        onClick={() => {
          setSelectedUser(null);
          setMessage("");
          onClose();
        }}
      />

      {/* Modal */}
      <div className="relative w-full max-w-md bg-[#1a1a1a] rounded-lg overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
          <button
            onClick={() => {
              setSelectedUser(null);
              setMessage("");
            }}
            className="p-1"
          >
            <Search className="w-5 h-5 text-gray-400" />
          </button>
          <h2 className="text-white font-semibold">공유 대상</h2>
          <button
            onClick={() => {
              setSelectedUser(null);
              setMessage("");
              onClose();
            }}
            className="p-1"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4">
          {selectedUser ? (
            // Message input view
            <div className="space-y-4">
              {/* Selected user */}
              <div className="flex items-center gap-3">
                {mockFollowingUsers
                  .filter((u) => u.id === selectedUser)
                  .map((user) => (
                    <div key={user.id} className="relative">
                      <img
                        src={user.profile_image}
                        alt={user.username}
                        className="w-12 h-12 rounded-full"
                      />
                      <button
                        onClick={() => setSelectedUser(null)}
                        className="absolute -top-1 -right-1 w-5 h-5 bg-[#FE2C55] rounded-full flex items-center justify-center"
                      >
                        <X className="w-3 h-3 text-white" />
                      </button>
                    </div>
                  ))}
              </div>

              {/* Message input */}
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="메시지 작성..."
                className="w-full h-32 bg-[#2a2a2a] text-white rounded-lg px-4 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-[#C9F227]"
              />

              {/* Send button */}
              <button
                onClick={handleSend}
                className="w-full py-3 bg-[#FE2C55] text-white font-semibold rounded-lg hover:bg-[#FE2C55]/90 transition-colors"
              >
                보내기
              </button>
            </div>
          ) : (
            // Default view
            <div className="space-y-6">
              {/* Following users */}
              <div className="flex gap-4 overflow-x-auto pb-2">
                {mockFollowingUsers.map((user) => (
                  <button
                    key={user.id}
                    onClick={() => handleUserClick(user.id)}
                    className="flex flex-col items-center gap-2 min-w-[60px]"
                    disabled={user.isMe}
                  >
                    <div className="relative">
                      <img
                        src={user.profile_image}
                        alt={user.username}
                        className={`w-14 h-14 rounded-full ${
                          user.isMe ? "opacity-100" : "opacity-90 hover:opacity-100"
                        }`}
                        style={{
                          background: user.isMe
                            ? "linear-gradient(135deg, #C9F227 0%, #00F2EA 100%)"
                            : "transparent",
                        }}
                      />
                    </div>
                    <span className="text-white text-xs text-center line-clamp-1">
                      {user.username}
                    </span>
                  </button>
                ))}
              </div>

              {/* Social share options */}
              <div className="flex gap-4 justify-center">
                {socialShareOptions.map((option) => (
                  <button
                    key={option.id}
                    onClick={() => handleSocialShare(option.id)}
                    className="flex flex-col items-center gap-2"
                  >
                    <div
                      className={`w-14 h-14 ${option.color} rounded-full flex items-center justify-center text-2xl`}
                    >
                      {option.icon}
                    </div>
                    <span className="text-white text-xs text-center">{option.name}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

