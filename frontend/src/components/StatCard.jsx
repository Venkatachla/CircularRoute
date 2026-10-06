import { motion } from "motion/react";
import { TrendingUp, AlertTriangle, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatNumber } from "@/utils/format";

function Sparkline({ data, tone }) {
  const w = 96, h = 32;
  const max = Math.max(...data), min = Math.min(...data);
  const pts = data.map((v, i) => [(i / (data.length - 1)) * w, h - ((v - min) / (max - min || 1)) * (h - 4) - 2]);
  const d = pts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
  return (
    <svg width={w} height={h} className={cn("overflow-visible", tone)} aria-hidden>
      <motion.path d={d} fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round"
        initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 1.1, ease: "easeOut" }} />
    </svg>
  );
}

const TREND = {
  up: { icon: TrendingUp, cls: "text-success", spark: "text-brand" },
  warn: { icon: AlertTriangle, cls: "text-warning", spark: "text-warning" },
  down: { icon: TrendingDown, cls: "text-danger", spark: "text-danger" },
};

export default function StatCard({ stat }) {
  const t = TREND[stat.trendDir];
  const Icon = t.icon;
  return (
    <motion.div
      whileHover={{ y: -2, boxShadow: "var(--shadow-lift)" }}
      transition={{ duration: 0.18 }}
      className="card-surface p-5"
    >
      <div className="label-caps">{stat.label}</div>
      <div className="mt-3 flex items-end justify-between gap-3">
        <div className="tabular text-3xl font-semibold tracking-tight">{formatNumber(stat.value)}</div>
        <Sparkline data={stat.spark} tone={t.spark} />
      </div>
      <div className="mt-3 flex items-center gap-1.5 text-xs">
        <Icon className={cn("size-3.5", t.cls)} />
        <span className={cn("font-medium", t.cls)}>{stat.trend}</span>
        <span className="text-muted-foreground">{stat.note}</span>
      </div>
    </motion.div>
  );
}
