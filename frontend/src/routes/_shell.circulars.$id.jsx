import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { useState } from "react";
import { ArrowLeft, Mail, Users } from "lucide-react";
import { toast } from "sonner";
import PageHeader from "@/components/PageHeader";
import StatusBadge from "@/components/StatusBadge";
import DocumentPreview from "@/components/DocumentPreview";
import ExtractionPanel from "@/components/ExtractionPanel";
import DecisionFlow from "@/components/DecisionFlow";
import RecipientResolution from "@/components/RecipientResolution";
import { ErrorState, EmptyState } from "@/components/States";
import { getCircular } from "@/services/circularService";
import { resolveCircularRecipients, sendCircularMail } from "@/services/distributionService";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/_shell/circulars/$id")({
  head: ({ loaderData }) => {
    const t = loaderData?.circular ? `${loaderData.circular.title} — CircularRoute` : "Circular — CircularRoute";
    return {
      meta: [
        { title: t },
        { name: "description", content: "Circular extraction and Copy-To recipient details." },
        { property: "og:title", content: t },
        { property: "og:description", content: "Circular extraction and Copy-To recipient details." },
      ],
    };
  },
  loader: async ({ params }) => {
    const circular = await getCircular(params.id).catch(() => {
      throw notFound();
    });
    return { circular };
  },
  component: Detail,
  errorComponent: ({ error }) => <ErrorState error={error} />,
  notFoundComponent: () => (
    <EmptyState
      title="Circular not found"
      body="It may have been removed."
      action={<Link to="/circulars" className="text-sm text-brand">Back to circulars</Link>}
    />
  ),
});

function Detail() {
  const { circular } = Route.useLoaderData();
  const [currentCircular, setCurrentCircular] = useState(circular);
  const [sending, setSending] = useState(false);
  const [resolving, setResolving] = useState(false);
  const [resolution, setResolution] = useState(null);

  const resolve = async () => {
    setResolving(true);
    try {
      const result = await resolveCircularRecipients(currentCircular.id);
      setResolution(result);
      if (result.status === "resolved") toast.success(`${result.recipients.length} recipient email(s) resolved`);
      else toast.error(result.unresolved?.length ? `${result.unresolved.length} recipient(s) need correction` : "No email recipients could be resolved");
    } catch (error) {
      toast.error(error.message || "Unable to resolve recipient emails");
    } finally {
      setResolving(false);
    }
  };

  const send = async () => {
    if (resolution?.status !== "resolved") {
      toast.error("Resolve and review recipient emails before sending");
      return;
    }
    setSending(true);
    try {
      const result = await sendCircularMail(currentCircular.id);
      if (result.status === "success") toast.success(`Circular sent to ${result.sent} recipient(s)`);
      else toast.error(`Delivery incomplete: ${result.sent}/${result.total} sent. Check Distribution for details.`);
    } catch (error) {
      toast.error(error.message || "Unable to send circular");
    } finally {
      setSending(false);
    }
  };

  return (
    <>
      <Link to="/circulars" className="mb-3 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="size-4" />Circulars
      </Link>
      <PageHeader
        eyebrow={currentCircular.ref}
        title={currentCircular.title}
        actions={<div className="flex items-center gap-2"><StatusBadge status={currentCircular.status} /><Button variant="outline" onClick={resolve} disabled={resolving || sending}><Users className="size-4" />{resolving ? "Resolving…" : resolution ? "Refresh recipients" : "Resolve recipients"}</Button><Button onClick={send} disabled={sending || resolving || resolution?.status !== "resolved"} title={resolution?.status !== "resolved" ? "Resolve and review recipient emails first" : "Send circular by email"}><Mail className="size-4" />{sending ? "Sending…" : "Send circular"}</Button></div>}
      />
      {resolution && <section className="mb-6 rounded-lg border bg-card p-4" aria-live="polite">
        <div className="mb-3 flex items-center justify-between gap-3">
          <h2 className="font-semibold">Resolved email recipients ({resolution.recipients.length})</h2>
          {resolution.status === "resolved" && <span className="text-sm text-success">Ready to send</span>}
        </div>
        {resolution.recipients.length > 0 && <ul className="grid gap-2 sm:grid-cols-2">
          {resolution.recipients.map((recipient) => <li key={recipient.email} className="rounded-md border px-3 py-2 text-sm"><span className="font-medium">{recipient.name}</span><span className="ml-2 font-mono text-xs text-muted-foreground">{recipient.email}</span></li>)}
        </ul>}
        {resolution.unresolved?.length > 0 && <div className="mt-3 rounded-md border border-warning/40 bg-warning-soft p-3 text-sm"><p className="font-medium">These extracted recipients need correction before sending:</p><ul className="mt-1 list-disc pl-5">{resolution.unresolved.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}</ul></div>}
        {resolution.status !== "resolved" && resolution.unresolved?.length === 0 && <p className="text-sm text-muted-foreground">No recipient email addresses were found in the directory.</p>}
      </section>}
      <div className="mb-6"><DecisionFlow confidence={currentCircular.confidence} /></div>
      <div className="mb-6"><DocumentPreview circular={currentCircular} /></div>
      <ExtractionPanel circular={currentCircular} />
      <div className="mt-6">
        <RecipientResolution
          circular={currentCircular}
          onUpdate={(updated) => { setCurrentCircular(updated); setResolution(null); }}
        />
      </div>
    </>
  );
}
