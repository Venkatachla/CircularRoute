import { createFileRoute, Outlet } from "@tanstack/react-router";
import AppShell from "@/layouts/AppShell";

export const Route = createFileRoute("/_shell")({
  component: ShellLayout,
});

function ShellLayout() {
  return (
    <AppShell>
      <Outlet />
    </AppShell>
  );
}
