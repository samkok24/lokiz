import { Search, Bell, User } from "lucide-react";
import { Link, useLocation } from "wouter";
import { useAuthStore } from "@/lib/store/authStore";
import { APP_LOGO, APP_TITLE } from "@/const";
import { useState } from "react";

export default function Header() {
  const [, setLocation] = useLocation();
  const { isAuthenticated } = useAuthStore();
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setLocation(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-black border-b border-gray-800 h-16">
      <div className="container mx-auto h-full flex items-center justify-between px-4">
        {/* 로고 */}
        <Link href="/">
          <div className="flex items-center gap-2 cursor-pointer">
            <img src={APP_LOGO} alt={APP_TITLE} className="h-8 w-8" />
            <span className="text-xl font-bold text-[#D0FF00]">lokiz</span>
          </div>
        </Link>

        {/* 검색 바 */}
        <form onSubmit={handleSearch} className="flex-1 max-w-md mx-4 md:mx-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 md:w-5 md:h-5 text-gray-400" />
            <input
              type="text"
              placeholder="검색"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 md:pl-10 pr-3 md:pr-4 py-1.5 md:py-2 bg-gray-900 border border-gray-700 rounded-full text-xs md:text-sm focus:outline-none focus:border-[#D0FF00] transition-colors"
            />
          </div>
        </form>

        {/* 우측 아이콘 */}
        {isAuthenticated && (
          <div className="hidden md:flex items-center gap-4">
            {/* 알림 */}
            <Link href="/notifications">
              <div className="relative p-2 hover:bg-gray-800 rounded-full transition-colors cursor-pointer">
                <Bell className="w-6 h-6" />
                {/* 읽지 않은 알림 배지 */}
                <span className="absolute top-1 right-1 w-2 h-2 bg-[#FE2C55] rounded-full"></span>
              </div>
            </Link>

            {/* 프로필 */}
            <Link href="/profile/me">
              <div className="p-2 hover:bg-gray-800 rounded-full transition-colors cursor-pointer">
                <User className="w-6 h-6" />
              </div>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
}

