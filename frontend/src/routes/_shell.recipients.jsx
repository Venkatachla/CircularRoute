import { createFileRoute } from "@tanstack/react-router";
import PageHeader from "@/components/PageHeader";
import { EmptyState } from "@/components/States";

export const Route = createFileRoute("/_shell/recipients")({
  head: () => ({
    meta: [
      { title: "Recipients — CircularRoute" },
      { name: "description", content: "Resolve recipient phrases against the institutional directory." },
      { property: "og:title", content: "Recipients — CircularRoute" },
      { property: "og:description", content: "Resolve recipient phrases against the institutional directory." },
    ],
  }),
  component: Recipients,
});

function Recipients() {
  return (
    <>
      <PageHeader eyebrow="Resolver" title="Recipients" subtitle="Preview recipient matching from the institutional directory." />
      <EmptyState title="Recipient data is not connected" body="Department and role options will appear after backend integration." />
    </>
  );
}
