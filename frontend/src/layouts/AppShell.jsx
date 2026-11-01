import { Link } from "@tanstack/react-router";
import { Send } from "lucide-react";
import Logo from "@/components/Logo";

export default function AppShell({ children }) {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4 sm:px-6">
          <Link to="/" aria-label="CircularRoute home"><Logo inverted={false} /></Link>
          <span className="inline-flex items-center gap-2 text-sm text-muted-foreground"><Send className="size-4" />Circular mail routing</span>
        </div>
      </header>
      <div className="px-4 py-8 sm:px-6 sm:py-12">{children}</div>
    </div>
  );
}
