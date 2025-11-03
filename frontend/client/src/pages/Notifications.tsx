import { Heart, MessageCircle, UserPlus, Mail, Bell } from "lucide-react";
import { mockNotifications } from "@shared/mockData";
import type { Notification } from "@shared/types";

const getNotificationIcon = (type: Notification['type']) => {
  switch (type) {
    case "like":
      return <Heart className="w-5 h-5 text-[#FE2C55]" />;
    case "comment":
      return <MessageCircle className="w-5 h-5 text-blue-500" />;
    case "follow":
      return <UserPlus className="w-5 h-5 text-green-500" />;
    case "message":
      return <Mail className="w-5 h-5 text-purple-500" />;
    case "system":
      return <Bell className="w-5 h-5 text-yellow-500" />;
    default:
      return <Bell className="w-5 h-5 text-gray-500" />;
  }
};

export default function Notifications() {
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-2xl mx-auto py-6">
        <h1 className="text-2xl font-bold mb-6 px-4">알림</h1>

        <div className="space-y-1">
          {mockNotifications.map((notification) => (
            <div
              key={notification.id}
              className={`flex items-start gap-3 p-4 hover:bg-[#1a1a1a] transition-colors cursor-pointer ${
                !notification.isRead ? "bg-[#1a1a1a]" : ""
              }`}
            >
              {/* Icon */}
              <div className="flex-shrink-0 mt-1">
                {getNotificationIcon(notification.type)}
              </div>

              {/* User Avatar */}
              {notification.user && (
                <img
                  src={notification.user.avatar}
                  alt={notification.user.username}
                  className="w-10 h-10 rounded-full flex-shrink-0"
                />
              )}

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="text-sm">
                  {notification.user && (
                    <span className="font-semibold">{notification.user.nickname}</span>
                  )}
                  <span className="text-gray-400 ml-1">{notification.message}</span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {new Date(notification.createdAt).toLocaleDateString('ko-KR', {
                    month: 'numeric',
                    day: 'numeric',
                    hour: 'numeric',
                    minute: 'numeric'
                  })}
                </div>
              </div>

              {/* Video Thumbnail (if applicable) */}
              {notification.video && (
                <img
                  src={notification.video.thumbnailUrl}
                  alt="Video thumbnail"
                  className="w-12 h-16 rounded object-cover flex-shrink-0"
                />
              )}

              {/* Unread Indicator */}
              {!notification.isRead && (
                <div className="w-2 h-2 bg-[#FE2C55] rounded-full flex-shrink-0 mt-2" />
              )}
            </div>
          ))}
        </div>

        {mockNotifications.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-gray-400">
            <Bell className="w-16 h-16 mb-4 text-gray-600" />
            <p className="text-sm">알림이 없습니다</p>
          </div>
        )}
      </div>
    </div>
  );
}

