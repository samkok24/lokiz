import { useEffect } from "react";
import { useLocation } from "wouter";
import { useAuthStore } from "@/lib/store/authStore";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const [, setLocation] = useLocation();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      // 로그인하지 않은 경우 홈으로 리다이렉트 (로그인 모달이 열림)
      setLocation("/");
    }
  }, [isAuthenticated, setLocation]);

  // 로그인되지 않은 경우 아무것도 렌더링하지 않음
  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}

