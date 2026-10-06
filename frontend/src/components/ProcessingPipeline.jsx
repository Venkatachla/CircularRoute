import { motion, AnimatePresence } from "motion/react";
import {
  Check, Upload, Wand2, ScanText, Brain, Table2, Users, ShieldCheck, Gauge, Send, Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";

const ICONS = { upload: Upload, pre: Wand2, ocr: ScanText, understand: Brain, extract: Table2, resolve: Users, validate: ShieldCheck, decide: Gauge, distribute: Send };

/**
 * CircularRoute's signature visual: a vertical, live processing pipeline.
 * stages: [{key,label,desc}], current: index of active stage, times: {key: seconds}
 */
export default function ProcessingPipeline({ stages, current, times = {}, compact = false }) {
  return (
    <ol className="relative" aria-label="Processing pipeline">
      {stages.map((s, i) => {
        const state = i < current ? "done" : i === current ? "active" : "idle";
        const Icon = ICONS[s.key] || Check;
        const last = i === stages.length - 1;
        return (
          <li key={s.key} className="relative flex gap-4 pb-5 last:pb-0" aria-current={state === "active" ? "step" : undefined}>
            {!last && (
              <div className="absolute left-[15px] top-8 bottom-0 w-px bg-border">
                <motion.div
                  className="w-full bg-brand"
                  initial={{ height: 0 }}
                  animate={{ height: state === "done" ? "100%" : 0 }}
                  transition={{ duration: 0.35, ease: "easeOut" }}
                />
              </div>
            )}
            <div
              className={cn(
                "relative z-10 flex size-8 shrink-0 items-center justify-center rounded-full border transition-colors duration-300",
                state === "done" && "border-brand bg-brand text-brand-foreground",
                state === "active" && "border-brand bg-card text-brand ring-4 ring-brand-soft",
                state === "idle" && "border-border bg-card text-muted-foreground",
              )}
            >
              <AnimatePresence mode="wait" initial={false}>
                {state === "done" ? (
                  <motion.span key="d" initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.18 }}>
                    <Check className="size-4" strokeWidth={2.5} />
                  </motion.span>
                ) : state === "active" ? (
                  <motion.span key="a" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <Loader2 className="size-4 animate-spin" />
                  </motion.span>
                ) : (
                  <motion.span key="i" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <Icon className="size-3.5" />
                  </motion.span>
                )}
              </AnimatePresence>
            </div>
            <div className="min-w-0 flex-1 pt-1">
              <div className="flex items-baseline justify-between gap-3">
                <span className={cn("text-sm font-medium", state === "idle" ? "text-muted-foreground" : "text-foreground")}>{s.label}</span>
                <span className="tabular font-mono text-xs text-muted-foreground">
                  {state === "done" && times[s.key] != null ? `${times[s.key].toFixed(2)}s` : state === "active" ? "running" : state === "idle" ? "queued" : ""}
                </span>
              </div>
              {!compact && <p className="mt-0.5 text-xs text-muted-foreground">{s.desc}</p>}
              {state === "active" && (
                <div className="mt-2 h-0.5 overflow-hidden rounded-full bg-brand-soft">
                  <motion.div className="h-full w-1/3 bg-brand" animate={{ x: ["-100%", "300%"] }} transition={{ duration: 1.1, repeat: Infinity, ease: "easeInOut" }} />
                </div>
              )}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
