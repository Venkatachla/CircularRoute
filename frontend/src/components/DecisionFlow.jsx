import { motion } from "motion/react";
import { ShieldCheck, AlertTriangle, Send, UserCheck, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { AUTO_THRESHOLD } from "@/utils/format";
import { AnimatedNumber } from "./ConfidenceScore";

/** Confidence → decision → outcome. Horizontal on desktop, stacked on mobile. */
export default function DecisionFlow({ confidence }) {
  const high = confidence >= AUTO_THRESHOLD;
  const nodes = [
    { label: "Confidence score", value: <><AnimatedNumber value={confidence} />%</>, tone: high ? "text-success" : "text-warning" },
    {
      label: high ? "High confidence" : "Low confidence",
      value: high ? "Automatically approved" : "Human approval required",
      icon: high ? ShieldCheck : AlertTriangle,
      tone: high ? "text-success" : "text-warning",
      bg: high ? "bg-success-soft" : "bg-warning-soft",
    },
    {
      label: "Outcome",
      value: high ? "Email distribution" : "Approval Center",
      icon: high ? Send : UserCheck,
      tone: "text-brand",
      bg: "bg-brand-soft",
    },
  ];
  return (
    <div className="card-surface p-5">
      <div className="mb-4 flex items-center justify-between">
        <span className="label-caps">Decision flow</span>
        <span className="font-mono text-xs text-muted-foreground">threshold ≥ {AUTO_THRESHOLD}%</span>
      </div>
      <div className="flex flex-col items-stretch gap-2 md:flex-row md:items-center">
        {nodes.map((n, i) => {
          const Icon = n.icon;
          return (
            <div key={i} className="contents">
              <motion.div
                initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 + i * 0.25, duration: 0.25 }}
                className={cn("flex flex-1 items-center gap-3 rounded-lg border p-3", n.bg)}
              >
                {Icon && <Icon className={cn("size-5 shrink-0", n.tone)} />}
                <div className="min-w-0">
                  <div className="label-caps">{n.label}</div>
                  <div className={cn("tabular mt-0.5 text-sm font-semibold", i === 0 && "text-xl", n.tone)}>{n.value}</div>
                </div>
              </motion.div>
              {i < nodes.length - 1 && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 + i * 0.25 }} className="flex justify-center text-muted-foreground">
                  <ArrowRight className="size-4 rotate-90 md:rotate-0" />
                </motion.div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
