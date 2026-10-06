import { motion } from "motion/react";
import { cn } from "@/lib/utils";

const TONES = {
  Distributed: "bg-success-soft text-success",
  Delivered: "bg-success-soft text-success",
  Completed: "bg-success-soft text-success",
  Active: "bg-success-soft text-success",
  Processing: "bg-brand-soft text-brand",
  Sending: "bg-brand-soft text-brand",
  "Pending Approval": "bg-warning-soft text-warning",
  Pending: "bg-warning-soft text-warning",
  Retrying: "bg-warning-soft text-warning",
  "On Leave": "bg-warning-soft text-warning",
  Failed: "bg-danger-soft text-danger",
  Draft: "bg-muted text-muted-foreground",
  Inactive: "bg-muted text-muted-foreground",
};

const PULSE = new Set(["Processing", "Sending", "Retrying"]);

export default function StatusBadge({ status, className }) {
  const tone = TONES[status] || "bg-muted text-muted-foreground";
  return (
    <motion.span
      key={status}
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.18 }}
      className={cn("inline-flex items-center gap-1.5 whitespace-nowrap rounded-full px-2 py-0.5 text-xs font-medium", tone, className)}
    >
      <span className="relative flex size-1.5">
        {PULSE.has(status) && <span className="absolute inline-flex size-full animate-ping rounded-full bg-current opacity-60" />}
        <span className="relative inline-flex size-1.5 rounded-full bg-current" />
      </span>
      {status}
    </motion.span>
  );
}
