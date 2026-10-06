import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import PageHeader from "@/components/PageHeader";
import StatusBadge from "@/components/StatusBadge";
import { EmptyState, ErrorState } from "@/components/States";
import { deptName } from "@/utils/format";
import { listDirectory } from "@/services/recipientService";

export const Route = createFileRoute("/_shell/directory")({
  head: () => ({
    meta: [
      { title: "Institutional Directory — CircularRoute" },
      { name: "description", content: "Staff, roles and verified emails used for recipient matching." },
      { property: "og:title", content: "Institutional Directory — CircularRoute" },
      { property: "og:description", content: "Staff, roles and verified emails used for recipient matching." },
    ],
  }),
  loader: () => listDirectory(),
  component: Directory,
  errorComponent: ({ error }) => <ErrorState error={error} />,
  notFoundComponent: () => <div>Not found</div>,
});

function Directory() {
  const people = Route.useLoaderData();
  const [q, setQ] = useState("");
  const rows = people.filter((p) => (p.name + p.role + p.dept + p.email).toLowerCase().includes(q.toLowerCase()));
  return (
    <>
      <PageHeader eyebrow="System" title="Institutional directory" subtitle={`${people.length} people`} />
      <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search name, role, department…" className="mb-4 h-9 w-full max-w-sm rounded-md border bg-card px-3 text-sm" />
      {!rows.length && <EmptyState title="No directory records" body="Directory entries will appear after backend integration." />}
      {!!rows.length && <div className="card-surface overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b text-left">{["Name", "Role", "Department", "Email", "Status"].map((h) => <th key={h} className="label-caps p-3">{h}</th>)}</tr></thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.id} className="border-b last:border-0">
                <td className="p-3 font-medium">{p.name}</td><td className="p-3">{p.role}</td>
                <td className="p-3 text-muted-foreground">{deptName(p.dept)}</td>
                <td className="p-3 font-mono text-xs">{p.email}</td><td className="p-3"><StatusBadge status={p.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>}
    </>
  );
}
