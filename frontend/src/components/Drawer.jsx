import { useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { X } from "lucide-react";

/** Accessible right-side drawer with focus on open and Esc to close. */
export default function Drawer({ open, onClose, title, subtitle, children, footer, width = "max-w-xl" }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50">
          <motion.div className="absolute inset-0 bg-primary/30" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose} />
          <motion.aside
            role="dialog" aria-modal="true" aria-label={title}
            initial={{ x: "100%" }} animate={{ x: 0 }} exit={{ x: "100%" }}
            transition={{ type: "tween", duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
            className={`absolute right-0 top-0 flex h-full w-full ${width} flex-col bg-background shadow-[var(--shadow-pop)]`}
          >
            <header className="flex items-start justify-between gap-4 border-b bg-card px-5 py-4">
              <div className="min-w-0">
                <h2 className="truncate text-base font-semibold">{title}</h2>
                {subtitle && <p className="mt-0.5 text-xs text-muted-foreground">{subtitle}</p>}
              </div>
              <button autoFocus onClick={onClose} aria-label="Close panel" className="rounded-md p-1.5 text-muted-foreground hover:bg-muted"><X className="size-4" /></button>
            </header>
            <div className="flex-1 overflow-y-auto p-5">{children}</div>
            {footer && <footer className="border-t bg-card px-5 py-3">{footer}</footer>}
          </motion.aside>
        </div>
      )}
    </AnimatePresence>
  );
}
