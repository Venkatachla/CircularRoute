import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import PageHeader from "@/components/PageHeader";
import CircularTable from "@/components/CircularTable";
import { ErrorState, EmptyState } from "@/components/States";
import { listCirculars } from "@/services/circularService";

export const Route = createFileRoute("/_shell/circulars/")({
  head: () => ({
    meta: [
      { title: "Circulars — CircularRoute" },
      { name: "description", content: "Browse every circular processed by CircularRoute." },
      { property: "og:title", content: "Circulars — CircularRoute" },
      { property: "og:description", content: "Browse every circular processed by CircularRoute." },
    ],
  }),
  loader: () => listCirculars(),
  component: Circulars,
  errorComponent: ({ error }) => <ErrorState error={error} />,
  notFoundComponent: () => <div>Not found</div>,
});

const FILTERS = ["All", "Distributed", "Processing", "Pending Approval", "Draft"];

function Circulars() {
  const all = Route.useLoaderData();
  const [f, setF] = useState("All");
  const [q, setQ] = useState("");
  const rows = all.filter((c) => (f === "All" || c.status === f) && (c.title + c.ref).toLowerCase().includes(q.toLowerCase()));
  return (
    <>
      <PageHeader eyebrow="Library" title="Circulars" subtitle={`${all.length} circulars on record`} />
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search title or reference…" className="h-9 w-full max-w-sm rounded-md border bg-card px-3 text-sm" />
        <div className="flex flex-wrap gap-1">
          {FILTERS.map((x) => (
            <button key={x} onClick={() => setF(x)} className={`h-8 rounded-md px-3 text-xs font-medium ${f === x ? "bg-primary text-primary-foreground" : "border bg-card text-muted-foreground hover:text-foreground"}`}>{x}</button>
          ))}
        </div>
      </div>
      {rows.length ? <CircularTable circulars={rows} /> : <EmptyState title="No circulars match" body="Try a different filter or search term." />}
    </>
  );
}
