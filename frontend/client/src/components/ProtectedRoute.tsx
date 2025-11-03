import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { useAuthStore } from "@/lib/store/authStore";
import LoginModal from "@/components/LoginModal";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated } = useAuthStore();
  const [, setLocation] = useLocation();
  const [showLoginModal, setShowLoginModal] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      setShowLoginModal(true);
    }
  }, [isAuthenticated]);

  // 로그인되지 않은 경우 로그인 모달 표시
  if (!isAuthenticated) {
    return (
      <>
        <LoginModal 
          isOpen={showLoginModal} 
          onClose={() => {
            setShowLoginModal(false);
            setLocation("/"); // 모달 닫으면 홈으로 이동
          }}
        />
        {/* 로그인 모달 뒤에 페이지 내용을 흐리게 표시 */}
        <div className="blur-sm pointer-events-none">
          {children}
        </div>
      </>
    );
  }

  return <>{children}</>;
}

