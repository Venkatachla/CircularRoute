import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import { ShieldCheck } from "lucide-react";
import PageHeader from "@/components/PageHeader";
import ApprovalCard from "@/components/ApprovalCard";
import { ErrorState, EmptyState } from "@/components/States";
import { listCirculars, decideCircular } from "@/services/circularService";

export const Route = createFileRoute("/_shell/approvals")({
  head: () => ({
    meta: [
      { title: "Approvals — CircularRoute" },
      { name: "description", content: "Review low-confidence circulars before distribution." },
      { property: "og:title", content: "Approvals — CircularRoute" },
      { property: "og:description", content: "Review low-confidence circulars before distribution." },
    ],
  }),
  loader: async () => (await listCirculars()).filter((c) => c.status === "Pending Approval"),
  component: Approvals,
  errorComponent: ({ error }) => <ErrorState error={error} />,
  notFoundComponent: () => <div>Not found</div>,
});

function Approvals() {
  const initial = Route.useLoaderData();
  const [items, setItems] = useState(initial);
  const [busy, setBusy] = useState(null);
  const navigate = useNavigate();
  const decide = async (c, d) => {
    setBusy(c.id);
    await decideCircular(c.id, d);
    setItems((x) => x.filter((i) => i.id !== c.id));
    setBusy(null);
    d === "approve" ? toast.success(`${c.ref} approved and distributed`) : toast(`${c.ref} returned to draft`);
  };
  return (
    <>
      <PageHeader eyebrow="Human in the loop" title="Approval center" subtitle="Circulars below the 90% confidence threshold." />
      {items.length === 0 ? <EmptyState icon={ShieldCheck} title="No circulars to review" body="Approval records will appear here after backend integration." /> : (
        <div className="grid gap-4 md:grid-cols-2">
          {items.map((c) => (
            <ApprovalCard key={c.id} circular={c} busy={busy === c.id}
              onReview={() => navigate({ to: "/circulars/$id", params: { id: c.id } })}
              onApprove={() => decide(c, "approve")} onReject={() => decide(c, "reject")} />
          ))}
        </div>
      )}
    </>
  );
}
