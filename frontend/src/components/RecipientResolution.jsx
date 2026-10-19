import { motion } from "motion/react";
import { Check, FileText, PenTool, AlertCircle, Quote } from "lucide-react";
import { cn } from "@/lib/utils";
import ConfidenceScore from "./ConfidenceScore";

export function RecipientCard({ recipient, index = 0 }) {
  const isHandwritten = recipient.type === "handwritten";
  const confidenceVal = recipient.confidence
    ? Math.round(recipient.confidence <= 1 ? recipient.confidence * 100 : recipient.confidence)
    : null;

  return (
    <motion.li
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.03 }}
      className="rounded-lg border bg-card p-3 shadow-xs"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <span
            className={cn(
              "flex size-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold",
              isHandwritten
                ? "bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300"
                : "bg-brand-soft text-brand"
            )}
          >
            {isHandwritten ? <PenTool className="size-3.5" /> : <FileText className="size-3.5" />}
          </span>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="truncate text-sm font-semibold text-foreground">
                {recipient.text || recipient.raw_text}
              </span>
              <span
                className={cn(
                  "rounded px-1.5 py-0.5 text-[10px] font-medium border uppercase tracking-wide",
                  isHandwritten
                    ? "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300"
                    : "bg-surface text-muted-foreground border-border"
                )}
              >
                {recipient.type}
              </span>
            </div>
            {recipient.raw_text && recipient.raw_text !== recipient.text && (
              <div className="truncate text-xs text-muted-foreground mt-0.5">
                Raw Extracted: <span className="font-mono text-foreground font-normal">"{recipient.raw_text}"</span>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3">
          {recipient.source_page && (
            <span className="rounded border bg-surface px-2 py-0.5 font-mono text-xs text-muted-foreground">
              Page {recipient.source_page}
            </span>
          )}
          {confidenceVal !== null && <ConfidenceScore value={confidenceVal} />}
        </div>
      </div>
    </motion.li>
  );
}

function Step({ n, title, children }) {
  return (
    <div className="card-surface p-5">
      <div className="mb-3 flex items-center gap-2">
        <span className="flex size-5 items-center justify-center rounded bg-primary font-mono text-[10px] font-semibold text-primary-foreground">
          {n}
        </span>
        <span className="label-caps">{title}</span>
      </div>
      {children}
    </div>
  );
}

export default function RecipientResolution({ circular, data }) {
  // Support both circular prop and legacy data prop
  const source = circular || data || {};
  const recipientsList = source.recipients || [];
  const copyToFound = source.copy_to_found;
  const copyToPages = source.copy_to_pages || [];
  const handwrittenText = source.handwritten_text || [];

  return (
    <div className="space-y-4">
      <Step n="1" title={`Extracted Recipients from Copy-To Section (${recipientsList.length})`}>
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            {copyToFound ? (
              <span className="inline-flex items-center gap-1.5 font-medium text-success">
                <Check className="size-4" strokeWidth={2.5} />
                Copy-To Header Detected {copyToPages.length > 0 && `(Page ${copyToPages.join(", ")})`}
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 font-medium text-warning">
                <AlertCircle className="size-4" />
                No Copy-To header detected
              </span>
            )}
          </div>
          <span className="font-mono">{recipientsList.length} recipient phrase(s) extracted</span>
        </div>

        {recipientsList.length > 0 ? (
          <ul className="space-y-2.5">
            {recipientsList.map((r, i) => (
              <RecipientCard key={i} recipient={r} index={i} />
            ))}
          </ul>
        ) : (
          <div className="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
            {copyToFound
              ? "Copy-To section was located, but no individual recipient entries were extracted."
              : "No Copy-To distribution section was detected in this circular."}
          </div>
        )}

        {handwrittenText.length > 0 && (
          <div className="mt-4 border-t pt-4">
            <div className="label-caps mb-2 text-xs">Handwritten Additions (TrOCR)</div>
            <div className="flex flex-wrap gap-2">
              {handwrittenText.map((hw, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1.5 rounded-md border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs text-amber-900 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-200"
                >
                  <PenTool className="size-3" />
                  <span className="font-medium">{hw.text}</span>
                  {hw.source_page && <span className="opacity-75 font-mono text-[10px]">(P.{hw.source_page})</span>}
                </span>
              ))}
            </div>
          </div>
        )}
      </Step>
    </div>
  );
}
