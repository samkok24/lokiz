import { X, Heart, AtSign, Smile } from "lucide-react";
import { useState } from "react";
import { useAuthStore } from "@/lib/store/authStore";
import LoginModal from "@/components/LoginModal";

interface Comment {
  id: string;
  user: {
    id: string;
    username: string;
    profile_image: string;
  };
  text: string;
  like_count: number;
  is_liked: boolean;
  created_at: string;
  replies?: Comment[];
}

interface CommentPanelProps {
  isOpen: boolean;
  onClose: () => void;
  videoId: string;
  commentCount: number;
}

export default function CommentPanel({ isOpen, onClose, videoId, commentCount }: CommentPanelProps) {
  const { isAuthenticated } = useAuthStore();
  const [loginModalOpen, setLoginModalOpen] = useState(false);
  const [comments] = useState<Comment[]>([
    {
      id: "1",
      user: {
        id: "user1",
        username: "user1",
        profile_image: "https://via.placeholder.com/40",
      },
      text: "와 현타가 브아지?",
      like_count: 5,
      is_liked: false,
      created_at: "8-12",
      replies: [
        {
          id: "1-1",
          user: {
            id: "user2",
            username: "user2",
            profile_image: "https://via.placeholder.com/40",
          },
          text: "답글 테스트",
          like_count: 2,
          is_liked: false,
          created_at: "8-12",
        },
      ],
    },
    {
      id: "2",
      user: {
        id: "user3",
        username: "blackship",
        profile_image: "https://via.placeholder.com/40",
      },
      text: "사랑이 만드는건 꿀떡이냐",
      like_count: 25,
      is_liked: false,
      created_at: "8-12",
    },
    {
      id: "3",
      user: {
        id: "user4",
        username: "병수",
        profile_image: "https://via.placeholder.com/40",
      },
      text: "전략 개 이쁘다",
      like_count: 0,
      is_liked: false,
      created_at: "8-12",
    },
  ]);

  const [commentText, setCommentText] = useState("");

  const handleSubmit = () => {
    if (!isAuthenticated) {
      setLoginModalOpen(true);
      return;
    }
    console.log("Submit comment:", commentText);
    // TODO: Call API
    setCommentText("");
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/50 z-40"
        onClick={onClose}
      />

      {/* Comment Panel */}
      <div className="fixed top-0 right-0 h-screen w-[400px] bg-[#121212] z-50 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <h2 className="text-white font-semibold">댓글 ({commentCount})</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Comments List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {comments.map((comment) => (
            <div key={comment.id} className="space-y-2">
              {/* Main Comment */}
              <div className="flex gap-3">
                <img
                  src={comment.user.profile_image}
                  alt={comment.user.username}
                  className="w-10 h-10 rounded-full"
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-white font-semibold text-sm">
                      {comment.user.username}
                    </span>
                    <span className="text-gray-500 text-xs">{comment.created_at}</span>
                  </div>
                  <p className="text-white text-sm mt-1">{comment.text}</p>
                  <div className="flex items-center gap-4 mt-2">
                    <button className="text-gray-400 hover:text-white text-xs">
                      답글
                    </button>
                    {comment.replies && comment.replies.length > 0 && (
                      <button className="text-gray-400 hover:text-white text-xs flex items-center gap-1">
                        답글 {comment.replies.length}개 보기
                        <span className="text-xs">▼</span>
                      </button>
                    )}
                  </div>
                </div>
                <button className="flex flex-col items-center gap-1">
                  <Heart
                    size={16}
                    className={comment.is_liked ? "fill-red-500 text-red-500" : "text-gray-400"}
                  />
                  {comment.like_count > 0 && (
                    <span className="text-gray-400 text-xs">{comment.like_count}</span>
                  )}
                </button>
              </div>

              {/* Replies */}
              {comment.replies && comment.replies.map((reply) => (
                <div key={reply.id} className="flex gap-3 ml-12">
                  <img
                    src={reply.user.profile_image}
                    alt={reply.user.username}
                    className="w-8 h-8 rounded-full"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-white font-semibold text-sm">
                        {reply.user.username}
                      </span>
                      <span className="text-gray-500 text-xs">{reply.created_at}</span>
                    </div>
                    <p className="text-white text-sm mt-1">{reply.text}</p>
                  </div>
                  <button className="flex flex-col items-center gap-1">
                    <Heart
                      size={14}
                      className={reply.is_liked ? "fill-red-500 text-red-500" : "text-gray-400"}
                    />
                    {reply.like_count > 0 && (
                      <span className="text-gray-400 text-xs">{reply.like_count}</span>
                    )}
                  </button>
                </div>
              ))}
            </div>
          ))}
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-800">
          <div className="flex items-center gap-2 bg-[#1a1a1a] rounded-lg p-3">
            <input
              type="text"
              placeholder="댓글을 달 한마디를 해주세요..."
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSubmit()}
              className="flex-1 bg-transparent text-white text-sm outline-none placeholder-gray-500"
            />
            <button className="text-gray-400 hover:text-white">
              <AtSign size={20} />
            </button>
            <button className="text-gray-400 hover:text-white">
              <Smile size={20} />
            </button>
            <button
              onClick={handleSubmit}
              disabled={!commentText.trim()}
              className="text-primary font-semibold text-sm disabled:opacity-50"
            >
              게시
            </button>
          </div>
        </div>
      </div>

      {/* Login Modal */}
      <LoginModal 
        isOpen={loginModalOpen} 
        onClose={() => setLoginModalOpen(false)}
      />
    </>
  );
}

