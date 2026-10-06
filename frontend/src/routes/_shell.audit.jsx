import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import PageHeader from "@/components/PageHeader";
import Drawer from "@/components/Drawer";
import { EmptyState, ErrorState } from "@/components/States";
import { listAuditLogs } from "@/services/auditService";
import { formatDate, formatTime } from "@/utils/format";

export const Route = createFileRoute("/_shell/audit")({
  head: () => ({
    meta: [
      { title: "Audit Logs — CircularRoute" },
      { name: "description", content: "Complete, tamper-evident history of every circular action." },
      { property: "og:title", content: "Audit Logs — CircularRoute" },
      { property: "og:description", content: "Complete, tamper-evident history of every circular action." },
    ],
  }),
  loader: () => listAuditLogs(),
  component: Audit,
  errorComponent: ({ error }) => <ErrorState error={error} />,
  notFoundComponent: () => <div>Not found</div>,
});

function Audit() {
  const logs = Route.useLoaderData();
  const [sel, setSel] = useState(null);
  return (
    <>
      <PageHeader eyebrow="Compliance" title="Audit logs" subtitle="Every action by people and the system." />
      {!logs.length && <EmptyState title="No audit records" body="Audit activity will appear here after backend integration." />}
      {!!logs.length && <div className="card-surface overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b text-left">{["Time", "User", "Action", "Reference", "Status"].map((h) => <th key={h} className="label-caps p-3">{h}</th>)}</tr></thead>
          <tbody>
            {logs.map((l) => (
              <tr key={l.id} onClick={() => setSel(l)} className="cursor-pointer border-b last:border-0 hover:bg-surface">
                <td className="p-3 font-mono text-xs">{formatDate(l.ts)} {formatTime(l.ts)}</td>
                <td className="p-3">{l.user}</td>
                <td className="p-3 font-medium">{l.action}</td>
                <td className="p-3 font-mono text-xs">{l.ref}</td>
                <td className="p-3 text-muted-foreground">{l.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>}
      <Drawer open={!!sel} onClose={() => setSel(null)} title={sel?.action} subtitle={sel?.ref}>
        {sel && (
          <dl className="space-y-3 text-sm">
            {[["Time", `${formatDate(sel.ts)} ${formatTime(sel.ts)}`], ["User", sel.user], ["Source", sel.source], ["Status", sel.status], ["Recipients", sel.recipients ?? "—"], ["Details", sel.details]].map(([k, v]) => (
              <div key={k}><dt className="label-caps">{k}</dt><dd className="mt-0.5">{v}</dd></div>
            ))}
          </dl>
        )}
      </Drawer>
    </>
  );
}
