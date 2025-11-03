import { Home, Compass, PlusSquare, MessageCircle, User } from "lucide-react";
import { Link, useLocation } from "wouter";

export default function MobileBottomNav() {
  const [location] = useLocation();

  const navItems = [
    { icon: Home, label: "홈", path: "/" },
    { icon: Compass, label: "탐색", path: "/explore" },
    { icon: PlusSquare, label: "업로드", path: "/upload" },
    { icon: MessageCircle, label: "메시지", path: "/messages" },
    { icon: User, label: "프로필", path: "/profile/me" },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-black border-t border-gray-800 h-16">
      <div className="h-full flex items-center justify-around px-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location === item.path;

          return (
            <Link key={item.path} href={item.path}>
              <div
                className={`flex flex-col items-center justify-center w-16 h-full transition-colors cursor-pointer ${
                  isActive ? "text-[#D0FF00]" : "text-gray-400 hover:text-white"
                }`}
              >
                <Icon className="w-6 h-6" />
                <span className="text-xs mt-1">{item.label}</span>
              </div>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

