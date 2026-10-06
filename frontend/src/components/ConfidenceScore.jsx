import { motion, animate, useMotionValue, useTransform } from "motion/react";
import { useEffect } from "react";
import { cn } from "@/lib/utils";
import { confidenceTone } from "@/utils/format";

const STROKE = { success: "stroke-success", warning: "stroke-warning", danger: "stroke-danger" };
const TEXT = { success: "text-success", warning: "text-warning", danger: "text-danger" };
const BG = { success: "bg-success", warning: "bg-warning", danger: "bg-danger" };

function AnimatedNumber({ value, decimals = 1 }) {
  const mv = useMotionValue(0);
  const text = useTransform(mv, (v) => v.toFixed(decimals));
  useEffect(() => {
    const c = animate(mv, value, { duration: 1, ease: [0.22, 1, 0.36, 1] });
    return c.stop;
  }, [value, mv]);
  return <motion.span>{text}</motion.span>;
}

/** Circular ring indicator. */
export function ConfidenceRing({ value, size = 128, label = "Confidence" }) {
  const tone = confidenceTone(value);
  const r = (size - 12) / 2;
  const c = 2 * Math.PI * r;
  return (
    <div className="relative" style={{ width: size, height: size }} role="img" aria-label={`${label} ${value}%`}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} className="fill-none stroke-muted" strokeWidth="8" />
        <motion.circle
          cx={size / 2} cy={size / 2} r={r} strokeWidth="8" strokeLinecap="round"
          className={cn("fill-none", STROKE[tone])}
          strokeDasharray={c}
          initial={{ strokeDashoffset: c }}
          animate={{ strokeDashoffset: c - (value / 100) * c }}
          transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={cn("tabular text-2xl font-semibold tracking-tight", TEXT[tone])}>
          <AnimatedNumber value={value} />%
        </span>
        <span className="label-caps mt-0.5">{label}</span>
      </div>
    </div>
  );
}

/** Compact inline bar for tables. */
export default function ConfidenceScore({ value, className }) {
  if (!value) return <span className="text-xs text-muted-foreground">—</span>;
  const tone = confidenceTone(value);
  return (
    <div className={cn("flex items-center gap-2", className)} aria-label={`Confidence ${value}%`}>
      <div className="h-1.5 w-14 overflow-hidden rounded-full bg-muted">
        <motion.div
          className={cn("h-full rounded-full", BG[tone])}
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        />
      </div>
      <span className={cn("tabular text-xs font-medium", TEXT[tone])}>{value.toFixed(1)}%</span>
    </div>
  );
}

export function ConfidenceBar({ label, value }) {
  const tone = confidenceTone(value);
  return (
    <div>
      <div className="mb-1 flex justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className={cn("tabular font-medium", TEXT[tone])}>{value}%</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-muted">
        <motion.div className={cn("h-full rounded-full", BG[tone])} initial={{ width: 0 }} animate={{ width: `${value}%` }} transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }} />
      </div>
    </div>
  );
}

export { AnimatedNumber };
