import { useState } from "react";
import { Link, useRouterState } from "@tanstack/react-router";
import { motion, AnimatePresence } from "motion/react";
import {
  LayoutDashboard, FileText, UploadCloud, Users, ShieldCheck, Send, ScrollText, BookUser, Settings,
  PanelLeftClose, PanelLeftOpen, Search, Menu, X, LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";
import Logo from "@/components/Logo";
import SearchCommand from "@/components/SearchCommand";
import NotificationCenter from "@/components/NotificationCenter";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

const NAV = [
  { to: "/", label: "Overview", icon: LayoutDashboard, exact: true },
  { to: "/circulars", label: "Circulars", icon: FileText },
  { to: "/upload", label: "Upload Circular", icon: UploadCloud },
  { to: "/recipients", label: "Recipients", icon: Users },
  { to: "/approvals", label: "Approvals", icon: ShieldCheck, badge: 2 },
  { to: "/distribution", label: "Distribution", icon: Send },
  { to: "/audit", label: "Audit Logs", icon: ScrollText },
];
const SYSTEM = [
  { to: "/directory", label: "Institutional Directory", icon: BookUser },
  { to: "/settings", label: "Settings", icon: Settings },
];

function NavItem({ item, collapsed, onNavigate }) {
  const Icon = item.icon;
  return (
    <Link
      to={item.to}
      onClick={onNavigate}
      activeOptions={{ exact: !!item.exact }}
      title={collapsed ? item.label : undefined}
      className="group relative flex h-9 items-center gap-3 rounded-md px-2.5 text-sm text-navy-muted transition-colors hover:bg-navy-foreground/5 hover:text-navy-foreground data-[status=active]:bg-navy-foreground/10 data-[status=active]:text-navy-foreground"
    >
      {({ isActive }) => (
        <>
          {isActive && <motion.span layoutId="nav-indicator" className="absolute left-0 top-2 bottom-2 w-0.5 rounded-full bg-brand" />}
          <Icon className="size-[18px] shrink-0" />
          {!collapsed && <span className="flex-1 truncate">{item.label}</span>}
          {!collapsed && item.badge && <span className="tabular rounded bg-warning px-1.5 text-[10px] font-semibold text-primary">{item.badge}</span>}
        </>
      )}
    </Link>
  );
}

function SidebarContent({ collapsed, onNavigate, onToggle }) {
  return (
    <div className="flex h-full flex-col bg-navy">
      <div className={cn("flex h-14 items-center border-b border-navy-foreground/10", collapsed ? "justify-center px-2" : "justify-between px-4")}>
        <Link to="/" onClick={onNavigate}><Logo collapsed={collapsed} /></Link>
        {onToggle && !collapsed && (
          <button onClick={onToggle} aria-label="Collapse sidebar" className="rounded p-1 text-navy-muted hover:text-navy-foreground"><PanelLeftClose className="size-4" /></button>
        )}
      </div>
      <nav className="flex-1 space-y-0.5 overflow-y-auto p-3" aria-label="Main">
        {NAV.map((n) => <NavItem key={n.to} item={n} collapsed={collapsed} onNavigate={onNavigate} />)}
        <div className={cn("pb-2 pt-6 text-[10px] font-semibold uppercase tracking-[0.1em] text-navy-muted/70", collapsed ? "text-center" : "px-2.5")}>{collapsed ? "—" : "System"}</div>
        {SYSTEM.map((n) => <NavItem key={n.to} item={n} collapsed={collapsed} onNavigate={onNavigate} />)}
      </nav>
      {onToggle && collapsed && (
        <button onClick={onToggle} aria-label="Expand sidebar" className="mx-auto mb-2 rounded p-1.5 text-navy-muted hover:text-navy-foreground"><PanelLeftOpen className="size-4" /></button>
      )}
      <div className={cn("flex items-center gap-3 border-t border-navy-foreground/10 p-3", collapsed && "justify-center")}>
        <div className="flex size-8 shrink-0 items-center justify-center rounded-md bg-navy-foreground/10 text-xs font-semibold text-navy-foreground">AD</div>
        {!collapsed && (
          <div className="min-w-0 leading-tight">
            <div className="truncate text-sm font-medium text-navy-foreground">Administrator</div>
            <div className="truncate text-xs text-navy-muted">MSRIT / Institution</div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function AppShell({ children }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <div className="flex min-h-screen bg-background">
      <motion.aside
        animate={{ width: collapsed ? 64 : 248 }}
        transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
        className="sticky top-0 hidden h-screen shrink-0 overflow-hidden lg:block"
      >
        <SidebarContent collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
      </motion.aside>

      <AnimatePresence>
        {mobileOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <motion.div className="absolute inset-0 bg-primary/40" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setMobileOpen(false)} />
            <motion.div className="absolute inset-y-0 left-0 w-72" initial={{ x: "-100%" }} animate={{ x: 0 }} exit={{ x: "-100%" }} transition={{ type: "tween", duration: 0.22 }}>
              <SidebarContent collapsed={false} onNavigate={() => setMobileOpen(false)} />
              <button onClick={() => setMobileOpen(false)} aria-label="Close menu" className="absolute right-3 top-4 rounded p-1 text-navy-muted"><X className="size-4" /></button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b bg-card/95 px-4 backdrop-blur sm:px-6">
          <button onClick={() => setMobileOpen(true)} aria-label="Open menu" className="rounded-md p-2 text-muted-foreground hover:bg-muted lg:hidden"><Menu className="size-5" /></button>
          <button
            onClick={() => setSearchOpen(true)}
            className="flex h-9 w-full max-w-md items-center gap-2 rounded-md border bg-surface px-3 text-sm text-muted-foreground transition hover:border-input"
          >
            <Search className="size-4" />
            <span className="flex-1 truncate text-left">Search circulars, recipients…</span>
            <kbd className="hidden rounded border bg-card px-1.5 font-mono text-[10px] sm:inline">Ctrl K</kbd>
          </button>
          <div className="ml-auto flex items-center gap-1">
            <NotificationCenter />
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button aria-label="Profile menu" className="ml-1 flex size-8 items-center justify-center rounded-md bg-primary text-xs font-semibold text-primary-foreground">?</button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>
                  <div className="text-sm">Account</div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild><Link to="/settings"><Settings className="size-4" />Settings</Link></DropdownMenuItem>
                <DropdownMenuItem asChild><Link to="/login"><LogOut className="size-4" />Sign in</Link></DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>
        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
          <motion.div key={pathname} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.22, ease: "easeOut" }} className="mx-auto max-w-[1400px]">
            {children}
          </motion.div>
        </main>
      </div>
      <SearchCommand open={searchOpen} setOpen={setSearchOpen} />
    </div>
  );
}
