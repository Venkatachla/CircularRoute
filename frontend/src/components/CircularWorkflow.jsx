import { useState } from "react";
import { AlertCircle, CheckCircle2, FileText, Loader2, Mail, Send, UploadCloud } from "lucide-react";
import { toast } from "sonner";
import UploadDropzone from "@/components/UploadDropzone";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { uploadCircular } from "@/services/circularService";
import { resolveCircularRecipients, sendCircularMail } from "@/services/distributionService";

const STEPS = ["Upload circular", "Extract printed and handwritten names", "Resolve names and find emails"];

export default function CircularWorkflow() {
  const [file, setFile] = useState(null);
  const [documentId, setDocumentId] = useState(null);
  const [matches, setMatches] = useState(null);
  const [recipientNames, setRecipientNames] = useState([]);
  const [subject, setSubject] = useState("");
  const [stage, setStage] = useState("idle");
  const [processing, setProcessing] = useState(false);
  const [resolving, setResolving] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [sent, setSent] = useState(false);

  const selectFile = (nextFile) => {
    setFile(nextFile);
    setDocumentId(null);
    setMatches(null);
    setRecipientNames([]);
    setSubject("");
    setStage("idle");
    setError("");
    setSent(false);
  };

  const processFile = async () => {
    if (!file) return;
    setProcessing(true);
    setError("");
    setMatches(null);
    setRecipientNames([]);
    setDocumentId(null);
    setSent(false);
    try {
      setStage("extracting");
      const extracted = await uploadCircular(file);
      setDocumentId(extracted.document_id);
      setSubject(`Circular: ${file.name.replace(/\.[^.]+$/, "")}`);

      setStage("matching");
      const resolved = await resolveCircularRecipients(extracted.document_id);
      setMatches(resolved);
      setRecipientNames((resolved.matches || []).map((row) => row.recipient_name || row.extracted_text || ""));
      setStage("complete");
    } catch (err) {
      setStage("error");
      setError(err.message || "Could not process this circular.");
    } finally {
      setProcessing(false);
    }
  };

  const lookupEditedNames = async () => {
    if (!documentId) return;
    setResolving(true);
    setError("");
    try {
      const result = await resolveCircularRecipients(documentId, recipientNames);
      setMatches(result);
      setRecipientNames((result.matches || []).map((row) => row.recipient_name || row.extracted_text || ""));
      toast.success(result.status === "resolved" ? "Names resolved and emails found" : "Some names need review or have no email mapping");
    } catch (err) {
      setError(err.message || "Could not look up recipient names.");
    } finally {
      setResolving(false);
    }
  };

  const send = async () => {
    if (!documentId || matches?.status !== "resolved" || !subject.trim()) return;
    setSending(true);
    setError("");
    try {
      const result = await sendCircularMail(documentId, {
        recipient_names: recipientNames,
        subject: subject.trim(),
        attach_document: true,
      });
      if (result.status === "success") {
        setSent(true);
        toast.success(`Circular sent to ${result.sent} mapped recipient(s)`);
      } else {
        const failures = (result.results || [])
          .filter((delivery) => delivery.status !== "sent")
          .map((delivery) => `${delivery.email}: ${delivery.error || delivery.status}`)
          .join("\n");
        setError(failures || `Email sending was incomplete: ${result.sent} of ${result.total} messages sent.`);
      }
    } catch (err) {
      setError(err.message || "Could not send the circular.");
    } finally {
      setSending(false);
    }
  };

  const namesChanged = matches?.matches?.some((row, index) => row.recipient_name !== recipientNames[index]);
  const canSend = matches?.status === "resolved" && !namesChanged && !sending && !processing && !resolving && !sent;

  return (
    <main className="mx-auto w-full max-w-3xl space-y-7">
      <header className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">CircularRoute</p>
        <h1 className="text-3xl font-semibold tracking-tight">Send a circular</h1>
        <p className="text-sm text-muted-foreground">Upload a PDF or image. Printed names and handwritten notes are resolved against the faculty knowledge base before email lookup.</p>
      </header>

      <section className="card-surface space-y-4 p-5 sm:p-6">
        <h2 className="font-semibold">1. Choose a circular</h2>
        <UploadDropzone onFile={selectFile} disabled={processing || sending} />
        {file && <div className="flex items-center gap-2 rounded-md border px-3 py-2 text-sm"><FileText className="size-4 text-brand" /><span className="min-w-0 flex-1 truncate">{file.name}</span><span className="text-xs text-muted-foreground">{Math.max(1, Math.round(file.size / 1024))} KB</span></div>}
        <Button size="lg" onClick={processFile} disabled={!file || processing || sending}>
          {processing ? <><Loader2 className="animate-spin" />{stage === "matching" ? "Resolving names and emails…" : "Extracting printed and handwritten text…"}</> : <><UploadCloud />Upload circular</>}
        </Button>

        {stage !== "idle" && <ol className="grid gap-2 border-t pt-4 sm:grid-cols-3">
          {STEPS.map((label, index) => {
            const done = stage === "complete" || (stage === "matching" && index < 2) || (stage === "extracting" && index === 0);
            const active = (stage === "extracting" && index === 1) || (stage === "matching" && index === 2);
            return <li key={label} className="flex items-center gap-2 text-xs text-muted-foreground">
              {done ? <CheckCircle2 className="size-4 shrink-0 text-success" /> : active ? <Loader2 className="size-4 shrink-0 animate-spin text-brand" /> : <span className="flex size-4 shrink-0 items-center justify-center rounded-full border text-[10px]">{index + 1}</span>}
              <span className={active ? "font-medium text-foreground" : ""}>{label}</span>
            </li>;
          })}
        </ol>}
      </section>

      {matches && <section className="card-surface space-y-4 p-5 sm:p-6">
        <div className="flex items-start justify-between gap-3">
          <div><h2 className="font-semibold">2. Extracted and resolved recipients</h2><p className="mt-1 text-sm text-muted-foreground">The AI sees printed names and handwritten text, compares them with the two closest knowledge base entries, then resolves emails from the backend directory.</p></div>
          {matches.status === "resolved" && !namesChanged && <span className="inline-flex items-center gap-1.5 text-sm font-medium text-success"><CheckCircle2 className="size-4" />Mapped</span>}
        </div>

        {recipientNames.length > 0 ? <div className="space-y-3">
          {recipientNames.map((name, index) => {
            const row = matches.matches?.[index] || {};
            const isFileInstruction = row.status === "skipped" && row.recipient_name?.toLowerCase() === "file";
            const firstInHandwrittenPhrase = row.source_type !== "handwritten" || !matches.matches
              ?.slice(0, index)
              .some((previous) => previous.source_type === "handwritten" && previous.source_page === row.source_page && previous.source_text === row.source_text);
            return <div key={row.source_id || index} className="rounded-md border p-3 space-y-2">
              <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                <span className="rounded bg-muted px-2 py-1 uppercase tracking-wide">{row.source_type || "extracted"}</span>
                <span className="text-muted-foreground">Page {row.source_page || "—"}</span>
              </div>
              {firstInHandwrittenPhrase && <p className="text-sm"><span className="text-muted-foreground">{row.source_type === "handwritten" ? "Handwritten text:" : "Extracted:"}</span> {row.source_text || row.extracted_text || "—"}</p>}
              {row.source_type === "handwritten" && <p className="text-xs text-muted-foreground">Separate item sent for matching: <span className="font-medium text-foreground">{row.extracted_text || "—"}</span></p>}
              {isFileInstruction ? <div role="status" className="rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900">This circular should be added to the file. It will not be added as an email recipient.</div> : <label className="block space-y-1 text-sm font-medium">Resolved name<Input aria-label={`Resolved recipient ${index + 1}`} value={name} onChange={(event) => setRecipientNames((current) => current.map((value, i) => i === index ? event.target.value : value))} placeholder="Canonical faculty name" /></label>}
              {row.candidates?.length > 0 && <div className="text-xs text-muted-foreground">Closest knowledge base entries: {row.candidates.map((candidate) => `${candidate.faculty_name}${candidate.recipient_kind === "group" ? " · student group" : candidate.recipient_kind === "non_recipient" ? " · filing instruction" : ""} (${Math.round(candidate.similarity * 100)}%)`).join(" · ")}</div>}
              {row.emails?.length > 0 && <div className="text-xs font-mono text-success">{row.emails.join(", ")}</div>}
            </div>;
          })}
        </div> : <p className="rounded-md border border-dashed p-4 text-sm text-muted-foreground">No recipient names were extracted from this circular.</p>}

        {recipientNames.length > 0 && <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={lookupEditedNames} disabled={resolving || processing || sending}>
            {resolving ? <><Loader2 className="animate-spin" />Looking up names…</> : "Look up names"}
          </Button>
          {matches.matches?.map((row, index) => row.status === "unmatched" && row.recipient_name === recipientNames[index] ? <span key={`unmatched-${index}`} className="self-center text-xs text-muted-foreground">No email found for: {row.recipient_name || row.extracted_text || "(empty name)"}</span> : null)}
        </div>}

        <label className="block space-y-2 text-sm font-medium">Email subject<Input value={subject} onChange={(event) => setSubject(event.target.value)} placeholder="Enter email subject" maxLength={200} /></label>
        <Button size="lg" onClick={send} disabled={!canSend || !subject.trim()}>
          {sending ? <><Loader2 className="animate-spin" />Sending…</> : sent ? <><CheckCircle2 />Sent</> : <><Send />Send circular with attachment</>}
        </Button>
        {sent && <p className="flex items-center gap-2 text-sm text-success"><Mail className="size-4" />Resend accepted the circular for the mapped recipient emails.</p>}
      </section>}

      {matches?.status !== "resolved" && matches && <div role="status" className="flex items-start gap-2 rounded-md border border-warning/30 bg-warning-soft p-3 text-sm"><AlertCircle className="mt-0.5 size-4 shrink-0" /><span>Some extracted text could not be confidently resolved to a known recipient or email. Review the name, edit it if needed, then look it up again.</span></div>}
      {error && <div role="alert" className="flex items-start gap-2 rounded-md border border-danger/30 bg-danger-soft p-3 text-sm text-danger"><AlertCircle className="mt-0.5 size-4 shrink-0" /><span className="whitespace-pre-line">{error}</span></div>}
    </main>
  );
}
