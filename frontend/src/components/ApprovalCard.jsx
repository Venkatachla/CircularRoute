import { motion } from "motion/react";
import { AlertTriangle, Clock, Users, Check, X, Eye, ShieldAlert, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import ConfidenceScore from "./ConfidenceScore";
import { deptName, formatDate } from "@/utils/format";

export default function ApprovalCard({ circular, onReview, onApprove, onReject, busy }) {
  const isBlocked = Boolean(circular.has_unresolved_recipients || circular.canApprove === false);
  const interpreted = circular.interpreted_recipients || [];
  const allEmails = Array.from(
    new Set(interpreted.flatMap((i) => i.emails || []))
  );

  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: 40, transition: { duration: 0.2 } }}
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
            <span>
              <span className="font-medium">Reason for review: </span>
              {circular.reviewReason || "Manual verification required."}
            </span>
          </div>

          {isBlocked && (
            <div className="mt-2 flex items-center gap-2 rounded-md border border-danger/30 bg-danger-soft px-3 py-1.5 text-xs text-danger">
              <ShieldAlert className="size-4 shrink-0" />
              <span>
                <strong>Approval Blocked:</strong> Unresolved handwritten Copy-To recipients must be corrected before distribution.
              </span>
            </div>
          )}

          {allEmails.length > 0 && (
            <div className="mt-3 text-xs text-muted-foreground">
              <div className="flex items-center gap-1 font-medium text-foreground mb-1">
                <Mail className="size-3.5 text-brand" />
                <span>Final Target Recipients ({allEmails.length}):</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {allEmails.map((email) => (
                  <span key={email} className="rounded bg-surface px-1.5 py-0.5 font-mono text-[11px] border">
                    {email}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-muted-foreground">
            <span>Uploaded by <span className="text-foreground">{circular.uploadedBy || "System"}</span></span>
            <span className="flex items-center gap-1">
              <Users className="size-3.5" />
              {allEmails.length > 0 ? `${allEmails.length} resolved` : (Array.isArray(circular.recipients) ? `${circular.recipients.length} phrases` : "Unresolved")}
            </span>
            <span className="flex items-center gap-1"><Clock className="size-3.5" />{formatDate(circular.date)}</span>
            <ConfidenceScore value={circular.confidence} />
          </div>
        </div>

        <div className="flex shrink-0 flex-col items-end gap-2">
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={onReview}>
              <Eye className="size-3.5" />Review
            </Button>
            <Button variant="outline" size="sm" onClick={onReject} disabled={busy} className="text-danger hover:text-danger">
              <X className="size-3.5" />Reject
            </Button>
            <Button
              size="sm"
              onClick={onApprove}
              disabled={busy || isBlocked}
              title={isBlocked ? "Cannot approve with unresolved recipients" : "Approve and distribute"}
            >
              <Check className="size-3.5" />Approve
            </Button>
          </div>
          {isBlocked && (
            <span className="text-[11px] text-danger">Resolve instructions to unlock</span>
          )}
        </div>
      </div>
    </motion.article>
  );
}
