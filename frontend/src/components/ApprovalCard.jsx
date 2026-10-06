import { motion } from "motion/react";
import { AlertTriangle, Clock, Users, Check, X, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import ConfidenceScore from "./ConfidenceScore";
import { deptName, formatDate } from "@/utils/format";

export default function ApprovalCard({ circular, onReview, onApprove, onReject, busy }) {
  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, x: 40, transition: { duration: 0.2 } }}
      whileHover={{ boxShadow: "var(--shadow-lift)" }}
      className="card-surface p-5"
    >
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-muted-foreground">{circular.ref}</span>
            <span className="text-xs text-muted-foreground">·</span>
            <span className="text-xs text-muted-foreground">{deptName(circular.dept)}</span>
          </div>
          <h3 className="mt-1 text-base font-semibold tracking-tight">{circular.title}</h3>
          <div className="mt-3 flex items-start gap-2 rounded-md border border-warning/30 bg-warning-soft px-3 py-2 text-sm">
            <AlertTriangle className="mt-0.5 size-4 shrink-0 text-warning" />
            <span><span className="font-medium">Reason for review: </span>{circular.reviewReason}</span>
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-muted-foreground">
            <span>Uploaded by <span className="text-foreground">{circular.uploadedBy}</span></span>
            <span className="flex items-center gap-1"><Users className="size-3.5" />{circular.recipients || "Unresolved"} recipients</span>
            <span className="flex items-center gap-1"><Clock className="size-3.5" />{formatDate(circular.date)}</span>
            <ConfidenceScore value={circular.confidence} />
          </div>
        </div>
        <div className="flex shrink-0 gap-2">
          <Button variant="outline" size="sm" onClick={onReview}><Eye className="size-3.5" />Review</Button>
          <Button variant="outline" size="sm" onClick={onReject} disabled={busy} className="text-danger hover:text-danger"><X className="size-3.5" />Reject</Button>
          <Button size="sm" onClick={onApprove} disabled={busy}><Check className="size-3.5" />Approve</Button>
        </div>
      </div>
    </motion.article>
  );
}
