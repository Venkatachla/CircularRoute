import { createFileRoute } from "@tanstack/react-router";
import PageHeader from "@/components/PageHeader";
import StatusBadge from "@/components/StatusBadge";
import { EmptyState, ErrorState } from "@/components/States";
import { deptName } from "@/utils/format";
import { getDistribution } from "@/services/distributionService";

export const Route = createFileRoute("/_shell/distribution")({
  head: () => ({
    meta: [
      { title: "Distribution — CircularRoute" },
      { name: "description", content: "Live email delivery status for distributed circulars." },
      { property: "og:title", content: "Distribution — CircularRoute" },
      { property: "og:description", content: "Live email delivery status for distributed circulars." },
    ],
  }),
  loader: () => getDistribution(),
  component: Distribution,
  errorComponent: ({ error }) => <ErrorState error={error} />,
  notFoundComponent: () => <div>Not found</div>,
});

const DOT = { info: "bg-brand", success: "bg-success", warning: "bg-warning" };

function Distribution() {
  const d = Route.useLoaderData();
  return (
    <>
      <PageHeader eyebrow="Delivery" title="Distribution" subtitle="Email delivery status for circulars." />
      {!d.timeline.length && !d.rows.length ? <EmptyState title="No delivery records" body="Distribution data will appear here after backend integration." /> : <div className="grid gap-6 lg:grid-cols-3">
        <div className="card-surface p-5">
          <div className="label-caps mb-4">Timeline</div>
          <ol className="space-y-4">
            {d.timeline.map((e, i) => (
              <li key={i} className="flex gap-3 text-sm"><span className={`mt-1.5 size-2 shrink-0 rounded-full ${DOT[e.kind]}`} /><span className="font-mono text-xs text-muted-foreground">{e.t}</span><span>{e.text}</span></li>
            ))}
          </ol>
        </div>
        <div className="card-surface overflow-x-auto lg:col-span-2">
          <table className="w-full text-sm">
            <thead><tr className="border-b text-left"><th className="label-caps p-3">Recipient</th><th className="label-caps p-3">Department</th><th className="label-caps p-3">Sent</th><th className="label-caps p-3">State</th></tr></thead>
            <tbody>
              {d.rows.map((r) => (
                <tr key={r.id} className="border-b last:border-0">
                  <td className="p-3"><div className="font-medium">{r.name}</div><div className="font-mono text-xs text-muted-foreground">{r.email}</div></td>
                  <td className="p-3 text-muted-foreground">{deptName(r.dept)}</td>
                  <td className="p-3 font-mono text-xs">{r.sentAt}</td>
                  <td className="p-3"><StatusBadge status={r.state} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>}
    </>
  );
}
