import { useState } from "react";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { toast } from "sonner";
import { authAPI } from "@/lib/api/auth";
import { useAuthStore } from "@/lib/store/authStore";

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function LoginModal({ isOpen, onClose }: LoginModalProps) {
  const [, setLocation] = useLocation();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await authAPI.login({ username: formData.username, password: formData.password });
      
      if (result.user && result.access_token) {
        setAuth(result.user, result.access_token);
        toast.success("로그인 성공!");
        onClose();
        setLocation("/");
      } else {
        toast.error("로그인에 실패했습니다.");
      }
    } catch (error) {
      toast.error("로그인 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-center text-3xl font-bold text-primary">
            Lokiz
          </DialogTitle>
        </DialogHeader>

        <div className="text-center text-muted-foreground mb-4">
          로그인하여 시작하세요
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="username">사용자명</Label>
            <Input
              id="username"
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
              disabled={loading}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">비밀번호</Label>
            <Input
              id="password"
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
              disabled={loading}
            />
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "로그인 중..." : "로그인"}
          </Button>
        </form>

        <div className="text-center text-sm text-muted-foreground mt-4">
          계정이 없으신가요?{" "}
          <button
            onClick={() => {
              onClose();
              setLocation("/register");
            }}
            className="text-primary hover:underline"
          >
            회원가입
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

