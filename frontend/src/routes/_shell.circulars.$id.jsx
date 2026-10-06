import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArrowLeft } from "lucide-react";
import PageHeader from "@/components/PageHeader";
import StatusBadge from "@/components/StatusBadge";
import DocumentPreview from "@/components/DocumentPreview";
import ExtractionPanel from "@/components/ExtractionPanel";
import DecisionFlow from "@/components/DecisionFlow";
import RecipientResolution from "@/components/RecipientResolution";
import { ErrorState, EmptyState } from "@/components/States";
import { getCircular } from "@/services/circularService";
import { resolveRecipients } from "@/services/recipientService";

export const Route = createFileRoute("/_shell/circulars/$id")({
  head: ({ loaderData }) => {
    const t = loaderData ? `${loaderData.circular.title} — CircularRoute` : "Circular — CircularRoute";
    return { meta: [{ title: t }, { name: "description", content: "Circular extraction, recipients and decision." }, { property: "og:title", content: t }, { property: "og:description", content: "Circular extraction, recipients and decision." }] };
  },
  loader: async ({ params }) => {
    const circular = await getCircular(params.id).catch(() => { throw notFound(); });
    const resolution = await resolveRecipients({ phrase: circular.recipientPhrase, departments: circular.departments, roles: circular.roles });
    return { circular, resolution };
  },
  component: Detail,
  errorComponent: ({ error }) => <ErrorState error={error} />,
  notFoundComponent: () => <EmptyState title="Circular not found" body="It may have been removed." action={<Link to="/circulars" className="text-sm text-brand">Back to circulars</Link>} />,
});

function Detail() {
  const { circular, resolution } = Route.useLoaderData();
  return (
    <>
      <Link to="/circulars" className="mb-3 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"><ArrowLeft className="size-4" />Circulars</Link>
      <PageHeader eyebrow={circular.ref} title={circular.title} actions={<StatusBadge status={circular.status} />} />
      <div className="mb-6"><DecisionFlow confidence={circular.confidence} /></div>
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="h-[640px]"><DocumentPreview circular={circular} /></div>
        <ExtractionPanel circular={circular} />
      </div>
      <div className="mt-6"><RecipientResolution data={resolution} /></div>
    </>
  );
}
