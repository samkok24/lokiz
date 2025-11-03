import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { useTheme } from "@/contexts/ThemeContext";
import { Camera, ChevronRight } from "lucide-react";

export default function Settings() {
  const { theme, toggleTheme } = useTheme();
  const [profile, setProfile] = useState({
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=user1",
    nickname: "사용자1",
    username: "user1",
    bio: "안녕하세요! LOKIZ에서 AI 글리치 영상을 만들어보세요.",
    email: "user1@example.com",
  });

  const [privacy, setPrivacy] = useState({
    privateAccount: false,
    allowComments: true,
    allowDM: true,
  });

  const [notifications, setNotifications] = useState({
    likes: true,
    comments: true,
    follows: true,
    messages: true,
  });

  const [activeSection, setActiveSection] = useState<string | null>(null);

  const handleProfileUpdate = () => {
    // TODO: API 연동 시 실제 업데이트 로직 추가
    console.log("Profile updated:", profile);
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container max-w-4xl py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold">설정</h1>
        </div>

        {/* Profile Section */}
        <section className="mb-8 bg-card rounded-lg p-6 border border-border">
          <h2 className="text-xl font-semibold mb-6">프로필 편집</h2>

          {/* Avatar */}
          <div className="mb-6">
            <Label className="mb-2 block">프로필 사진</Label>
            <div className="flex items-center gap-4">
              <div className="relative">
                <img
                  src={profile.avatar}
                  alt="프로필"
                  className="w-24 h-24 rounded-full object-cover"
                />
                <button className="absolute bottom-0 right-0 bg-primary text-primary-foreground p-2 rounded-full hover:bg-primary/90">
                  <Camera className="w-4 h-4" />
                </button>
              </div>
              <div className="text-sm text-muted-foreground">
                <p>JPG, PNG 또는 GIF (최대 2MB)</p>
              </div>
            </div>
          </div>

          {/* Nickname */}
          <div className="mb-4">
            <Label htmlFor="nickname">닉네임</Label>
            <Input
              id="nickname"
              value={profile.nickname}
              onChange={(e) =>
                setProfile({ ...profile, nickname: e.target.value })
              }
              className="mt-2"
            />
          </div>

          {/* Username */}
          <div className="mb-4">
            <Label htmlFor="username">유저명</Label>
            <Input
              id="username"
              value={profile.username}
              onChange={(e) =>
                setProfile({ ...profile, username: e.target.value })
              }
              className="mt-2"
              placeholder="@username"
            />
          </div>

          {/* Bio */}
          <div className="mb-6">
            <Label htmlFor="bio">소개</Label>
            <Textarea
              id="bio"
              value={profile.bio}
              onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
              className="mt-2"
              rows={4}
            />
          </div>

          <Button onClick={handleProfileUpdate} className="bg-[#D0FF00] hover:bg-[#D0FF00]/90 text-black">
            프로필 저장
          </Button>
        </section>

        {/* Account Section */}
        <section className="mb-8 bg-card rounded-lg p-6 border border-border">
          <h2 className="text-xl font-semibold mb-6">계정 설정</h2>

          {/* Email */}
          <div className="mb-4">
            <Label htmlFor="email">이메일</Label>
            <Input
              id="email"
              type="email"
              value={profile.email}
              onChange={(e) =>
                setProfile({ ...profile, email: e.target.value })
              }
              className="mt-2"
            />
          </div>

          {/* Password */}
          <div className="mb-6">
            <button
              onClick={() => setActiveSection(activeSection === "password" ? null : "password")}
              className="flex items-center justify-between w-full text-left"
            >
              <span className="font-medium">비밀번호 변경</span>
              <ChevronRight className={`w-5 h-5 transition-transform ${activeSection === "password" ? "rotate-90" : ""}`} />
            </button>

            {activeSection === "password" && (
              <div className="mt-4 space-y-4">
                <div>
                  <Label htmlFor="current-password">현재 비밀번호</Label>
                  <Input
                    id="current-password"
                    type="password"
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="new-password">새 비밀번호</Label>
                  <Input
                    id="new-password"
                    type="password"
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="confirm-password">새 비밀번호 확인</Label>
                  <Input
                    id="confirm-password"
                    type="password"
                    className="mt-2"
                  />
                </div>
                <Button className="bg-[#D0FF00] hover:bg-[#D0FF00]/90 text-black">
                  비밀번호 변경
                </Button>
              </div>
            )}
          </div>
        </section>

        {/* Privacy Section */}
        <section className="mb-8 bg-card rounded-lg p-6 border border-border">
          <h2 className="text-xl font-semibold mb-6">개인정보 보호</h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">비공개 계정</p>
                <p className="text-sm text-muted-foreground">
                  승인한 팔로워만 내 콘텐츠를 볼 수 있습니다
                </p>
              </div>
              <Switch
                checked={privacy.privateAccount}
                onCheckedChange={(checked) =>
                  setPrivacy({ ...privacy, privateAccount: checked })
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">댓글 허용</p>
                <p className="text-sm text-muted-foreground">
                  다른 사용자가 내 영상에 댓글을 달 수 있습니다
                </p>
              </div>
              <Switch
                checked={privacy.allowComments}
                onCheckedChange={(checked) =>
                  setPrivacy({ ...privacy, allowComments: checked })
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">DM 허용</p>
                <p className="text-sm text-muted-foreground">
                  다른 사용자가 나에게 메시지를 보낼 수 있습니다
                </p>
              </div>
              <Switch
                checked={privacy.allowDM}
                onCheckedChange={(checked) =>
                  setPrivacy({ ...privacy, allowDM: checked })
                }
              />
            </div>
          </div>
        </section>

        {/* Notifications Section */}
        <section className="mb-8 bg-card rounded-lg p-6 border border-border">
          <h2 className="text-xl font-semibold mb-6">알림 설정</h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="font-medium">좋아요 알림</p>
              <Switch
                checked={notifications.likes}
                onCheckedChange={(checked) =>
                  setNotifications({ ...notifications, likes: checked })
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <p className="font-medium">댓글 알림</p>
              <Switch
                checked={notifications.comments}
                onCheckedChange={(checked) =>
                  setNotifications({ ...notifications, comments: checked })
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <p className="font-medium">팔로우 알림</p>
              <Switch
                checked={notifications.follows}
                onCheckedChange={(checked) =>
                  setNotifications({ ...notifications, follows: checked })
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <p className="font-medium">메시지 알림</p>
              <Switch
                checked={notifications.messages}
                onCheckedChange={(checked) =>
                  setNotifications({ ...notifications, messages: checked })
                }
              />
            </div>
          </div>
        </section>

        {/* Theme Section */}
        <section className="mb-8 bg-card rounded-lg p-6 border border-border">
          <h2 className="text-xl font-semibold mb-6">테마 설정</h2>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">다크 모드</p>
              <p className="text-sm text-muted-foreground">
                어두운 테마 사용
              </p>
            </div>
            <Switch
              checked={theme === "dark"}
              onCheckedChange={toggleTheme}
            />
          </div>
        </section>
      </div>
    </div>
  );
}

