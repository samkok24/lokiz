import { Link } from "wouter";
import { Button } from "@/components/ui/button";

/**
 * All content in this page are only for example, delete if unneeded
 * When building pages, remember your instructions in Frontend Best Practices, Design Guide and Common Pitfalls
 */
export default function Home() {
  return (
    <div className="min-h-screen">
      <div className="container mx-auto py-8">
        <h1 className="text-3xl font-bold mb-4">For You</h1>
        <p className="text-muted-foreground mb-4">피드가 여기에 표시됩니다.</p>
        <Link href="/profile/1">
          <Button variant="default">프로필 페이지 보기</Button>
        </Link>
      </div>
    </div>
  );
}
