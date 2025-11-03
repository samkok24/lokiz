import { useState } from "react";
import { Link, useLocation } from "wouter";
import { Home, Compass, Users, MessageCircle, PlusSquare, User, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/lib/store/authStore";
import LoginModal from "@/components/LoginModal";

export default function Sidebar() {
  const [location] = useLocation();
  const { user, isAuthenticated } = useAuthStore();
  const [loginModalOpen, setLoginModalOpen] = useState(false);

  const navItems = [
    { icon: Home, label: "추천", path: "/" },
    { icon: Compass, label: "탐색", path: "/explore" },
    { icon: Users, label: "팔로잉", path: "/following" },
    { icon: MessageCircle, label: "메시지", path: "/messages" },
  ];

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-black border-r border-border flex flex-col">
      {/* Logo */}
      <div className="p-6">
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-2xl font-bold text-primary">LOKIZ</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location === item.path;
          
          return (
            <Link 
              key={item.path} 
              href={item.path}
              className={`
                flex items-center space-x-4 px-4 py-3 rounded-lg mb-1
                transition-colors duration-200
                ${isActive 
                  ? "bg-muted text-primary font-semibold" 
                  : "text-foreground hover:bg-muted/50"
                }
              `}
            >
              <Icon className="w-6 h-6" />
              <span className="text-base">{item.label}</span>
            </Link>
          );
        })}

        {/* Upload Button */}
        {isAuthenticated && (
          <Link 
            href="/upload"
            className="flex items-center space-x-4 px-4 py-3 rounded-lg mb-1 text-foreground hover:bg-muted/50 transition-colors"
          >
            <PlusSquare className="w-6 h-6" />
            <span className="text-base">업로드</span>
          </Link>
        )}

        {/* Profile */}
        {isAuthenticated && user && (
          <Link 
            href={`/profile/${user.id}`}
            className="flex items-center space-x-4 px-4 py-3 rounded-lg mb-1 text-foreground hover:bg-muted/50 transition-colors"
          >
            <User className="w-6 h-6" />
            <span className="text-base">프로필</span>
          </Link>
        )}

        {/* Settings */}
        {isAuthenticated && (
          <Link 
            href="/settings"
            className="flex items-center space-x-4 px-4 py-3 rounded-lg mb-1 text-foreground hover:bg-muted/50 transition-colors"
          >
            <Settings className="w-6 h-6" />
            <span className="text-base">설정</span>
          </Link>
        )}
      </nav>

      {/* Login Button */}
      {!isAuthenticated && (
        <div className="p-4 border-t border-border">
          <Button 
            variant="default" 
            className="w-full"
            onClick={() => setLoginModalOpen(true)}
          >
            로그인
          </Button>
        </div>
      )}

      {/* Login Modal */}
      <LoginModal
        isOpen={loginModalOpen}
        onClose={() => setLoginModalOpen(false)}
      />

      {/* Footer */}
      <div className="p-4 text-xs text-muted-foreground">
        <div className="space-y-1">
          <a href="#" className="hover:text-foreground">프로그램</a>
          <span className="mx-2">·</span>
          <a href="#" className="hover:text-foreground">약관 및 정책</a>
        </div>
        <div className="mt-2">
          © 2025 LOKIZ
        </div>
      </div>
    </aside>
  );
}

