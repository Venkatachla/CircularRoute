import { createFileRoute } from "@tanstack/react-router";
import { toast } from "sonner";
import Logo from "@/components/Logo";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Sign in — CircularRoute" },
      { name: "description", content: "Sign in to the MSRIT circular routing console." },
      { property: "og:title", content: "Sign in — CircularRoute" },
      { property: "og:description", content: "Sign in to the MSRIT circular routing console." },
    ],
  }),
  component: Login,
});

function Login() {
  return (
    <div className="flex min-h-screen">
      <div className="hidden flex-1 flex-col justify-between bg-navy p-10 lg:flex">
        <Logo />
        <p className="max-w-md text-2xl font-semibold text-navy-foreground">Every circular, read, understood and delivered to the right people.</p>
        <span className="text-xs text-navy-muted">Ramaiah Institute of Technology</span>
      </div>
      <form onSubmit={(e) => { e.preventDefault(); toast.error("Sign-in will be available after backend integration."); }} className="m-auto w-full max-w-sm space-y-4 p-6">
        <h1 className="text-2xl font-semibold">Sign in</h1>
        <input type="email" required placeholder="Email" className="h-10 w-full rounded-md border bg-card px-3 text-sm" aria-label="Email" />
        <input type="password" required placeholder="Password" className="h-10 w-full rounded-md border bg-card px-3 text-sm" aria-label="Password" />
        <button className="h-10 w-full rounded-md bg-primary text-sm font-medium text-primary-foreground">Continue</button>
      </form>
    </div>
  );
}
