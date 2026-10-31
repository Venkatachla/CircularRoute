import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Check,
  FileText,
  PenTool,
  AlertCircle,
  AlertTriangle,
  Info,
  ChevronDown,
  ChevronRight,
  Edit3,
  Save,
  X,
  Mail,
  UserCheck,
  ShieldAlert,
  ShieldCheck,
  RefreshCw,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import ConfidenceScore from "./ConfidenceScore";
import { correctHandwriting } from "@/services/circularService";
import { toast } from "sonner";

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

function StatusBadge({ status }) {
  switch (status) {
    case "RESOLVED":
      return (
        <span className="inline-flex items-center gap-1 rounded-md border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-xs font-semibold text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300">
          <Check className="size-3" strokeWidth={2.5} />
          RESOLVED
        </span>
      );
    case "UNRESOLVED":
      return (
        <span className="inline-flex items-center gap-1 rounded-md border border-rose-200 bg-rose-50 px-2 py-0.5 text-xs font-semibold text-rose-700 dark:border-rose-800 dark:bg-rose-950/40 dark:text-rose-300">
          <AlertTriangle className="size-3" />
          UNRESOLVED
        </span>
      );
    case "INFORMATIONAL":
      return (
        <span className="inline-flex items-center gap-1 rounded-md border border-blue-200 bg-blue-50 px-2 py-0.5 text-xs font-semibold text-blue-700 dark:border-blue-800 dark:bg-blue-950/40 dark:text-blue-300">
          <Info className="size-3" />
          INFORMATIONAL
        </span>
      );
    case "MANUALLY CORRECTED":
      return (
        <span className="inline-flex items-center gap-1 rounded-md border border-purple-200 bg-purple-50 px-2 py-0.5 text-xs font-semibold text-purple-700 dark:border-purple-800 dark:bg-purple-950/40 dark:text-purple-300">
          <Edit3 className="size-3" />
          MANUALLY CORRECTED
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center gap-1 rounded-md border border-border bg-surface px-2 py-0.5 text-xs font-semibold text-muted-foreground">
          {status}
        </span>
      );
  }
}

export default function RecipientResolution({ circular, data, onUpdate }) {
  // Support both circular prop and legacy data prop
  const [currCircular, setCurrCircular] = useState(circular || data || {});
  const [expandedIndex, setExpandedIndex] = useState(null);
  const [editingIndex, setEditingIndex] = useState(null);
  const [editValue, setEditValue] = useState("");
  const [isEditingFull, setIsEditingFull] = useState(false);
  const [fullCorrectionValue, setFullCorrectionValue] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  // Sync state if prop changes
  if (circular && circular.id !== currCircular.id) {
    setCurrCircular(circular);
  }

  const recipientsList = currCircular.recipients || [];
  const copyToFound = currCircular.copy_to_found;
  const copyToPages = currCircular.copy_to_pages || [];
  const rawOcrText = currCircular.raw_ocr_text || (currCircular.handwritten_text?.[0]?.raw_ocr_text) || (currCircular.handwritten_text?.[0]?.text) || "";
  const correctedText = currCircular.corrected_text || (currCircular.handwritten_text?.[0]?.corrected_text) || "";
  const cropImage = currCircular.handwritten_crop_image || (currCircular.handwritten_text?.[0]?.crop_image);
  const interpretedRecipients = currCircular.interpreted_recipients || (currCircular.handwritten_text?.[0]?.interpreted_recipients) || [];

  const hasUnresolved = interpretedRecipients.some((r) => r.status === "UNRESOLVED");

  // Handle individual instruction correction
  const handleStartEdit = (index, currentInstruction) => {
    setEditingIndex(index);
    setEditValue(currentInstruction);
  };

  const handleSaveEdit = async (index) => {
    if (!editValue.trim()) return;
    setIsSaving(true);
    try {
      const updated = await correctHandwriting(currCircular.id, {
        instruction_index: index,
        corrected_instruction: editValue.trim(),
      });
      setCurrCircular(updated);
      setEditingIndex(null);
      if (onUpdate) onUpdate(updated);
      toast.success("Instruction updated and recipients re-resolved");
    } catch (err) {
      toast.error(err.message || "Failed to update instruction");
    } finally {
      setIsSaving(false);
    }
  };

  // Handle full corrected text save
  const handleStartFullEdit = () => {
    setFullCorrectionValue(correctedText || rawOcrText);
    setIsEditingFull(true);
  };

  const handleSaveFullEdit = async () => {
    if (!fullCorrectionValue.trim()) return;
    setIsSaving(true);
    try {
      const updated = await correctHandwriting(currCircular.id, {
        corrected_text: fullCorrectionValue.trim(),
      });
      setCurrCircular(updated);
      setIsEditingFull(false);
      if (onUpdate) onUpdate(updated);
      toast.success("Handwritten text corrected and recipients re-resolved against Excel directory");
    } catch (err) {
      toast.error(err.message || "Failed to save correction");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Printed / Extracted Recipients Section */}
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
      </Step>

      {/* 2. Handwritten Extraction & Recipient Resolution Section */}
      <Step n="2" title="Copy To – Handwritten Extraction & Recipient Resolution">
        <div className="space-y-5">
          {/* Safety Status Banner */}
          {hasUnresolved ? (
            <div className="flex items-start gap-3 rounded-lg border border-amber-300 bg-amber-50/80 p-3.5 text-amber-900 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-200">
              <ShieldAlert className="size-5 shrink-0 text-amber-600 dark:text-amber-400 mt-0.5" />
              <div className="text-sm">
                <span className="font-semibold">Approval Blocked: Unresolved Recipients Remain.</span>
                <p className="mt-0.5 text-xs text-amber-800/90 dark:text-amber-300/90">
                  One or more handwritten instructions could not be automatically mapped to a valid directory entry (e.g. unknown abbreviation or missing email).
                  Please use the <strong>Correct</strong> action below to specify a valid identifier or role before approving this circular.
                </p>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-3 rounded-lg border border-emerald-300 bg-emerald-50/80 p-3 text-emerald-900 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-200">
              <ShieldCheck className="size-5 shrink-0 text-emerald-600 dark:text-emerald-400" />
              <div className="text-sm">
                <span className="font-semibold">All Handwritten Recipients Resolved.</span>
                <span className="ml-2 text-xs text-emerald-800/90 dark:text-emerald-300/90">
                  Ready for distribution. All instructions have been validated against the Excel directory.
                </span>
              </div>
            </div>
          )}

          {/* Original Handwritten Crop & Raw OCR Text Display */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Original Crop */}
            <div className="rounded-lg border bg-surface p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="label-caps flex items-center gap-1.5 text-foreground font-semibold">
                    <PenTool className="size-3.5 text-amber-600" />
                    Original Handwritten Crop
                  </span>
                  <span className="rounded bg-muted px-2 py-0.5 text-[10px] font-mono text-muted-foreground">
                    PDF Document Source
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mb-3">
                  Actual image region detected and isolated from the circular's Copy To section:
                </p>
              </div>
              <div className="flex items-center justify-center rounded-md border border-border/80 bg-background/50 p-3 min-h-[90px]">
                {cropImage ? (
                  <img
                    src={cropImage}
                    alt="Original handwritten crop"
                    className="max-h-24 w-auto rounded object-contain shadow-xs border bg-white"
                  />
                ) : (
                  <div className="text-xs text-muted-foreground italic flex items-center gap-1.5">
                    <PenTool className="size-3.5 opacity-60" />
                    Handwritten crop preview loaded
                  </div>
                )}
              </div>
            </div>

            {/* Raw Extracted Handwriting & Correction Fields */}
            <div className="rounded-lg border bg-surface p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="label-caps flex items-center gap-1.5 text-foreground font-semibold">
                    <FileText className="size-3.5 text-brand" />
                    Raw Extracted Handwriting
                  </span>
                  <span className="rounded bg-brand/10 border border-brand/20 px-2 py-0.5 text-[10px] font-mono text-brand font-medium">
                    Immutable TrOCR Output
                  </span>
                </div>
                <div className="rounded-md border bg-card p-2.5 font-mono text-sm font-medium text-foreground">
                  {rawOcrText || <span className="text-muted-foreground italic font-sans text-xs">No handwritten text recognized</span>}
                </div>
              </div>

              {/* Administrator Correction Display / Button */}
              <div className="mt-3 pt-3 border-t">
                {correctedText && correctedText !== rawOcrText ? (
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[11px] font-semibold text-purple-700 dark:text-purple-300 flex items-center gap-1">
                        <Edit3 className="size-3" />
                        Administrator Corrected Text:
                      </span>
                      <Button
                        variant="ghost"
                        size="xs"
                        className="h-6 text-[11px] text-muted-foreground hover:text-foreground"
                        onClick={handleStartFullEdit}
                      >
                        Edit
                      </Button>
                    </div>
                    <div className="rounded border border-purple-200 bg-purple-50/60 p-2 font-mono text-xs text-purple-900 dark:border-purple-900 dark:bg-purple-950/40 dark:text-purple-200">
                      {correctedText}
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Original OCR text is active without overrides.</span>
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-7 text-xs gap-1"
                      onClick={handleStartFullEdit}
                    >
                      <Edit3 className="size-3" />
                      Override Text
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Full Text Edit Dialog / Box */}
          <AnimatePresence>
            {isEditingFull && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden rounded-lg border border-brand/40 bg-brand-soft/20 p-4"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                    <Edit3 className="size-3.5 text-brand" />
                    Correct Full Handwritten Copy-To Text
                  </span>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="size-6 text-muted-foreground"
                    onClick={() => setIsEditingFull(false)}
                  >
                    <X className="size-3.5" />
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground mb-2">
                  Original OCR text is strictly preserved. Enter corrected instructions separated by '&' or commas (e.g. <code>To file & students & faculty & vp</code>):
                </p>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={fullCorrectionValue}
                    onChange={(e) => setFullCorrectionValue(e.target.value)}
                    className="flex-1 rounded-md border border-input bg-card px-3 py-1.5 text-sm font-mono focus:border-brand focus:outline-none"
                    placeholder="e.g. To file & students & staff & vp"
                  />
                  <Button
                    size="sm"
                    className="gap-1.5"
                    onClick={handleSaveFullEdit}
                    disabled={isSaving}
                  >
                    {isSaving ? <RefreshCw className="size-3.5 animate-spin" /> : <Save className="size-3.5" />}
                    Save & Re-resolve
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsEditingFull(false)}
                    disabled={isSaving}
                  >
                    Cancel
                  </Button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Separated Instructions & Recipient Resolution Table */}
          <div className="rounded-lg border bg-card overflow-hidden shadow-xs">
            <div className="border-b bg-muted/40 px-4 py-2.5 flex items-center justify-between">
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-foreground">
                  Separated Instructions & Directory Resolution
                </h4>
                <p className="text-[11px] text-muted-foreground">
                  Individual handwritten items resolved against Excel directory (<code>temp_data.xlsx</code>)
                </p>
              </div>
              <span className="font-mono text-xs text-muted-foreground">
                {interpretedRecipients.length} item(s)
              </span>
            </div>

            {interpretedRecipients.length === 0 ? (
              <div className="p-8 text-center text-sm text-muted-foreground">
                No handwritten instructions detected or parsed.
              </div>
            ) : (
              <div className="divide-y">
                {interpretedRecipients.map((item, idx) => {
                  const isExpanded = expandedIndex === idx;
                  const isEditingThis = editingIndex === idx;
                  const hasEmails = item.emails && item.emails.length > 0;

                  return (
                    <div key={idx} className="transition-colors hover:bg-muted/10">
                      {/* Main Row */}
                      <div className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-3">
                        <div className="flex items-start md:items-center gap-3 flex-1 min-w-0">
                          {/* Toggle Expand Button if has emails */}
                          {hasEmails ? (
                            <button
                              onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                              className="mt-0.5 md:mt-0 p-1 rounded hover:bg-muted text-muted-foreground transition"
                              title={isExpanded ? "Collapse email details" : "Expand email details"}
                            >
                              {isExpanded ? <ChevronDown className="size-4" /> : <ChevronRight className="size-4" />}
                            </button>
                          ) : (
                            <span className="size-6 shrink-0 flex items-center justify-center text-muted-foreground/40">
                              •
                            </span>
                          )}

                          {/* Instruction Token */}
                          <div className="min-w-[120px]">
                            {isEditingThis ? (
                              <div className="flex items-center gap-1.5">
                                <input
                                  type="text"
                                  value={editValue}
                                  onChange={(e) => setEditValue(e.target.value)}
                                  className="w-28 rounded border border-brand bg-background px-2 py-1 text-xs font-mono focus:outline-none"
                                  autoFocus
                                />
                                <Button
                                  size="icon"
                                  variant="ghost"
                                  className="size-6 text-success hover:bg-success/10"
                                  onClick={() => handleSaveEdit(idx)}
                                  disabled={isSaving}
                                  title="Save"
                                >
                                  <Save className="size-3.5" />
                                </Button>
                                <Button
                                  size="icon"
                                  variant="ghost"
                                  className="size-6 text-muted-foreground hover:bg-muted"
                                  onClick={() => setEditingIndex(null)}
                                  disabled={isSaving}
                                  title="Cancel"
                                >
                                  <X className="size-3.5" />
                                </Button>
                              </div>
                            ) : (
                              <div className="flex items-center gap-1.5">
                                <span className="rounded bg-muted px-2 py-1 font-mono text-xs font-semibold text-foreground border">
                                  {item.instruction}
                                </span>
                                {item.raw_text && item.raw_text !== item.instruction && (
                                  <span className="text-[10px] text-muted-foreground font-mono" title="Original raw token">
                                    ({item.raw_text})
                                  </span>
                                )}
                              </div>
                            )}
                          </div>

                          {/* Interpretation Meaning */}
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium text-foreground">
                              {item.interpretation}
                            </div>
                            {item.unresolved_reason && (
                              <div className="text-xs text-rose-600 dark:text-rose-400 mt-0.5 flex items-center gap-1">
                                <AlertTriangle className="size-3 shrink-0" />
                                {item.unresolved_reason}
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Result & Status & Actions */}
                        <div className="flex items-center gap-3 shrink-0 ml-9 md:ml-0">
                          {/* Result */}
                          <div className="text-right min-w-[140px]">
                            <span className="text-xs font-semibold text-foreground">
                              {item.result}
                            </span>
                            {hasEmails && (
                              <button
                                onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                                className="block text-[11px] text-brand hover:underline font-medium"
                              >
                                {isExpanded ? "Hide" : "View"} {item.emails.length} email{item.emails.length > 1 ? "s" : ""}
                              </button>
                            )}
                          </div>

                          {/* Status Badge */}
                          <StatusBadge status={item.status} />

                          {/* Action Button: Edit / Correct */}
                          {!isEditingThis && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-7 text-xs text-muted-foreground hover:text-foreground gap-1"
                              onClick={() => handleStartEdit(idx, item.instruction)}
                              title="Correct this instruction"
                            >
                              <Edit3 className="size-3" />
                              Correct
                            </Button>
                          )}
                        </div>
                      </div>

                      {/* Expandable Email Details Section */}
                      <AnimatePresence>
                        {isExpanded && hasEmails && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                            className="bg-muted/30 border-t px-6 py-3"
                          >
                            <div className="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-1.5">
                              <Mail className="size-3.5 text-brand" />
                              Matched Excel Directory Emails ({item.emails.length}):
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                              {item.emails.map((email, emailIdx) => (
                                <div
                                  key={emailIdx}
                                  className="flex items-center gap-2 rounded border bg-card px-2.5 py-1.5 text-xs font-mono shadow-2xs"
                                >
                                  <UserCheck className="size-3.5 text-emerald-600 shrink-0" />
                                  <span className="truncate text-foreground">{email}</span>
                                </div>
                              ))}
                            </div>
                            {item.matched_faculty && (
                              <div className="mt-2 text-xs text-muted-foreground flex items-center gap-2">
                                <span>Faculty ID: <strong className="text-foreground">{item.matched_faculty.Faculty_id}</strong></span>
                                <span>•</span>
                                <span>Name: <strong className="text-foreground">{item.matched_faculty.faculty_name}</strong></span>
                              </div>
                            )}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </Step>
    </div>
  );
}
