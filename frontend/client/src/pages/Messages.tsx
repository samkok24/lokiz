import { useState } from "react";
import { Smile } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { mockConversations } from "@shared/mockData";
import type { Conversation, Message as MessageType } from "@shared/types";

interface Message {
  id: string;
  senderId: string;
  text: string;
  timestamp: string;
}

const emojis = [
  "😀", "😃", "😄", "😁", "😆", "😅", "🤣",
  "😂", "🙂", "🙃", "😉", "😊", "😇", "🥰",
  "😍", "🤩", "😘", "😗", "😚", "😙", "🥲",
  "😋", "😛", "😜", "🤪", "😝", "🤑", "🤗",
  "🤭", "🤫", "🤔", "🤐", "🤨", "😐", "😑",
  "😶", "😏", "😒", "🙄", "😬", "🤥", "😌",
  "😔",
];

export default function Messages() {
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(
    mockConversations[0]
  );
  const [message, setMessage] = useState("");
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [messages] = useState<Message[]>([]);

  const handleSendMessage = () => {
    if (!message.trim()) return;
    // TODO: Send message
    setMessage("");
  };

  const handleEmojiClick = (emoji: string) => {
    setMessage((prev) => prev + emoji);
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Left Panel - Conversations List */}
      <div className={`${selectedConversation ? 'hidden md:block' : 'block'} w-full md:w-[300px] border-r border-border bg-[#121212]`}>
        <div className="p-3 md:p-4 border-b border-border">
          <h1 className="text-lg md:text-xl font-bold">메시지</h1>
        </div>

        <div className="overflow-y-auto">
          {mockConversations.map((conversation) => (
            <div
              key={conversation.id}
              onClick={() => setSelectedConversation(conversation)}
              className={`flex items-center gap-3 p-3 md:p-4 cursor-pointer hover:bg-[#1a1a1a] transition-colors ${
                selectedConversation?.id === conversation.id ? "bg-[#1a1a1a]" : ""
              }`}
            >
              <img
                src={conversation.user.avatar}
                alt={conversation.user.nickname}
                className="w-10 h-10 md:w-12 md:h-12 rounded-full"
              />
              <div className="flex-1 min-w-0">
                <div className="font-semibold truncate">
                  {conversation.user.nickname}
                </div>
                <div className="text-sm text-gray-400">{conversation.lastMessageTime}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right Panel - Chat Screen */}
      <div className={`${selectedConversation ? 'flex' : 'hidden md:flex'} flex-1 flex-col`}>
        {selectedConversation ? (
          <>
            {/* Chat Header */}
            <div className="flex items-center gap-3 p-3 md:p-4 border-b border-border bg-[#121212]">
              {/* Back Button (Mobile) */}
              <button
                onClick={() => setSelectedConversation(null)}
                className="md:hidden p-2 hover:bg-[#1a1a1a] rounded-full"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <img
                src={selectedConversation.user.avatar}
                alt={selectedConversation.user.nickname}
                className="w-10 h-10 rounded-full"
              />
              <div>
                <div className="font-semibold">{selectedConversation.user.nickname}</div>
                <div className="text-sm text-gray-400">{selectedConversation.user.username}</div>
              </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-3 md:p-4">
              {messages.length === 0 && (
                <div className="flex items-center justify-center h-full text-gray-500">
                  메시지를 보내보세요
                </div>
              )}
              {messages.map((msg) => (
                <div key={msg.id} className="mb-4">
                  <div className="bg-[#2a2a2a] rounded-lg p-3 inline-block max-w-[70%]">
                    {msg.text}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">{msg.timestamp}</div>
                </div>
              ))}
            </div>

            {/* Message Input */}
            <div className="p-3 md:p-4 border-t border-border bg-[#121212] relative">
              <div className="flex items-center gap-2">
                <Input
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                  placeholder="메시지 보내기..."
                  className="flex-1 bg-[#2a2a2a] border-none text-white placeholder:text-gray-500"
                />
                <Button
                  onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                  variant="ghost"
                  size="icon"
                  className="text-gray-400 hover:text-white"
                >
                  <Smile className="w-5 h-5" />
                </Button>
              </div>

              {/* Emoji Picker */}
              {showEmojiPicker && (
                <div className="absolute bottom-16 right-4 bg-[#2a2a2a] rounded-lg p-4 shadow-lg border border-border">
                  <div className="grid grid-cols-7 gap-2 w-[280px]">
                    {emojis.map((emoji, index) => (
                      <button
                        key={index}
                        onClick={() => handleEmojiClick(emoji)}
                        className="text-2xl hover:bg-[#3a3a3a] rounded p-1 transition-colors"
                      >
                        {emoji}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            대화를 선택하세요
          </div>
        )}
      </div>
    </div>
  );
}

