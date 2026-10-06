/** CircularRoute mark: a routed path from a source node to three recipients. */
export default function Logo({ collapsed = false, inverted = true }) {
  return (
    <div className="flex items-center gap-2.5">
      <svg width="28" height="28" viewBox="0 0 28 28" aria-hidden className="shrink-0">
        <rect width="28" height="28" rx="7" className="fill-brand" />
        <circle cx="8" cy="14" r="2.5" className="fill-brand-foreground" />
        <path d="M10.5 14 H14 M14 14 C16 14 16 8 19 8 M14 14 H19 M14 14 C16 14 16 20 19 20" className="stroke-brand-foreground" strokeWidth="1.6" fill="none" strokeLinecap="round" />
        <circle cx="20.5" cy="8" r="1.6" className="fill-brand-foreground" />
        <circle cx="20.5" cy="14" r="1.6" className="fill-brand-foreground" />
        <circle cx="20.5" cy="20" r="1.6" className="fill-brand-foreground" />
      </svg>
      {!collapsed && (
        <div className="leading-tight">
          <div className={`text-sm font-semibold tracking-tight ${inverted ? "text-navy-foreground" : "text-foreground"}`}>CircularRoute</div>
          <div className={`text-[10px] ${inverted ? "text-navy-muted" : "text-muted-foreground"}`}>Intelligent Distribution</div>
        </div>
      )}
    </div>
  );
}
