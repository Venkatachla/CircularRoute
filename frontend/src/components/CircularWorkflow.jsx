import { useState } from "react";
import { AlertCircle, CheckCircle2, FileText, Loader2, Mail, Send, UploadCloud } from "lucide-react";
import { toast } from "sonner";
import UploadDropzone from "@/components/UploadDropzone";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { uploadCircular } from "@/services/circularService";
import { resolveCircularRecipients, sendCircularMail } from "@/services/distributionService";

const STEPS = ["Upload circular", "Extract recipient names", "Look up names in recipient JSON"];

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
      setRecipientNames((resolved.matches || []).map((row) => row.recipient_name));
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
      toast.success(result.status === "resolved" ? "All recipient names matched" : "Some names do not have an email mapping yet");
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
        <p className="text-sm text-muted-foreground">Upload a PDF or image, review the extracted recipient names, then send the circular.</p>
      </header>

      <section className="card-surface space-y-4 p-5 sm:p-6">
        <h2 className="font-semibold">1. Choose a circular</h2>
        <UploadDropzone onFile={selectFile} disabled={processing || sending} />
        {file && <div className="flex items-center gap-2 rounded-md border px-3 py-2 text-sm"><FileText className="size-4 text-brand" /><span className="min-w-0 flex-1 truncate">{file.name}</span><span className="text-xs text-muted-foreground">{Math.max(1, Math.round(file.size / 1024))} KB</span></div>}
        <Button size="lg" onClick={processFile} disabled={!file || processing || sending}>
          {processing ? <><Loader2 className="animate-spin" />{stage === "matching" ? "Looking up names…" : "Extracting recipient names…"}</> : <><UploadCloud />Upload circular</>}
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
          <div><h2 className="font-semibold">2. Extracted recipient names</h2><p className="mt-1 text-sm text-muted-foreground">Edit a name if needed, then look it up in the backend JSON map.</p></div>
          {matches.status === "resolved" && !namesChanged && <span className="inline-flex items-center gap-1.5 text-sm font-medium text-success"><CheckCircle2 className="size-4" />Mapped</span>}
        </div>

        {recipientNames.length > 0 ? <div className="space-y-2">
          {recipientNames.map((name, index) => <Input key={index} aria-label={`Recipient name ${index + 1}`} value={name} onChange={(event) => setRecipientNames((current) => current.map((value, i) => i === index ? event.target.value : value))} placeholder="Recipient name" />)}
        </div> : <p className="rounded-md border border-dashed p-4 text-sm text-muted-foreground">No recipient names were extracted from this circular.</p>}

        {recipientNames.length > 0 && <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={lookupEditedNames} disabled={resolving || processing || sending}>
            {resolving ? <><Loader2 className="animate-spin" />Looking up names…</> : "Look up names"}
          </Button>
          {matches.matches?.map((row, index) => row.status === "unmatched" && row.recipient_name === recipientNames[index] ? <span key={`unmatched-${index}`} className="self-center text-xs text-muted-foreground">No JSON mapping for: {row.recipient_name || "(empty name)"}</span> : null)}
        </div>}

        <label className="block space-y-2 text-sm font-medium">Email subject<Input value={subject} onChange={(event) => setSubject(event.target.value)} placeholder="Enter email subject" maxLength={200} /></label>
        <Button size="lg" onClick={send} disabled={!canSend || !subject.trim()}>
          {sending ? <><Loader2 className="animate-spin" />Sending…</> : sent ? <><CheckCircle2 />Sent</> : <><Send />Send circular with attachment</>}
        </Button>
        {sent && <p className="flex items-center gap-2 text-sm text-success"><Mail className="size-4" />Resend accepted the circular for the mapped recipient emails.</p>}
      </section>}

      {matches?.status !== "resolved" && matches && <div role="status" className="flex items-start gap-2 rounded-md border border-warning/30 bg-warning-soft p-3 text-sm"><AlertCircle className="mt-0.5 size-4 shrink-0" /><span>Some names do not yet have an email mapping. Add name and email pairs to <code>backend/recipient_email_map.json</code>, then look up the names again.</span></div>}
      {error && <div role="alert" className="flex items-start gap-2 rounded-md border border-danger/30 bg-danger-soft p-3 text-sm text-danger"><AlertCircle className="mt-0.5 size-4 shrink-0" /><span className="whitespace-pre-line">{error}</span></div>}
    </main>
  );
}
